"""
	This module controls the pushing of the templates. node_object is a list of dictionary compiled by the processdb module.
	It processes the information from the nodes.yaml file and stores it into a list of dictionary.
"""
import initialize
from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_policies
from processdb import process_templates
from search import search_node
from search import search_policy
from search import search_template
from mediator import mediator 
from node_create import node_create
from confirm import confirm

def auditdiff(args):
	argument_node = args.node
	argument_file = args.file
	argument_policy = args.policy
	auditcreeper = False
	commands = initialize.configuration	
	ext = {
		'jinja':'.jinja2',
		'json':'.json'
		}
	output = True
	push_cfgs = False
	redirect = []
	safe_push_list = []
	with_remediation = False 
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

		:param push_cfgs: This flag is to determine if a push is required for Cisco like platforms. Juniper will continue to push configs no matter if there are no diffs.
		:type ext: bool

		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list

		:param safe_push_list: A list of enable/disabled strings. This corresponds to templates that are safe to push (enable) vs. templates that are not safe to push (disabled).
		:type ext: list

		:param with_remediation: Current function to remediate or not remediate.
		:type ext: bool

		:param node_object: All node(s) in the database with all attributes.
		:type node_object: list

		:param node_template: All templates based on hardware_vendor and device type.
		:type node_template: list

		:param match_node: Nodes that matches the arguements passed in by user.
		:type match_node: list

		:param match_template: Return a list of 'match' and/or 'no match'.
		:type match_template: list 
	"""
	redirect.append('exec_cmd')
	node_object = process_nodes()
	match_node = search_node(argument_node,node_object)
	if argument_policy is not None:
		policy = argument_policy + ext['json']
		policy_list = []
		policy_list.append(policy)
		node_policy = process_policies()
		match_policy = search_policy(policy_list,safe_push_list,match_node,node_policy,node_object,auditcreeper,push_cfgs)
		policy_list_original = policy_list[:]
		policy_list_copy = policy_list
		if len(match_policy) != 0:
			policy_list = policy_list_copy
		if len(match_node) == 0:
			print('+ No matching node(s) found in database.')
			exit()
		elif 'NO MATCH' in match_policy:
			print('+ No matching policy(ies) found in database.')
			exit()
		else:
			node_create(match_node,node_object)
			mediator(args,policy_list,node_object,auditcreeper,output,with_remediation)
			exit()
	if argument_file is None and argument_policy is None:
		template_list = []
		auditcreeper = True
	else:
		template = args.file + ext['jinja']
		template_list = []
		template_list.append(template)
	node_template = process_templates()
	match_template = search_template(template_list,safe_push_list,match_node,node_template,node_object,auditcreeper,push_cfgs)
	if len(match_node) == 0:
		print('[x] No matching nodes found in database.')
		print('')
		exit()
	elif 'NO MATCH' in match_template or len(match_template) == 0:
		print('[x] No matching templates found in database.')
		print('')
		exit()
	else:
		node_create(match_node,node_object)
		mediator(args,template_list,node_object,auditcreeper,output,with_remediation)
#		if len(initialize.configuration) == 0:
#			pass	
#		else:
#			if remediation:
#				confirm(redirect,commands)

	return None	
