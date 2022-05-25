"""
	This module processes the rendering of templates.
"""
import initialize
import os
import re
from jinja2 import Environment, FileSystemLoader
from get_property import get_home_directory
from get_property import get_policy_directory
from get_property import get_template_directory
from get_property import get_standards_directory
from get_property import get_updated_list
from parse_cmd import parse_commands
from parse_cmd import parse_firewall_acl

def render(template_list,node_object,auditcreeper,output,with_remediation):
	"""
		Uncomment the below function and replace with the above define function to include secrets if hashicorp is used.
	"""
#def render(template_list,node_object,auditcreeper,output,with_remediation,secrets):
	global with_remediate
	with_remediate = with_remediation
	template_list_copy = template_list
	if auditcreeper:
	    template_list = template_list_copy[0]
	for index in initialize.element:
		get_hardware_vendor_template_directory = get_template_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
		print ("{}".format(node_object[index]['name']))
		for template in template_list:
			config = process_jinja2_template(node_object,index,template,with_remediation)
			print("{}{}".format(get_hardware_vendor_template_directory,template))
			if(output):
				print("{}".format(config))
			with open('{}/rendered-configs/{}.{}'.format(get_home_directory(),node_object[index]['name'],template.replace('jinja2','')) + 'conf','r') as file:
				init_config = file.readlines()
			"""
				The below parse_commands() function will only get executed if
				it needs to store commands in the global variable initialize.configuration
				for push. push_cfgs(output = True) vs render_config(output = False) functions.
			"""
			if output!=True:
				parse_commands(node_object[index],init_config,set_notation=False)
			print()
		if auditcreeper:
			template_list = get_updated_list(template_list_copy)

	return None

def process_jinja2_template(node_object,index,template,with_remediation):
	hardware_vendor_template_directory = get_template_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
	standards_directory = get_standards_directory(node_object[index]['name'],node_object[index]['hardware_vendor'],node_object[index]['type'])
	env = Environment(loader=FileSystemLoader([hardware_vendor_template_directory,standards_directory]),lstrip_blocks = True,trim_blocks=True)
	baseline = env.get_template(template)
	os.makedirs('{}/rendered-configs/'.format(get_home_directory()),exist_ok=True)
	with open('{}/rendered-configs/{}.{}'.format(get_home_directory(),node_object[index]['name'],template.replace('jinja2','')) + 'conf', 'w') as file:
		config = baseline.render(node = node_object[index],with_remediation = with_remediation)
		file.write(config) 
		file.close 

	return config

def remediate(input):
	"""
		Custom filter to process boolean.
	"""
	if with_remediate == True:
		return input
	else:
		return ''

def acl_render(policy_list,node_object,node_policy,policy_list_copy,auditcreeper):

	commands = [] 
	redirect = []
	policy_list_copy = policy_list
	if auditcreeper:
		policy_list = policy_list_copy[0]
		all_policies = policy_list_copy[0]
	"""
		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list

		:param commands: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list
	"""
	for index in initialize.element:
		get_hardware_vendor_policy_directory = get_policy_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
		print ("{}".format(node_object[index]['name']))
		redirect.append('push_acl')
		""" 
			The below iteration takes care of the configs for each policy file per firewall node(s).
		"""
		if auditcreeper:
			for policy in all_policies:
				print('{}{}'.format(get_hardware_vendor_policy_directory,policy))
			print('')
			for policy in policy_list:
				commands = parse_firewall_acl(node_object[index],policy)
				policy_list = get_updated_list(policy_list_copy)
			for configs in commands:
				print(configs)
			initialize.configuration.append(commands)
		else:
			for policy in policy_list:
				print('{}{}'.format(get_hardware_vendor_policy_directory,policy))
				commands = parse_firewall_acl(node_policy[index],policy)
			for configs in commands:
				print(configs)

	return commands
