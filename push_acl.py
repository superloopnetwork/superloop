### THIS MODULE CONTROLS THE PUSHING OF THE TEMPLATES.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_json
from search import search_node
from confirm_push import confirm_push
import initialize

def push_acl(args):

	redirect = []
	ext = '.jinja2'
	commands = initialize.configuration
	auditcreeper_flag = False
	output = False 
	argument_node = args.node
	remediation = True
	with_remediation = True

	### NODE_OBJECT IS A LIST OF ALL THE NODES IN THE DATABASE WITH ALL ATTRIBUTES
	node_object = process_nodes()

	### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
	match_node = search_node(argument_node,node_object)

	if(len(match_node) == 0):
		print("+ [NO MATCHING NODES AGAINST DATABASE]")
		print("")

	else:

		acl = process_json()

		print acl
		

#		for index in initialize.element:
#			redirect.append('push_cfgs')
#
#		confirm_push(redirect,commands)
#		print("")
