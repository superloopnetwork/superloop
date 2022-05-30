"""
	This module controls the process of yaml files to initialize database.
"""
import commentjson
import json
import os
import yaml
from yaml import CLoader as Loader
from node_create import node_create
from get_property import get_home_directory
from get_property import get_policy_directory

def process_nodes():
	with open("{}/superloop_code/database/nodes.yaml".format(get_home_directory()), 'r') as yaml_file:
		node_object = yaml.load(yaml_file,Loader=Loader)

	return node_object
	
def process_templates():
	with open("{}/superloop_code/database/templates.yaml".format(get_home_directory()), 'r') as yaml_file:
		template_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return template_object

def process_models():
	with open("{}/superloop_code/database/models.yaml".format(get_home_directory()), 'r') as yaml_file:
		models_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return models_object

def process_policies():
	with open("{}/superloop_code/database/policies.yaml".format(get_home_directory()), 'r') as yaml_file:
		policy_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return policy_object 

def process_json(hardware_vendor,opersys,device_type,policy_file):
	data = []
	if hardware_vendor == 'cisco' and  opersys == 'asa' and device_type == 'firewall':
		try:
			with open("{}{}".format(get_policy_directory(hardware_vendor,opersys,device_type),policy_file), 'r') as json_file:
				data = commentjson.load(json_file)
		except FileNotFoundError as error:
			print('+ Cannot locate file.')
			exit()
	elif hardware_vendor == 'juniper' and opersys == 'junos' and device_type == 'vfirewall':
		try:
			with open("{}{}".format(get_policy_directory(hardware_vendor,opersys,device_type),policy_file), 'r') as json_file:
				data = commentjson.load(json_file)
		except FileNotFoundError as error:
			print('+ Cannot locate file.')
			exit()
	return data
