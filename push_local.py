### THIS MODULE CONTROLS THE PUSHING OF THE LOCAL FILE.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from lib.objects.basenode import BaseNode
from processdb import process_nodes
from search import search_node
from search import node_element 
from node_create import node_create
from confirm_push import confirm_push
from parse_commands import parse_commands
import initialize
import os

def push_local(args):

	redirect = [] 
	commands = initialize.configuration
	argument_node = args.node
	filename = args.filename

	### NODE_OBJECT IS A LIST OF ALL THE NODES IN THE DATABASE WITH ALL ATTRIBUTES
	node_object = process_nodes()

	### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
	match_node = search_node(argument_node,node_object)

	if(len(match_node) == 0):
		print("+ [NO MATCHING NODES AGAINST DATABASE]")
		print("")

	else:
		node_element(match_node,node_object)
		node_create(match_node,node_object)

		for index in initialize.element:
			redirect.append('push_cfgs')

		home_directory = os.path.expanduser('~')

		for index in initialize.element:

			config_list = []

			f = open("{}/{}".format(home_directory,filename), "r")

			init_config = f.readlines()
			parse_commands(node_object[index],init_config)

		confirm_push(redirect,commands)
