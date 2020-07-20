### THIS MODULE PROCESS THE YAML FILE TO CREATE THE DATABASES OF BOTH
### NODES AND TEMPLATES

from node_create import node_create
from get_property import get_policy_directory
import yaml
import json
import commentjson
import os

home_directory = os.environ.get('HOME')

def process_nodes():

	with open("{}/database/nodes.yaml".format(home_directory)) as yaml_file:
		node_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return node_object
	
def process_templates():

	with open("{}/database/templates.yaml".format(home_directory)) as yaml_file:
		template_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return template_object

def process_encrypted():

	with open("{}/database/encrypted.yaml".format(home_directory)) as yaml_file:
		encrypted_string = yaml.load(yaml_file, yaml.UnsafeLoader)

	return encrypted_string

def process_models():

	with open("{}/database/models.yaml".format(home_directory)) as yaml_file:
		models_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return models_object

def process_policies():

	with open("{}/database/policy_push.yaml".format(home_directory)) as yaml_file:
		policy_object = yaml.load(yaml_file, yaml.UnsafeLoader)

	return policy_object 

def process_json(platform,os,device_type,policy_file):

	if(platform == 'cisco' and os == 'ios' and device_type == 'firewall'):
		with open("{}/policy/cisco/ios/firewall/{}".format(home_directory,policy_file)) as json_file:
			data = commentjson.load(json_file)

	elif(platform == 'juniper' and os == 'junos' and device_type == 'vfirewall'):
		with open("{}/policy/juniper/junos/firewall/{}".format(home_directory,policy_file)) as json_file:
			data = commentjson.load(json_file)

	return data
