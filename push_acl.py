### THIS MODULE CONTROLS THE PUSHING OF THE POLICIES FOR FIREWALLS.
### NODE_POLICY IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### POLICY_PUSH.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_policies
from search import search_node
from search import search_policy
from node_create import node_create
from confirm_push import confirm_push
from parse_cmd import parse_firewall_acl
from get_property import get_updated_list
from policies import policies
import initialize

def push_acl(args):

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

#	print("NODE_POLICY: {}".format(node_policy))
	### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
	match_node = search_node(argument_node,node_object)

	### MATCH_TEMPLATE IS A LIST OF 'MATCH' AND/OR 'NO MATCH' IT WILL USE THE MATCH_NODE
	### RESULT, RUN IT AGAINST THE NODE_OBJECT AND COMPARES IT WITH NODE_TEMPLATE DATABASE
	### TO SEE IF THERE IS A TEMPLATE FOR THE SPECIFIC PLATFORM AND TYPE.
	match_policy = search_policy(policy_list,match_node,node_policy,node_object,auditcreeper_flag)

	### THIS WILL PARSE OUT THE GENERATED CONFIGS FROM THE *.JINJA2 FILE TO A LIST

	### POLICY_LIST_COPY TAKE A COPY OF THE CURRENT POLICY_LIST
	policy_list_original = policy_list[:]
	policy_list_copy = policy_list
	### THE BELOW LENGTH OF MATCH_POLICY != 0 WILL TAKE CARE OF INVALID MATCH OF FIREWALL NODES
	### AGAINST NONE ARGS.FILE ARGUEMENT
	if(auditcreeper_flag and len(match_policy) != 0):
		policy_list = policy_list_copy[0]

	if(len(match_node) == 0):
		print("[!] [INVALID MATCHING NODE(S) AGAINST DATABASE]")
		print("")
	elif((len(match_policy) == 0) or ('NO MATCH' in match_policy)):
		print("[!] [INVALID FIREWALL NODE(S) ASSOCIATING WITH INVALID POLICY/POLICIES]")
		print("")

	else:
		node_create(match_node,node_object)
		policies(policy_list,node_policy,policy_list_copy,auditcreeper_flag)
		###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#		print("ELEMENT_POLICY: {}".format(initialize.element_policy))

#			for acl in acl_list:
#				config_list = parse_firewall_acl(node_object[index],acl)
#				commands.append(config_list)
#
#		print commands
#
#		confirm_push(redirect,commands)
#		print("")
