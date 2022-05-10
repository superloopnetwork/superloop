import initialize
import ipaddress
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
	acl_list = process_json(node_policy['hardware_vendor'],node_policy['opersys'],node_policy['type'],policy)
	config_list = []
	directory = get_policy_directory(node_policy['hardware_vendor'],node_policy['opersys'],node_policy['type'])
	PATH_FILTER_RE = r"\'.+\'"
	set_address = []
	set_address_group = []
	"""
		:param acl_list: Entire ACLs from the polic(y/ies) per file.
		:type acl_list: list

		:param config_list: ACL configurations storage.
		:type config_list: list

		:param directory: Path to network objects file. Example: NETWORKS.net
		:type directory: str

		:param PATH_FILTER_RE: Path to network objects file. Example: NETWORKS.net
		:type PATH_FILTER_RE: str
	"""
#	print(directory)
	"""
		Open the JSON policy file and parse out the audit_filter section via 
		regular expression.
	"""
	with open('{}'.format(directory) + policy, 'r') as file:
		parse_include = file.readline()
	path = eval(re.findall(PATH_FILTER_RE, parse_include)[0])
#	print(path)
	"""
		Uncomment the below print statement for debugging purposes
	"""
#	print("PATH_FILTER: {}".format(path))
	"""
		Uncomment the below print statement for debugging purposes
	"""
#	print("ACL_LIST inside parse_firewall_acl: {}".format(acl_list))
	for acl in acl_list:
		term = acl['term']
		to_zone = acl['to_zone']	
		from_zone = acl['from_zone']	
		source_address = acl['source']
		destination_address = acl['destination']
		source_user = acl['source_user']
		category = acl['category']
		application = acl['application']
		service = acl['service']
		source_hip = acl['source_hip']
		destination_hip = acl['destination_hip']
		tag = acl['tag']
		action = acl['action']
		description = acl['description']
		source_object_group = object_group(path,source_address,set_address,set_address_group)
		destination_object_group = object_group(path,destination_address,set_address,set_address_group)
		if node_policy['hardware_vendor'] == 'cisco' or node_policy['hardware_vendor'] == 'juniper' or node_policy['hardware_vendor'] == 'palo_alto':
			config_list.append('set rulebase security rules \"{}\" to {}'.format(term,to_zone))
			config_list.append('set rulebase security rules \"{}\" from {}'.format(term,from_zone))
			config_list.append('set rulebase security rules \"{}\" source {}'.format(term,source_address))
			config_list.append('set rulebase security rules \"{}\" destination {}'.format(term,destination_address))
			config_list.append('set rulebase security rules \"{}\" source-user {}'.format(term,source_user))
			config_list.append('set rulebase security rules \"{}\" category {}'.format(term,category))
			config_list.append('set rulebase security rules \"{}\" application {}'.format(term,application))
			config_list.append('set rulebase security rules \"{}\" service {}'.format(term,service))
			config_list.append('set rulebase security rules \"{}\" source-hip {}'.format(term,source_hip))
			config_list.append('set rulebase security rules \"{}\" destination-hip {}'.format(term,destination_hip))
			config_list.append('set rulebase security rules \"{}\" tag {}'.format(term,tag))
			config_list.append('set rulebase security rules \"{}\" action {}'.format(term,action))
	"""
		Removing any duplicates set_address from list.
	"""
	set_address = list(set(set_address))
	for address in set_address:
		print(address)
	set_address_group = list(set(set_address_group))
	for group in set_address_group:
		print(group)
	for config_line in config_list:
		print(config_line)
	return None 

def object_group(path,object_group_acl,set_address,set_address_group):
	"""
		:param object_group_acl: List of the object group(s) specified in the policy file.
		:type object_group_acl: list

		:param all_object_group_list: The entire NETWORKS.net file in a list.
		:type all_object_group_list: list
    """
	with open('{}'.format(path), 'r') as file:
		object_group_string = file.read()
		all_object_groups_list = object_group_string.split('\n')
	for object_group in object_group_acl:
		"""
			The below code will collect all the hosts address that are inputed.
		"""
		ipv4 = check_ipv4_address('{}'.format(object_group))
		ip_address = object_group.split('/')[0]
		if re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",ip_address):
			if ipv4:
				netmask = object_group.split('/')[1]
				if netmask == '32':
					set_address.append('set address H-{} ip-netmask {}'.format(object_group,object_group))
				else:
					set_address.append('set address N-{} ip-netmask {}'.format(object_group,object_group))
			else:
				print('+ The IP address {} is not valid. Please correct it in the policy file.'.format(ip_address))
				exit()
		else:
			if '{} ='.format(object_group) in set(all_object_groups_list):
				element = all_object_groups_list.index('{} ='.format(object_group))
				element = element + 1
				list_group = ''
				str_set_address_group = 'set address-group {} static ['.format(object_group)
				str_end_bracket = ']'
				address_group = []
				while all_object_groups_list[element] != '':
					ipv4 = check_ipv4_address('{}'.format(all_object_groups_list[element]))
					netmask = all_object_groups_list[element].split('/')[1]
					if ipv4:
						"""
							The below code will check if it's a host or a network and create the neccessary address for it beginning with H for host or N for network.
						"""
						if netmask == '32':
							set_address.append('set address H-{} ip-netmask {}'.format(all_object_groups_list[element],all_object_groups_list[element]))
							address_group.append('{}'.format(all_object_groups_list[element]))
						else:
							set_address.append('set address N-{} ip-netmask {}'.format(all_object_groups_list[element],all_object_groups_list[element]))
							address_group.append('{}'.format(all_object_groups_list[element]))
						element = element + 1
					else:
						print('+ The IP address {} is not valid. Please correct it in the NETWORKS.net file.'.format(all_object_groups_list[element]))
						exit()
						
				"""
					Building the address_group so it can be appended to the set_address_group
				"""
				for group in address_group:
					index_position = address_group.index(group)
					if len(address_group) - 1 == index_position:
						list_group = list_group + '{}'.format(group)
					else:
						list_group = list_group + '{} '.format(group)
				set_address_group.append('{} {} {}'.format(str_set_address_group,list_group,str_end_bracket))
			elif '{} ='.format(object_group) not in set(all_object_groups_list):
				print('+ The object-group \'{}\' does not exist in the NETWORKS.net file.'.format(object_group))
				exit()
	return None

def check_ipv4_address(ipv4_address):
	try:
		ipaddress.IPv4Network(ipv4_address)
		return True
	except ValueError:
		return False
