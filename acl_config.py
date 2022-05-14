"""
	This module controls the rendering of policies.
"""
from get_property import get_secrets
from lib.objects.basenode import BaseNode
from acl_render import acl_render
from processdb import process_nodes
from processdb import process_policies
from search import search_node
from search import search_policy 
from render import render
from node_create import node_create
from multithread import multithread_engine
import initialize

def acl_config(args):
	argument_node = args.node
	auditcreeper = True 
	commands = initialize.configuration
	ext = '.json'
	output = True
	policy_list = []
	push_acl = False
	safe_push_list = []
	with_remediation = True 
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
		
		:param push_acl: This flag is to determine if a push is required for Cisco like platforms. Juniper will continue to push configs no matter if there are no diffs. 
		:type ext: bool

		:param safe_push_list: A list of enable/disabled strings. This corresponds to policies that are safe to push (enable) vs. policies that are not safe to push (disabled).
		:type ext: list

		:param with_remediation: Current function to remediate or not remediate.  
		:type ext: bool 
	"""
#	if(args.policy is None):
#		auditcreeper = True
#	else:
#	policy = args.policy + ext
#	policy_list.append(policy)
	node_object = process_nodes()
	node_policy = process_policies()
	match_node = search_node(argument_node,node_object)
	match_policy = search_policy(policy_list,safe_push_list,match_node,node_policy,node_object,auditcreeper,push_acl)
	"""
		:param node_object: All node(s) in the database with all attributes.
		:type node_object: list

		:param node_policy: All policies based on hardware_vendor and device type.
		:type node_policy: list

		:param match_node: Nodes that matches the arguements passed in by user.
		:type match_node: list

		:param match_policy: Return a list of 'match' and/or 'no match'.
		:type match_policy: list 
	"""
	### POLICY_LIST_COPY TAKE A COPY OF THE CURRENT POLICY_LIST
	policy_list_original = policy_list[:]
	policy_list_copy = policy_list
	### THE BELOW LENGTH OF MATCH_POLICY != 0 WILL TAKE CARE OF INVALID MATCH OF FIREWALL NODES
	### AGAINST NONE ARGS.FILE ARGUEMENT
#	if(auditcreeper and len(match_policy) != 0):
	if len(match_policy) != 0:
		policy_list = policy_list_copy[0]
	if len(match_node) == 0:
		print('+ No matching node(s) found in database.')
	elif 'NO MATCH' in match_policy:
		print('+ No matching policy(ies) found in database.')
	else:
		node_create(match_node,node_object)
		acl_render(policy_list,node_object,node_policy,policy_list_copy,auditcreeper)

	return None
