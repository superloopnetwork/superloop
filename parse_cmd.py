### PARSE_COMMANDS FUNCTION WILL GENERATE THE COMMANDS IN A FORM A LIST SO IT CAN BE
### FED INTO THE METHOD OF THE OBJECT CREATED.
### PARSE_FIREWALL_ACL FUNCTION WILL GENERATE FIREWALL ACLS BASED ON THE PLATFORM AND OS
from processdb import process_json
from get_property import get_policy_directory
import initialize
import re


def parse_commands(node_object,init_config):

	commands = initialize.configuration

	config_list = []

	if(node_object['platform'] == 'juniper'):
		config_list.append('load replace terminal')

	for config_line in init_config:
		strip_config = config_line.strip('\n')
		config_list.append(strip_config)

	if(node_object['platform'] == 'juniper'):
		config_list.append('\x04')

	commands.append(config_list)

	return commands

def parse_firewall_acl(node_policy,policy):

	config_list = []
	PATH_FILTER_RE = r"\'.+\'"

	### THIS WILL OPEN THE JSON POLICY AND PARSE OUT THE AUDIT_FILTER SECTION VIA REGULAR EXPRESSION
#	print("{} {} {}".format(node_policy['platform'],node_policy['os'],node_policy['type']))
	directory = get_policy_directory(node_policy['platform'],node_policy['os'],node_policy['type'])

	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print("NODE_POLICY: {}".format(node_policy))
#	print("NODE: {}".format(policy))
	acl_list = process_json(node_policy['platform'],node_policy['os'],node_policy['type'],policy)
	f = open("{}".format(directory) + policy, "r")
	parse_include = f.readline()
	path = eval(re.findall(PATH_FILTER_RE, parse_include)[0])
	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
	print("PATH_FILTER: {}".format(path))
	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print("ACL_LIST inside parse_firewall_acl: {}".format(acl_list))
	for acl in acl_list:

		term = acl['term']
		source_address = acl['source']
		destination_address = acl['destination']
		protocol = acl['protocol']
		destination_port = acl['destination-port']
		action = acl['action']

		source_object_group = object_group(path,source_address)
		destination_object_group = object_group(path,destination_address)

		if(node_policy['platform'] == 'cisco' or node_policy['platform'] == 'juniper'):
			print("{} {} {} {} {} {}".format(term,source_address,destination_address,protocol,destination_port,action))
			config_list = "{} {} {} {} {} {}".format(term,source_address,destination_address,protocol,destination_port,action) 
	
	print
	return config_list

def object_group(path,object_group_search):

	subnets = []

	with open('{}'.format(path)) as f:
		object_group_string = f.read()
		object_group_list = object_group_string.split('\n')

#	print('{} ='.format(object_group_search))
	if('{} ='.format(object_group_search) in set(object_group_list)):
		print 'TRUE'
		element = object_group_list.index('{} ='.format(object_group_search))
		element = element + 1
		print '{}'.format(object_group_list[element])

		while object_group_list[element] != "":
			subnets.append(object_group_list[element])
			element = element + 1

		print subnets
	else:
		print 'FALSE'

	return None
