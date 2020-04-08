### THIS MODULE PROCESS THE YAML FILE TO CREATE THE DATABASES OF BOTH
### NODES AND TEMPLATES

from node_create import node_create
import yaml
import json

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
		passwords = yaml.load(yaml_file)

	return passwords

def process_json():

	with open("/policy/policy.json") as json_file:
		data = json.load(json_file)

	return data
