"""
	This module executes user requested commands to devices.
"""
import initialize
from lib.objects.basenode import BaseNode
from processdb import process_nodes
from search import search_node
from search import node_element 
from node_create import node_create
from multithread import multithread_engine

def exec_cmd(args):
	argument_command = args.command
	argument_node = args.node
	redirect = []
	authentication = True
	"""
		:param argument_command: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list
		
		:param argument_node: Argument accepted as regular expression.
		:type augument_node: str
		
		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list
	"""
	redirect.append('exec_cmd') 
	try:
		if argument_command == 'reload' or argument_command == 'reboot':
			print("superloopError: command not supported")
			return False
		else:
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
				print()
			else:
				node_element(match_node,node_object)
				node_create(match_node,node_object)
				multithread_engine(initialize.ntw_device,redirect,argument_command,authentication)
	except Exception as error:
		print("ExceptionError: an exception occured")
		print(error)

	return None
