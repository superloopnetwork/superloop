"""
	This mediator is a generic audit diff for various hardware vendors including Cisco, Citrix and F5.
"""
import re
import initialize
import os
from ciscoconfparse import CiscoConfParse
from get_property import get_template_directory
from get_property import get_syntax
from get_property import get_sorted_juniper_template_list 

home_directory = os.environ.get('HOME')

def generic_audit_diff(node_object,index,template,template_list,AUDIT_FILTER_RE,output,with_remediation):

	for template in template_list:
		
		filtered_backup_config = []
		rendered_config = []
		backup_config = []
		commands = []
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
		with open("{}/backup-configs/{}".format(home_directory,node_object[index]['name']) + ".conf", "r") as file:
			init_config = file.readlines()
		for config_line in init_config:
			strip_config = config_line.strip('\n')
			strip_config = strip_config.rstrip()
			if strip_config == '' or strip_config == ' ' or strip_config == '!' or strip_config == '! ':
				continue	
			else:
				backup_config.append(strip_config)	
		directory = get_template_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
		with open("{}".format(directory) + template, "r") as file:
			parse_audit = file.readline()
		"""
			This will take each element from the audit_filter list and search for the matched lines in backup_config.
		"""
		audit_filter = eval(re.findall(AUDIT_FILTER_RE, parse_audit)[0])
#		parse_backup_configs = CiscoConfParse("{}/backup-configs/{}".format(home_directory,node_object[index]['name']) + ".conf", syntax=get_syntax(node_object,index))
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
		"""
			sync_diff() will diff out the filtered_backup_config from the rendered_configs and store whatever commands that has deltas.
		"""
		parse = CiscoConfParse(filtered_backup_config)
		push_configs = parse.sync_diff(
				rendered_config,
				"",
				ignore_order=True, 
				remove_lines=True, 
				debug=False
		)
		"""
			Calculating the percentage of config lines from the template that matches the running-configuration of the device. This will 
			provide an accurate reading config standardization. 
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
			is executed, not configs would be pushed as an empty list is appended.
		"""
		if len(push_configs) == 0:
			if output:
				print("{}{} (none)".format(directory,template))
				print('')
			else:
				initialize.configuration.append([])
				print('There are no diffs to be pushed for template {} on {}'.format(template,node_object[index]['name']))
				if len(initialize.element) == 0:
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
				for line in push_configs:
					search = parse_backup_configs.find_objects(r"^{}".format(re.escape(line)),exactmatch=True)
					if re.search(r'^no',line) or re.search(r'\sno',line):
						line = re.sub("no","",line)
						print("-{}".format(line))
						total_push_config_lines = total_push_config_lines - 1
					elif len(search) == 0:
						print("+ {}".format(line))
						total_push_config_lines = total_push_config_lines - 1
					elif len(search) > 1:
						print("+ {}".format(line))
						total_push_config_lines = total_push_config_lines - 1
					else:
						print("  {}".format(line))
						total_push_config_lines = total_push_config_lines - 1
				matched_lines = total_filtered_backup_config_lines - total_push_config_lines
				matched_percentage = round(matched_lines/total_filtered_backup_config_lines*100,2)
				print('')
				print('+ config standardization: {}%'.format(matched_percentage))
			else:
				if node_object[index]['hardware_vendor'] == 'cisco':
					for line in push_configs:
						commands.append(line)
					initialize.configuration.append(commands)
				elif node_object[index]['hardware_vendor'] == 'citrix':
					commands = parse_negation_commands(push_configs)
					initialize.configuration.append(commands)
					"""
						For debug purpose, you may enable the below print statement.
					"""
					print(initialize.configuration)

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
