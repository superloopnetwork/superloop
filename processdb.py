"""
	This module controls the process of yaml files to initialize database.
"""
import commentjson
import json
import os
import yaml
from node_create import node_create
from get_property import get_real_path
from get_property import get_policy_directory

def process_nodes():
	with open("{}/database/nodes.yaml".format(get_real_path())) as yaml_file:
		node_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return node_object
	
def process_templates():
	with open("{}/database/templates.yaml".format(get_real_path())) as yaml_file:
		template_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return template_object

def process_models():
	with open("{}/database/models.yaml".format(get_real_path())) as yaml_file:
		models_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return models_object

def process_policies():
	with open("{}/database/policy_push.yaml".format(get_real_path())) as yaml_file:
		policy_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return policy_object 

def process_json(hardware_vendor,opersys,device_type,policy_file):
	if hardware_vendor == 'cisco' and  opersys == 'ios' and device_type == 'firewall':
		with open("{}/policy/cisco/ios/firewall/{}".format(get_real_path(),policy_file)) as json_file:
			data = commentjson.load(json_file)

	elif hardware_vendor == 'juniper' and opersys == 'junos' and device_type == 'vfirewall':
		with open("{}/policy/juniper/junos/firewall/{}".format(get_real_path(),policy_file)) as json_file:
			data = commentjson.load(json_file)

	return data
