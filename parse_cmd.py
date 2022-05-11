
import ipaddress
import re
from processdb import process_json
from get_property import get_home_directory
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
	create_object_group_network(path,set_address,set_address_group)
	create_object_group_service(set_address,set_address_group)
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
		exist = check_acl_group_exist(path,term,source_address,destination_address)
		if exist and node_policy['hardware_vendor'] == 'cisco' or node_policy['hardware_vendor'] == 'juniper' or node_policy['hardware_vendor'] == 'palo_alto':
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
	set_address = list(dict.fromkeys(set_address))
	for address in set_address:
		print(address)
	set_address_group = list(dict.fromkeys(set_address_group))
	for group in set_address_group:
		print(group)
	for config_line in config_list:
		print(config_line.replace('\'',' ').replace(',','').replace('   ',' '))
	return None 

def create_object_group_network(path,set_address,set_address_group):
	with open('{}'.format(path), 'r') as file:
		object_group_network_string = file.read()
		all_object_group_network_list = object_group_network_string.split('\n')
	for object_group in all_object_group_network_list:
		if '=' in object_group:
			element = all_object_group_network_list.index('{}'.format(object_group))
			element = element + 1
			list_group = ''
			str_set_address_group = 'set address-group {} static ['.format(object_group)
			str_end_bracket = ']'
			address_group = []
			while all_object_group_network_list[element] != '':
				str_set_address_host = 'set address H-{} ip-netmask {}'.format(all_object_group_network_list[element],all_object_group_network_list[element])
				str_set_address_network = 'set address N-{} ip-netmask {}'.format(all_object_group_network_list[element],all_object_group_network_list[element])
				ipv4 = check_ipv4_address('{}'.format(all_object_group_network_list[element]))
				if "/" in all_object_group_network_list[element]:
					if ipv4:
						ip_address = all_object_group_network_list[element].split('/')[0]
						netmask = all_object_group_network_list[element].split('/')[1]
						"""
							The below code will check if it's a host or a network and create the neccessary address for it beginning with H for host or N for network.
						"""
						if netmask == '32':
							set_address.append(str_set_address_host)
							address_group.append(all_object_group_network_list[element])
						else:
							set_address.append(str_set_address_network)
							address_group.append(all_object_group_network_list[element])
						element = element + 1
					else:
						print('+ IP address \'{}\' is invalid. Please correct the address in the NETWORKS.net file.'.format(all_object_group_network_list[element]))
						exit()
				else:
					if '{} ='.format(all_object_group_network_list[element]) in all_object_group_network_list:
						address_group.append(all_object_group_network_list[element])
						element = element + 1
					else:
						print('+ object-group \'{}\' was not found in NETWORKS.net file. Please create or correct the name.'.format(all_object_group_network_list[element]))
						exit()
			for group in address_group:
				index_position = address_group.index(group)
				if len(address_group) - 1 == index_position:
					list_group = list_group + '{}'.format(group)
				else:
					list_group = list_group + '{} '.format(group)
			set_address_group.append('{} {} {}'.format(str_set_address_group,list_group,str_end_bracket))
	return None

def create_object_group_service(set_service,set_service_group):
	path = '~/superloop_code/policy/SERVICES.net'.replace('~','{}'.format(get_home_directory()))
	with open('{}'.format(path), 'r') as file:
		object_group_service_string = file.read()
		all_object_groups_service_list = object_group_service_string.split('\n')
	for object_group in all_object_groups_service_list:
		if '=' in object_group:
			element = all_object_group_service_list.index('{}'.format(object_group))
			element = element + 1
			list_group = ''
			str_set_service_group = 'set service-group {} static ['.format(object_group)
			str_end_bracket = ']'
			address_group = []
			while all_object_group_service_list[element] != '':
				
			
	return None

def check_ipv4_address(ipv4_address):
	try:
		ipaddress.IPv4Network(ipv4_address)
		return True
	except ValueError:
		return False
	return None

def check_acl_group_exist(path,term,source_address,destination_address):
	with open('{}'.format(path), 'r') as file:
		object_group_network_string = file.read()
		all_object_group_network_list = object_group_network_string.split('\n')
	for source in source_address:
		if '{} ='.format(source) in all_object_group_network_list or source in all_object_group_network_list:
			continue
		else:
			print('+ Source object \'{}\' in policy file under term; \'{}\', does not exist in the NETWORKS.net file. Please ensure the object is present.'.format(source,term))
			exit()
	for destination in destination_address:
		if '{} ='.format(destination) in all_object_group_network_list or destination in all_object_group_network_list:
			continue
		else:
			print('+ Destination object \'{}\' in policy file under term; \'{}\', does not exist in the NETWORKS.net file. Please ensure the object is present.'.format(destination,term))
			exit()

	return True

