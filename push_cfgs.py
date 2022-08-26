"""
	This module controls the push of the templates.
"""
import initialize
import json
import os
from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_templates
from search import search_node
from search import search_template
from mediator import mediator
from multithread import multithread_engine
from render import render
from node_create import node_create
from confirm import confirm

def push_cfgs(args):
	args.policy = None
	argument_confirm = args.confirm
	argument_node = args.node
	auditcreeper = False
	commands = initialize.configuration
	config_counter = 0
	debug = {}
	ext = '.jinja2'
	output = False 
	redirect = []
	safe_push_list = []
	push_cfgs = True
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
		:type redirect: list
		
		:param safe_push_list: A list of enable/disabled strings. This corresponds to templates that are safe to push (enable) vs. templates that are not safe to push (disabled).
		:type ext: list

		:param push_cfgs: This flag is to determine if a push is required for Cisco like platforms. Juniper will continue to push configs no matter if there are no diffs. 
		:type ext: bool 

		:param with_remediation: Current function to remediate or not remediate.  
		:type ext: bool 
	"""
#	try:
	if argument_confirm is None or argument_confirm.lower() == 'true':
		confirm_flag = True 
	elif argument_confirm.lower() == 'false':
		confirm_flag = False
		authentication = False
		initialize.password = os.environ.get('NETWORK_PASSWORD')
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
	match_template = search_template(template_list,safe_push_list,match_node,node_template,node_object,auditcreeper,push_cfgs)
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
		print('[x] No matching node(s) found in database.')
		print('')
		exit()
	elif 'NO MATCH' in match_template or len(match_template) == 0:
		print('[x] No matching template(s) found in database.')
		print('')
		exit()
	else:
		node_create(match_node,node_object)
		mediator(args,template_list,node_object,auditcreeper,output,with_remediation)	
		for index in initialize.element:
			redirect.append('push_cfgs')
		if not any(initialize.configuration):
			print('[>] There are no diffs to be pushed. All configuration matches template(s).')
			print('')
			exit()
		for index in initialize.debug_element:
			debug[node_object[index]['name']] = [initialize.configuration[config_counter]]
			config_counter = config_counter + 1
		debug_json = json.dumps(debug, indent=4)
		print('[DEBUG]\n{}'.format(debug_json))
#		for index in initialize.debug_element:
#			print('[DEBUG] {{{} : {}}}'.format(node_object[index]['name'],initialize.configuration[config_counter]))
#			config_counter = config_counter + 1
		for index in range(len(initialize.element)):
			if len(initialize.configuration) != 0:
				push_cfgs = True
				break
			else:
				push_cfgs = False
		if push_cfgs and confirm_flag:
			confirm(redirect,commands,authentication)
		elif push_cfgs and not confirm_flag:
			multithread_engine(initialize.ntw_device,redirect,commands,authentication)
		else:
			pass
		print('')
#	except Exception as error:
#		print('ExceptionError: an exception occured')
#		print(error)

	return None
