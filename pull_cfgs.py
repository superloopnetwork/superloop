### THIS MODULE PULLS CONFIGS FROM ONE/MULTIPLE/ALL NODES BASED ON THE INPUTED ARGUMENT NODE.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from processdb import process_nodes
from search import search_node
from search import node_element 
from render import render
from node_create import node_create
from multithread import multithread_engine
from confirm import confirm
import initialize

def pull_cfgs(args):

	redirect = []
	auditcreeper = False
	commands = initialize.configuration
	argument_node = args.node 
	argument_confirm = args.confirm
	output = False
	remediation = False
	with_remediation = False

	try:
		if argument_confirm is None or argument_confirm.lower() == 'true':
			confirm_flag = True 
		elif argument_confirm.lower() == 'false':
			confirm_flag = False
		else:
			raise argparse.ArgumentTypeError('Boolean value expected.')

		### NODE_OBJECT IS A LIST OF ALL THE NODES IN THE DATABASE WITH ALL ATTRIBUTES
		node_object = process_nodes()
	
		### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
		match_node = search_node(argument_node,node_object)
	
		if(len(match_node) == 0):
			print("[+] [NO MATCHING NODES AGAINST DATABASE]")
			print("")
	
		else:
			node_element(match_node,node_object)
			node_create(match_node,node_object)	
			for index in initialize.element:
				redirect.append('pull_cfgs')
	
			if(confirm_flag):
				confirm(redirect,commands)
			else:
				multithread_engine(initialize.ntw_device,redirect,commands)
			print("")

	except Exception as error:
		print("ExceptionError: an exception occured")
		print(error)

