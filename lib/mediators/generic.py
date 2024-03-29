"""
	This mediator is a generic audit diff for various hardware vendors including Cisco, Citrix and F5.
"""
import diffios
import re
import initialize
import itertools
import os
from ciscoconfparse import CiscoConfParse
from ciscoconfparse import HDiff
from get_property import get_no_negate
from get_property import get_policy_directory
from get_property import get_template_directory
from get_property import get_syntax
from get_property import get_sorted_juniper_template_list 
from parse_cmd import citrix_parse_negation_commands
from parse_cmd import cisco_parse_negation_commands

home_directory = os.environ.get('HOME')

def generic_audit_diff(args,node_configs,node_object,index,template,input_list,AUDIT_FILTER_RE,output,with_remediation):
	length_rendered_config = 0
	length_backup_config = 0
	delta_diff_counter = 0
	delta_length_rendered_config = 0
	for template in input_list:
		filtered_backup_config = []
		rendered_config = []
		backup_config = []
		"""
		:param filtered_backup_config: Audit filters that matches the lines in backup_config. Entries include depths/deep configs.
		:type filtered_backup_config: list

		:param rendered_config: Rendered configs from the templates.
		:type rendered_config: list

		:param backup_config: Backup configs from the 'show run', 'list ltm' etc...
		:type backup_config: list

		:param commands: ... Configurations generated from the diff'ed output.
		:type commands: list
		"""
		with open("{}/rendered-configs/{}.{}".format(home_directory,node_object[index]['name'],template.split('.')[0]) + ".conf", "r") as file:
			init_config = file.readlines()
		for config_line in init_config:
			strip_config = config_line.strip('\n')
			strip_config = strip_config.rstrip()
			if strip_config == '' or strip_config == ' ' or strip_config == '!':
				continue	
			else:
				rendered_config.append(strip_config)	
		length_rendered_config = len(rendered_config)
		with open("{}/backup-configs/{}".format(home_directory,node_object[index]['name']) + ".conf", "r") as file:
			init_config = file.readlines()
		for config_line in init_config:
			strip_config = config_line.strip('\n')
			strip_config = strip_config.rstrip()
			if strip_config == '' or strip_config == ' ' or strip_config == '!' or strip_config == '! ':
				continue	
			else:
				backup_config.append(strip_config)	
		length_backup_config = len(backup_config)
		if args.policy is not None:
			directory = get_policy_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
			with open("{}".format(directory) + template, "r") as file:
				parse_audit = file.readline()
		else:
			directory = get_template_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
			with open("{}".format(directory) + template, "r") as file:
				parse_audit = file.readline()
		"""
			This will take each element from the audit_filter list and search for the matched lines in backup_config.
		"""
		audit_filter = eval(re.findall(AUDIT_FILTER_RE, parse_audit)[0])
		parse_backup_configs = CiscoConfParse(backup_config, syntax=get_syntax(node_object,index))
		"""
			Matched entries are then appended to the filter_backup_config variable. parse_audit_filter() call will find all parent/child.
		"""
		filtered_backup_config = parse_audit_filter(
				node_object,
				index,
				parse_backup_configs,
				audit_filter
		)
		diff = diffios.Compare(filtered_backup_config,rendered_config)
		push_configs = diff.missing() + diff.additional()
		push_configs = list(itertools.chain.from_iterable(push_configs))
		addition = list(itertools.chain.from_iterable(diff.additional()))
		"""
			Calculating the percentage of config lines from the template that matches the running-configuration of the device.
			This willprovide an accurate reading config standardization.
		"""
		total_template_lines = len(rendered_config)
		total_filtered_backup_config_lines = len(filtered_backup_config)
		total_backup_config_lines = len(backup_config)
		total_push_config_lines = len(push_configs)
		"""
		:param total_template_lines: Total number of lines in the template.
		:type total_template_lines: int

		:param total_filtered_backup_config_lines: Total number of lines in the filtered backup config.
		:type total_filtered_backup_config_lines: int

		:param total_backup_config_lines: Total number of lines in the backup config.
		:type total_backup_config_lines: int
		"""

		"""
			If there are no diffs and only and audit diff is executed, (none) will be printed to show users the result. However, if there are no diffs but a push cfgs
			is executed, no configs would be pushed as an empty list is appended.
		"""
		if len(push_configs) == 0 and output:
			if output:
				print('{}{} (none)'.format(directory,template))
				print('')
				template_percentage = round(length_rendered_config / length_backup_config * 100,2)
				initialize.compliance_percentage = round(initialize.compliance_percentage + template_percentage,2)
			else:
				initialize.configuration.append([])
				print('There are no diffs to be pushed for template {} on {}'.format(template,node_object[index]['name']))
				if len(initialize.element) == 0:
					node_configs.append('')
					break
		else:
			"""
				If an audit diff is executed, the diff is outputed to user. If a push cfgs is executed against Cisco like platforms, the commands from the diff are executed
				with the negation (no). This is to maintain the sequence of the the commands in order to match the jinja2 templates. What you see on the template is what the
				users want exactly as the running-configurations. The with_remediation flag is no longer required on the template itself as it may cause disruptions to
				services. For example, blowing out an entire logging configs (no logging) and re-adding all the logging host back on.
			"""
			if output:
				print("{}{}".format(directory,template))
				print('\n'.join(HDiff(filtered_backup_config,rendered_config,syntax="ios",ordered_diff=True).unified_diffs()[3:]))
				delta_length_rendered_config = length_rendered_config - delta_diff_counter
				template_percentage = round(delta_length_rendered_config / length_backup_config * 100,2)
				initialize.compliance_percentage = round(initialize.compliance_percentage + template_percentage,2)
			else:
				if node_object[index]['hardware_vendor'] == 'cisco' and len(push_configs) != 0:
					negate_configs = cisco_parse_negation_commands(diff.missing())
					for config in negate_configs:
						node_configs.append(config)
					for config in addition:
						node_configs.append(config)
				elif node_object[index]['hardware_vendor'] == 'citrix':
					negate_configs = citrix_parse_negation_commands(diff.missing())
					for config in negate_configs:
						node_configs.append(config)
					for config in addition:
						node_configs.append(config)
	return None

def parse_audit_filter(node_object,index,parse_backup_configs,audit_filter):
	filtered_backup_config = []
	for audit in audit_filter:
		current_template = parse_backup_configs.find_objects(r"^{}".format(audit))
		for audit_string in current_template:
			filtered_backup_config.append(audit_string.text)
			if audit_string.is_parent:
				for child in audit_string.all_children:
					filtered_backup_config.append(child.text)

	return filtered_backup_config
