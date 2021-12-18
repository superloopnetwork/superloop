"""
	This module controls the push of the templates.
"""
import initialize
from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_templates
from search import search_node
from search import search_template
from mediator import mediator
from render import render
from node_create import node_create
from confirm import confirm

def push_cfgs(args):
	argument_node = args.node
	auditcreeper = False
	commands = initialize.configuration
	ext = '.jinja2'
	output = False 
	redirect = []
	push_cfgs = False
	with_remediation = True
	authentication = False
	"""
		:param argument_node: Argument accepted as regular expression.
		:type augument_node: str
		
		:param auditcreeper: When auditcreeper is active/non-active.
		:type auditcreeper: bool
		
		:param commands: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list
		
		:param ext: File extention
		:type ext: str 
		
		:param output: Flag to output to stdout.  
		:type ext: bool 
		
		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list
		
		:param push_cfgs: This flag is to determine if a push is required for Cisco like platforms. Juniper will continue to push configs no matter if there are no diffs. 
		:type ext: bool 

		:param with_remediation: Current function to remediate or not remediate.  
		:type ext: bool 
	"""
	if(args.file is None):
		template_list = []
		auditcreeper = True
	else:
		template = args.file + ext
		template_list = []
		template_list.append(template)
	node_object = process_nodes()
	node_template = process_templates()
	match_node = search_node(argument_node,node_object)
	match_template = search_template(template_list,match_node,node_template,node_object,auditcreeper)
	"""
		:param node_object: All node(s) in the database with all attributes.
		:type node_object: list

		:param node_template: All templates based on hardware_vendor and device type.
		:type node_template: list

		:param match_node: Nodes that matches the arguements passed in by user.
		:type match_node: list

		:param match_template: Return a list of 'match' and/or 'no match'.
		:type match_template: list 
	"""
	if len(match_node) == 0:
		print('+ No matching node(s) found in database.')
		print('')
	elif 'NO MATCH' in match_template:
		print('+ No matching template(s) found in database.')
		print('')
	else:
		node_create(match_node,node_object)
		for index in initialize.element:
			if node_object[index]['hardware_vendor'] == 'cisco':
				get_diff = True
				break
		if get_diff:
			mediator(template_list,node_object,auditcreeper,output,with_remediation)	
		else:
			render(template_list,node_object,auditcreeper,output,with_remediation)
		for index in initialize.element:
			redirect.append('push_cfgs')
		for index in range(len(initialize.element)):
			if len(commands[index]) != 0:
				push_cfgs = True
				break
			else:
				push_cfgs = False
		if push_cfgs:
			confirm(redirect,commands,authentication)
		print('')

	return None
