### THIS FUNCTION PREPARES THE PUSHING OF ACL TO THE MATCHED
### FIREWALLS AGAINST A SPECIFIED POLICY FILE. IF NO ARGUMENT
### IS GIVEN, IT WILL MATCH AGAINST ALL AVAILABLE POLICIES.
from parse_cmd import parse_firewall_acl
from get_property import get_updated_list
import initialize


def policies(policy_list,node_policy,policy_list_copy,auditcreeper_flag):

	redirect = []
	commands = []

	for index in initialize.element_policy:
		redirect.append('push_acl')
		# THE BELOW FORLOOP TAKES CARE OF THE CONFIGS FOR EACH POLICY TERM PER FIREWALL NODES
		for policy in policy_list:
			###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
			print("{}".format(node_policy[index]['hostname']))
			print("{}".format(policy))
			parse_firewall_acl(node_policy[index],policy)
			if(auditcreeper_flag):
				policy_list = get_updated_list(policy_list_copy)

	return commands
