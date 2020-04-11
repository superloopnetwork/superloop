### THIS MODULE CONTROLS THE PUSHING OF THE POLICIES.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_policies
from processdb import process_json
from search import search_node
from search import search_policy
from auditdiff_engine import auditdiff_engine
from render import render
from node_create import node_create
from confirm_push import confirm_push
from parse_cmd import parse_firewall_acl
import initialize

def push_acl(args):

	redirect = []
	ext = '.json'
	commands = initialize.configuration
	auditcreeper_flag = False
	output = False 
	argument_node = args.node
	remediation = True
	with_remediation = True

	if(args.file is None):
#		print("ARGS.FILE IS NONE")
		policy_list = []
		auditcreeper_flag = True
	else:
#		print("ARGS.FILE IS VALID")
		policy = args.file + ext
		policy_list = []
		policy_list.append(policy)

	### NODE_OBJECT IS A LIST OF ALL THE NODES IN THE DATABASE WITH ALL ATTRIBUTES
	node_object = process_nodes()

	### NODE_POLICY IS A LIST OF ALL THE POLICY BASED ON PLATFORMS AND DEVICE TYPE
	node_policy = process_policies()

	### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
	match_node = search_node(argument_node,node_object)

	### MATCH_TEMPLATE IS A LIST OF 'MATCH' AND/OR 'NO MATCH' IT WILL USE THE MATCH_NODE
	### RESULT, RUN IT AGAINST THE NODE_OBJECT AND COMPARES IT WITH NODE_TEMPLATE DATABASE
	### TO SEE IF THERE IS A TEMPLATE FOR THE SPECIFIC PLATFORM AND TYPE.
	match_policy = search_policy(policy_list,match_node,node_policy,node_object,auditcreeper_flag)

	### THIS WILL PARSE OUT THE GENERATED CONFIGS FROM THE *.JINJA2 FILE TO A LIST

	if(len(match_node) == 0):
		print("[!] [INVALID MATCHING NODE(S) AGAINST DATABASE]")
		print("")
	### WHEN UNKNOWN NODE(S) (MATCHED SEARCH ENTRIES BUT NOT FIREWALL) DO NOT HAVE ANY POLICIES SETUP
	elif(len(match_policy) == 0):
		print("[!] [INVALID FIREWALL NODE(S) ASSOCIATING WITH INVALID POLICY/POLICIES]")
		print("")
	### WHEN KNOWN NODE(S) (MATCHED SEARCH ENTRIES ARE FIREWALLS) BUT DO NOT MATCH A POLICY)
	elif('NO MATCH' in match_policy):
		print("[!] [VALID FIREWALL NODE(S) ASSOCIATING WITH INVALID POLICY/POLICIES]")
		print("")

	else:
		node_create(match_node,node_object)
		acl_list = process_json()
		print acl_list
	
#		THE BELOW FORLOOP TAKES CARE OF THE REDIRECT FOR ALL NODES
		for index in initialize.element:
			redirect.append('push_acl')

#		THE BELOW FORLOOP TAKES CARE OF THE CONFIGS FOR EACH POLICY TERM
		for index in initialize.element:
			parse_firewall_acl(node_object[index],acl_list[index])
#
#		confirm_push(redirect,commands)
#		print("")
