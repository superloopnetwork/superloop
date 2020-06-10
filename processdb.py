### THIS MODULE PROCESS THE YAML FILE TO CREATE THE DATABASES OF BOTH
### NODES AND TEMPLATES

from node_create import node_create
from get_property import get_policy_directory
import yaml
import json
import commentjson

def process_nodes():

	with open("/database/nodes.yaml") as yaml_file:
		node_object = yaml.load(yaml_file)

	return node_object
	
def process_templates():

	with open("/database/templates.yaml") as yaml_file:
		template_object = yaml.load(yaml_file)

	return template_object

def process_encrypted():

	with open("/database/encrypted.yaml") as yaml_file:
		encrypted_string = yaml.load(yaml_file)

	return encrypted_string

def process_policies():

	with open("/database/policy_push.yaml") as yaml_file:
		policy_object = yaml.load(yaml_file)

	return policy_object 

def process_json(platform,os,device_type,policy_file):

	if(platform == 'cisco' and os == 'ios' and device_type == 'firewall'):
		with open("/policy/cisco/ios/firewall/{}".format(policy_file)) as json_file:
			data = commentjson.load(json_file)

	elif(platform == 'juniper' and os == 'junos' and device_type == 'vfirewall'):
		with open("/policy/juniper/junos/firewall/{}".format(policy_file)) as json_file:
			data = commentjson.load(json_file)

	return data
