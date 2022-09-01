"""
This module allows auditing to occur for different hardware vendors.
"""
from jinja2 import Environment, FileSystemLoader
from ciscoconfparse import CiscoConfParse
from render import process_jinja2_template 
from render import process_json_template 
from multithread import multithread_engine
from lib.mediators.generic import generic_audit_diff
from lib.mediators.juniper import juniper_mediator
from lib.mediators.juniper import juniper_audit_diff
from get_property import get_home_directory
from get_property import get_template_directory
from get_property import get_updated_list
from get_property import get_syntax
from get_property import get_secrets
from get_property import get_sorted_juniper_template_list 
import re
import initialize
import os

def mediator(args,input_list,node_object,auditcreeper,output,with_remediation):
	AUDIT_FILTER_RE = r'\[.*\]'
	authentication = True
	command = [] 
	initialize.debug_element = initialize.element[:]
	template_counter = 0
	node_index = 0 
	policy_list_original = input_list[:]
	policy_list_copy = input_list
	redirect = []
	template_list_original = input_list[:]
	template_list_copy = input_list

	"""
	:param AUDIT_FILTER_RE: Regular expression to filter out the audit filter in every template.
	:type AUDIT_FILTER_RE: str

	:param command: A list within a list where each element represents per node of commands to execute.
	:type command: list

	:param initialize.debug_element: Duplicate of initialize.element as elments need to be popped off when there are no diffs to help display what will be changing in configs.
	:type initialize.debug_element: list
	
	:param template_counter: Used to keep track of the number of templates it cycles through for Juniper.
	:type template_counter: int
	
	:param node_index: Keeps track of the index in initialize.ntw_device. If remediation is not required (configs matches template), then the node is popped off initialize.ntw_device and nothing is changed on that device.
	:type node_index: int
	
	:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
	:type redirect: list

	:param template_list_original: Take a duplicate copy of template_list
	:type template_list_original: list
	
	:param template_list_copy: Memory reference to template_list
	:type template_list_copy: list
	
	"""
	"""
	The mediator is broken up into two sections. The first section of code will gather all rendered configs first as it's required for all hardware vendors 
	(Cisco, Juniper & F5). Juniper does not require backup-configs in order to be diff'ed. The diff is server (node) side processed and the results 
	are returned back to superloop. Cisco hardware_vendors will require backup-configs (get_config) where the diffs are processed locally.
	"""
	if auditcreeper:
		input_list = template_list_copy[0]
	for index in initialize.element:
		rendered_config = []
		if node_object[index]['hardware_vendor'] == 'juniper':
			"""
                Juniper's diff output are always in a certain stanza order. 
                The input_list ordered processed may very well not be in the 
                same order as Juniper's. In order to keep it consistent, we must 
                call the function get_sorted_juniper_template() and it will 
                return a sorted Juniper's stanza list.
			"""
			input_list = get_sorted_juniper_template_list(input_list)
			rendered_config.append('load replace terminal')
		for template in input_list:
			print('[>] {} ; {}'.format(node_object[index]['name'],template))
			"""
				Uncomment the secrets below if you are using hashicorp vault. You will need to setup the credentials.
			"""
#			secrets = get_secrets()
			if args.policy is not None:
				output = False
				process_json_template(input_list,node_object,policy_list_copy,output,auditcreeper)
				output = True 
			else:
				process_jinja2_template(node_object,index,template,with_remediation)
			"""
				Compiling the rendered configs from template and preparing
				for pushing to node.
			"""
			if node_object[index]['hardware_vendor'] == 'juniper':
				template_counter = template_counter + 1
				with open('{}/rendered-configs/{}.{}'.format(get_home_directory(),node_object[index]['name'],template.split('.')[0]) + '.conf','r') as file:
					init_config = file.readlines()
				for config_line in init_config:
					strip_config = config_line.strip('\n')
					if(strip_config == '' or strip_config == "!"):
						continue	
					else:
						rendered_config.append(strip_config)	
				"""
					This below statement will check to see if it's the last 
					template for the node. It will then append 3 commands to the list.
				"""
				if template_counter == len(input_list):
					rendered_config.append('\x04')
					if output:
						rendered_config.append('show | compare')
						rendered_config.append('rollback 0')
				"""
					Uncomment the below print statement for debugging purposes
				"""
					#print("RENDERED CONFIG: {}".format(rendered_config))
		"""
			The below statement will only execute if user is auditing 
			against multiple templates. If only one template is being 
			audited, do no pop off element.
		"""
