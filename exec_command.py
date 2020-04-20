### THIS MODULE EXECUTES USER REQUESTED COMMANDS TO DEVICES.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from lib.objects.basenode import BaseNode
from processdb import process_nodes
from search import search_node
from search import node_element 
from node_create import node_create
from multithread import multithread_engine
import initialize

def exec_command(args):

	redirect = []
	redirect.append('exec_command') 
	command = args.argument
	argument_node = args.node

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
		multithread_engine(initialize.ntw_device,redirect,command)
