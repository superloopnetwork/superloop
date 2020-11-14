"""
	This module controls the pushing of local file.
"""
import initialize
import os
from lib.objects.basenode import BaseNode
from processdb import process_nodes
from search import search_node
from search import node_element 
from node_create import node_create
from confirm import confirm
from parse_cmd import parse_commands

def push_local(args):
	argument_filename = args.filename
	argument_node = args.node
	commands = initialize.configuration
	home_directory = os.path.expanduser('~')
	redirect = [] 
	"""
		:param argument_filename: Argument accepted as template name.
		:type augument_filename: str
		
		:param argument_node: Argument accepted as regular expression.
		:type augument_node: str
		
		:param commands: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list

		:param home_directory: User home directory.
		:type home_directory: str

		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list
	"""
	node_object = process_nodes()
	match_node = search_node(argument_node,node_object)
	"""
		:param node_object: All node(s) in the database with all attributes.
		:type node_object: list

		:param match_node: Nodes that matches the arguements passed in by user.
		:type match_node: list
	"""
	if len(match_node) == 0:
		print('+ No matching node(s) found in database.')
		print('')
	else:
		node_element(match_node,node_object)
		node_create(match_node,node_object)
		for index in initialize.element:
			redirect.append('push_cfgs')
		for index in initialize.element:
			config_list = []
			f = open('{}/{}'.format(home_directory,argument_filename), 'r')
			init_config = f.readlines()
			parse_commands(node_object[index],init_config)
		confirm(redirect,commands)

	return None