#		if len(input_list) != 1:
#		print('template_list_copy > {}'.format(template_list_copy))
#		print('input_list > {}'.format(input_list))
		input_list = get_updated_list(template_list_copy)
		if node_object[index]['hardware_vendor'] == 'cisco' or node_object[index]['hardware_vendor'] == 'f5' or node_object[index]['hardware_vendor'] == 'palo_alto':
			redirect.append('get_config')
			command.append([''])
			"""
			Juniper devices will receive a different redirect than 
			Cisco. Three additional commands are appeneded 
			at the end, ^d, show | compare and rollback 0.  All templates 
			matching are executed at once per device
		"""
		elif node_object[index]['hardware_vendor'] == 'juniper':
			redirect.append('get_diff')
			command.append(rendered_config)
			template_counter = 0
	"""
		Uncomment the below print statement for debugging purposes
	"""
	#print('REDIRECT: {}'.format(redirect))
	#print('TEMPLATE_LIST: {}'.format(input_list))
	#print('COMMAND: {}'.format(command))
	multithread_engine(initialize.ntw_device,redirect,command,authentication)
	input_list = template_list_original
	if(auditcreeper):
		input_list = template_list_original[0]
	for index in initialize.element:
		initialize.compliance_percentage = 0
		diff_config = []
		edit_list = []
		length_backup_config = 0
		length_rendered_config = 0
		node_configs = []
		diff_config = []
		ntw_device_pop = True 
		"""
			:param edit_list: Anchor points for Juniper audits based on the edit stanza.
			:type edit_list: list

			:param node_configs: Finalized configs used to push to device
			:type node_configs: list

			:param diff_config: Differential configs generated by the ~/diff-configs/*.conf file
			:type diff_config: list

			:param ntw_device_pop: Pop off each node once audit is complete.
			:type ntw_device_pop: bool
		"""
		if not with_remediation:
			print("Only in the device: -")
			print("Only in the generated config: +")
			print ("{}".format(node_object[index]['name']))
		if node_object[index]['hardware_vendor'] == 'cisco' or node_object[index]['hardware_vendor'] == 'f5' or node_object[index]['hardware_vendor'] == 'palo_alto':
			generic_audit_diff(args,node_configs,node_object,index,template,input_list,AUDIT_FILTER_RE,output,with_remediation)
#			print('node_configs > {}'.format(node_configs))
			initialize.configuration.append(node_configs)
		elif node_object[index]['hardware_vendor'] == 'juniper':
			input_list = get_sorted_juniper_template_list(input_list)
			directory = get_template_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
			with open('{}/diff-configs/{}'.format(get_home_directory(),node_object[index]['name']) + '.conf','r') as file:
				init_config = file.readlines()
			for config_line in init_config:
				strip_config = config_line.strip('\n')
				diff_config.append(strip_config)
			for output in diff_config:
				if 'errors' in output:
					error = True
					break
				else:
					error = False
			if error:
				print('+ Please check error(s) in template(s)')
				break
			else:
				juniper_mediator(node_object,input_list,diff_config,edit_list,index)
				juniper_audit_diff(directory,input_list,diff_config,edit_list)
			initialize.configuration.append(rendered_config)
#		print('initialize.configuration > {}'.format(initialize.configuration))
		if auditcreeper:
			if node_object[index]['hardware_vendor'] == 'cisco' and len(node_configs) == 0:
				if output:
					print('[>] {} code compliance: {}%'.format(node_object[index]['name'],initialize.compliance_percentage))
					print('')
				initialize.ntw_device.pop(len(initialize.configuration) - 1)
				initialize.configuration.pop(len(initialize.configuration) - 1)
			input_list = get_updated_list(template_list_original)

	return None
