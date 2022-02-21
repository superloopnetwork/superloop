import initialize
import re
from processdb import process_json
from get_property import get_policy_directory


def parse_commands(node_object,init_config,set_notation):
	"""
		This function generates the commands in a form of a list so that
		it can be passed into the method of the object.
	"""
	commands = initialize.configuration
	config_list = []
	if node_object['hardware_vendor'] == 'juniper' and set_notation!=True:
		config_list.append('load replace terminal')
	elif node_object['hardware_vendor'] == 'f5':
		config_list.append('load sys config merge from-terminal')
	for config_line in init_config:
		strip_config = config_line.strip('\n')
		config_list.append(strip_config)
	if node_object['hardware_vendor'] == 'juniper' and set_notation!=True or node_object['hardware_vendor'] == 'f5':
		config_list.append('\x04')
	commands.append(config_list)

	return commands

def parse_negation_commands(push_configs):
	command_split = []
	commands = []
	for line in push_configs:
		command_split = line.split()
		"""
			The below if statement will negate binding configurations associated with policy on the Citrix Netscaler.
		"""
		if command_split[0] == 'no' and command_split[1] == 'bind' and command_split[6] == '-index':
			command_split[1] = 'unbind'
			command = ' '.join(command_split[1:6])
			commands.append(command)
		else:
			commands.append(line)
		
	return commands

def parse_firewall_acl(node_policy,policy):
	"""
		This function will generate firewall acls based on the hardware_vendor and os.
	"""
	config_list = []
	PATH_FILTER_RE = r"\'.+\'"
	"""
		:param config_list: ACL configurations storage.
		:type config_list: list

		:param PATH_FILTER_RE: Path to network objects file. Example: NETWORKS.net
		:type PATH_FILTER_RE: str
	"""
	"""
		Open the JSON policy file and parse out the audit_filter section via 
		regular expression.
	"""
	directory = get_policy_directory(node_policy['hardware_vendor'],node_policy['opersys'],node_policy['type'])
	acl_list = process_json(node_policy['hardware_vendor'],node_policy['opersys'],node_policy['type'],policy)
	with open('{}'.format(directory) + policy, 'r') as file:
#	f = open("{}".format(directory) + policy, "r")
		parse_include = file.readline()
	path = eval(re.findall(PATH_FILTER_RE, parse_include)[0])
	"""
		Uncomment the below print statement for debugging purposes
	"""
	#print("PATH_FILTER: {}".format(path))
	"""
		Uncomment the below print statement for debugging purposes
	"""
	#print("ACL_LIST inside parse_firewall_acl: {}".format(acl_list))
	for acl in acl_list:
		term = acl['term']
		source_address = acl['source']
		destination_address = acl['destination']
		protocol = acl['protocol']
		destination_port = acl['destination-port']
		action = acl['action']
		source_object_group = object_group(path,source_address)
		destination_object_group = object_group(path,destination_address)
		if node_policy['hardware_vendor'] == 'cisco' or node_policy['hardware_vendor'] == 'juniper':
			print("{} {} {} {} {} {}".format(term,source_address,destination_address,protocol,destination_port,action))
			config_list = "{} {} {} {} {} {}".format(term,source_address,destination_address,protocol,destination_port,action) 
	print
	return config_list

def object_group(path,object_group_search):
	subnets = []
	with open('{}'.format(path), 'r') as file:
		object_group_string = file.read()
		object_group_list = object_group_string.split('\n')
	if '{} ='.format(object_group_search) in set(object_group_list):
		print('TRUE')
		element = object_group_list.index('{} ='.format(object_group_search))
		element = element + 1
		print('{}'.format(object_group_list[element]))
		while object_group_list[element] != "":
			subnets.append(object_group_list[element])
			element = element + 1
		print(subnets)
	else:
		print('FALSE')

	return None
