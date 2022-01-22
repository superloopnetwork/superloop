"""
	This module controls the pulling of configs.
"""
import initialize
import os
from processdb import process_nodes
from search import search_node
from search import node_element 
from render import render
from node_create import node_create
from multithread import multithread_engine
from confirm import confirm

def pull_cfgs(args):
	argument_confirm = args.confirm
	argument_node = args.node 
	commands = initialize.configuration
	output = False
	redirect = []
	authentication = True
	"""
		:param argument_configm: Argument accepted as boolean
		:type augument_confirm: bool

		:param argument_node: Argument accepted as regular expression.
		:type augument_node: str
		
		:param commands: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list

		:param output: Flag to output to stdout.  
		:type ext: bool 
		
		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list
	"""
	try:
		if argument_confirm is None or argument_confirm.lower() == 'true':
			confirm_flag = True 
		elif argument_confirm.lower() == 'false':
			confirm_flag = False
			authentication = False
			initialize.password = os.environ.get('NETWORK_PASSWORD')
		else:
			raise argparse.ArgumentTypeError('Boolean value expected.')
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
				redirect.append('pull_cfgs')
			if(confirm_flag):
				confirm(redirect,commands,authentication)
			else:
				multithread_engine(initialize.ntw_device,redirect,commands,authentication)
			print('')
	except Exception as error:
		print('ExceptionError: an exception occured')
		print(error)

	return None
