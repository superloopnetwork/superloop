"""
	This function prepares the pushing of ACLs to the matched firewalls
	against a specified policy file. If no argument is given, it will
	match against all available policies.
"""
import initialize
from parse_cmd import parse_firewall_acl
from get_property import get_updated_list

def policies(policy_list,node_policy,policy_list_copy,auditcreeper):

	commands = []
	redirect = []
	policy_list_copy = policy_list
	if auditcreeper:
		policy_list = policy_list_copy[0]
	"""
		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list

		:param commands: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list
	"""
	for index in initialize.element_policy:
		redirect.append('push_acl')
		""" 
			The below forloop takes care of the configs for each policy term per firewall node(s).
		"""
		for policy in policy_list:
			"""
				Un-comment the below print statement for debuging purposes.
			"""
#			print("{}".format(node_policy[index]['name']))
#			print("{}".format(policy))
			parse_firewall_acl(node_policy[index],policy)
			if auditcreeper:
				policy_list = get_updated_list(policy_list_copy)

	return commands
