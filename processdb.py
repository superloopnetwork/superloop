### THIS MODULE PROCESS THE YAML FILE TO CREATE THE DATABASE

from node_create import node_create
import yaml

def processdb(args):

	with open("nodes.yaml") as yaml_file:
		node_object = yaml.load(yaml_file)

	return node_object
	
