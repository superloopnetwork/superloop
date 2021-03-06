"""
	This module processes the rendering of templates.
"""
import initialize
import os
import re
from jinja2 import Environment, FileSystemLoader
from get_property import get_home_directory
from get_property import get_template_directory
from get_property import get_location_directory
from get_property import get_updated_list
from parse_cmd import parse_commands

def render(template_list,node_object,auditcreeper,output,with_remediation):
	global with_remediate
	with_remediate = with_remediation
	template_list_copy = template_list
	if auditcreeper:
	    template_list = template_list_copy[0]
	for index in initialize.element:
		get_hardware_vendorg_template_directory = get_template_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
		print ("{}".format(node_object[index]['name']))
		for template in template_list:
			config = process_jinja2_template(node_object,index,template,with_remediation)
			print("{}{}".format(get_hardware_vendorg_template_directory,template))
			if(output):
				print("{}".format(config))
			f = open("{}/rendered-configs/{}.{}".format(get_home_directory(),node_object[index]['name'],template.replace('jinja2','')) + "conf", "r")
			init_config = f.readlines()
			"""
				The below parse_commands() function will only get executed if
				it needs to store commands in the global variable initialize.configuration
				for push. push_cfgs(output = True) vs render_config(output = False) functions.
			"""
			if output!=True:
				parse_commands(node_object[index],init_config)
			print()
		if auditcreeper:
			template_list = get_updated_list(template_list_copy)

	return None

def process_jinja2_template(node_object,index,template,with_remediation):
	get_hardware_vendorg_template_directory = get_template_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
	get_location_template_directory = get_location_directory(node_object[index]['name'],node_object[index]['hardware_vendor'],node_object[index]['type'])
	env = Environment(loader=FileSystemLoader([get_hardware_vendorg_template_directory,get_location_template_directory]),lstrip_blocks = True,trim_blocks=True)
	baseline = env.get_template(template)
	os.makedirs('{}/rendered-configs/'.format(get_home_directory()),exist_ok=True)
	f = open("{}/rendered-configs/{}.{}".format(get_home_directory(),node_object[index]['name'],template.replace('jinja2','')) + "conf", "w") 
	config = baseline.render(nodes = node_object[index],with_remediation = with_remediation)
	f.write(config) 
	f.close 

	return config

def remediate(input):
	"""
		Custom filter to process boolean.
	"""
	if with_remediate == True:
		return input
	else:
		return ''
