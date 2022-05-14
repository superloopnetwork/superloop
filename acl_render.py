"""
	This function prepares the pushing of ACLs to the matched firewalls
	against a specified policy file. If no argument is given, it will
	match against all available policies.
"""
import initialize
from parse_cmd import parse_firewall_acl
from get_property import get_updated_list
from get_property import get_policy_directory

def acl_render(policy_list,node_object,node_policy,policy_list_copy,auditcreeper):

	commands = [] 
	redirect = []
	policy_list_copy = policy_list
	if auditcreeper:
		policy_list = policy_list_copy[0]
		all_policies = policy_list_copy[0]
	"""
		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list

		:param commands: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list
	"""
	for index in initialize.element:
		get_hardware_vendor_policy_directory = get_policy_directory(node_object[index]['hardware_vendor'],node_object[index]['opersys'],node_object[index]['type'])
		print ("{}".format(node_object[index]['name']))
		redirect.append('push_acl')
		""" 
			The below iteration takes care of the configs for each policy file per firewall node(s).
		"""
		if auditcreeper:
			for policy in all_policies:
				print('{}{}'.format(get_hardware_vendor_policy_directory,policy))
			print('')
			for policy in policy_list:
				commands = parse_firewall_acl(node_policy[index],policy)
				policy_list = get_updated_list(policy_list_copy)
			for configs in commands:
				print(configs)
			initialize.configuration.append(commands)
		else:
			for policy in policy_list:
				print('{}{}'.format(get_hardware_vendor_policy_directory,policy))
				commands = parse_firewall_acl(node_policy[index],policy)
			for configs in commands:
				print(configs)

	return commands
