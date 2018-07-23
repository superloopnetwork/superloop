### THIS MODULE PROCESS THE YAML FILE TO CREATE THE DATABASES OF BOTH
### NODES AND TEMPLATES

from node_create import node_create
import yaml

def process_nodes():

	with open("nodes.yaml") as yaml_file:
		node_object = yaml.load(yaml_file)

	return node_object
	
def process_templates():

	with open("templates.yaml") as yaml_file:
		template_object = yaml.load(yaml_file)

	return template_object
