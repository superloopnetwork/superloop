"""
	This module controls the pushing of the policies for firewalls.
"""
from acl_render import acl_render
import initialize
from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_policies
from search import search_node
from search import search_policy
from node_create import node_create
from confirm import confirm
from parse_cmd import parse_firewall_acl
from get_property import get_updated_list

def push_acl(args):
	argument_node = args.node
	auditcreeper = False
	commands = initialize.configuration
	ext = '.json'
	output = False 
	policy_list = []
	safe_push_list = []
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

		:param policy_list: This stores a collection of polic(y/ies).  
		:type ext: list

		:param safe_push_list: A list of enable/disabled strings. This corresponds to templates that are safe to push (enable) vs. templates that are not safe to push (disabled).
		:type ext: list
	"""
	if(args.policy is None):
		auditcreeper = True
	else:
		policy = args.policy + ext
		policy_list.append(policy)
	node_object = process_nodes()
	node_policy = process_policies()
	match_node = search_node(argument_node,node_object)
	match_policy = search_policy(policy_list,safe_push_list,match_node,node_policy,node_object,auditcreeper)
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
	### THIS WILL PARSE OUT THE GENERATED CONFIGS FROM THE *.JINJA2 FILE TO A LIST

	### POLICY_LIST_COPY TAKE A COPY OF THE CURRENT POLICY_LIST
	policy_list_original = policy_list[:]
	policy_list_copy = policy_list
	### THE BELOW LENGTH OF MATCH_POLICY != 0 WILL TAKE CARE OF INVALID MATCH OF FIREWALL NODES
	### AGAINST NONE ARGS.FILE ARGUEMENT
	if(auditcreeper and len(match_policy) != 0):
		policy_list = policy_list_copy[0]
	if len(match_node) == 0:
		print('+ No matching node(s) found in database.')
	elif 'NO MATCH' in match_policy:
		print('+ No matching policy(ies) found in database.')
	else:
		node_create(match_node,node_object)
		policies(policy_list,node_policy,policy_list_copy,auditcreeper)
		###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#		print("ELEMENT_POLICY: {}".format(initialize.element_policy))

#			for acl in acl_list:
#				config_list = parse_firewall_acl(node_object[index],acl)
#				commands.append(config_list)
#
#		print commands
#
#		confirm(redirect,commands)
#		print("")
