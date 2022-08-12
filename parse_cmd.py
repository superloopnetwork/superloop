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

def parse_firewall_acl(node_object,policy):
	"""
		This function will generate firewall acls based on the hardware_vendor and os.
	"""
	acl_list = process_json(node_object['hardware_vendor'],node_object['opersys'],node_object['type'],policy)
	commands = [] 
	rulebase_security = []
	directory = get_policy_directory(node_object['hardware_vendor'],node_object['opersys'],node_object['type'])
	NETWORK_PATH_FILTER_RE = r"\'.+NETWORKS.net\'"
	SERVICES_PATH_FILTER_RE = r"\'.+SERVICES.net\'"
	APPLICATIONS_PATH_FILTER_RE = r"\'.+APPLICATIONS.net\'"
	SOURCE_DEVICE_PATH_FILTER_RE = r"\'.+SOURCE_DEVICE.net\'"
	SOURCE_USER_PATH_FILTER_RE = r"\'.+SOURCE_USER.net\'"
	ZONES_PATH_FILTER_RE = r"\'.+ZONES.net\'"
	set_address = []
	set_address_group = []
	set_service = []
	set_service_group = []
	"""
		:param acl_list: Entire ACLs from the polic(y/ies) per file.
		:type acl_list: list

		:param rulebase_security: ACL configurations storage.
		:type rulebase_security: list

		:param directory: Path to network objects file. Example: NETWORKS.net
		:type directory: str

		:param NETWORK_PATH_FILTER_RE: Path to network objects file. Example: NETWORKS.net
		:type NETWORK_PATH_FILTER_RE: str
	"""
#	print(directory)
	"""
		Open the JSON policy file and parse out the audit_filter section via 
		regular expression.
	"""
	with open('{}'.format(directory) + policy, 'r') as file:
		parse_include = file.read()
	path_networks = eval(re.findall(NETWORK_PATH_FILTER_RE, parse_include)[0])
	path_services = eval(re.findall(SERVICES_PATH_FILTER_RE, parse_include)[0])
	path_applications = eval(re.findall(APPLICATIONS_PATH_FILTER_RE, parse_include)[0])
	path_source_device = eval(re.findall(SOURCE_DEVICE_PATH_FILTER_RE, parse_include)[0])
	path_source_user = eval(re.findall(SOURCE_USER_PATH_FILTER_RE, parse_include)[0])
	path_zones = eval(re.findall(ZONES_PATH_FILTER_RE, parse_include)[0])
	print(path_networks)
	"""
		Uncomment the below print statement for debugging purposes
	"""
#	print("PATH_FILTER: {}".format(path_networks))
	"""
		Uncomment the below print statement for debugging purposes
	"""
#	print("ACL_LIST inside parse_firewall_acl: {}".format(acl_list))
	create_object_group_network(path_networks,set_address,set_address_group)
	create_object_group_service(path_services,set_service,set_service_group)
	for acl in acl_list:
		term = acl.get('term',None)
		to_zone = acl.get('to_zone',None)	
		from_zone = acl.get('from_zone',None)
		source_address = acl.get('source',None)
		destination_address = acl.get('destination',None)
		source_user = acl.get('source_user',None)
		category = acl.get('category',None)
		application = acl.get('application',None)
		service = acl.get('service',None)
		source_hip = acl.get('source_hip',None)
		destination_hip = acl.get('destination_hip',None)
		tag = acl.get('tag',None)
		action = acl.get('action',None)
		log_start = acl.get('log_start',None)
		log_end = acl.get('log_end',None)
		log_setting = acl.get('log_setting',None)
		rule_type = acl.get('rule_type',None)
		group_tag = acl.get('group_tag',None)
		disabled = acl.get('disabled',None)
		profile_setting = acl.get('profile_setting',None)
		description = acl.get('description',None)
		exist = check_acl_group_exist(path_networks,path_services,path_applications,path_source_device,path_source_user,path_zones,term,to_zone,from_zone,source_address,destination_address,source_user,category,application,service,source_hip,destination_hip)
		if exist and node_object['hardware_vendor'] == 'cisco' or node_object['hardware_vendor'] == 'juniper' or node_object['hardware_vendor'] == 'palo_alto':
			if len(to_zone) > 1:
				rulebase_security.append('set rulebase security rules \"{}\" to {}'.format(term,to_zone))
			else:
				rulebase_security.append('set rulebase security rules \"{}\" to {}'.format(term,to_zone[0]))
			if len(from_zone) > 1:
				rulebase_security.append('set rulebase security rules \"{}\" from {}'.format(term,from_zone))
			else:
				rulebase_security.append('set rulebase security rules \"{}\" from {}'.format(term,from_zone[0]))
			if len(source_address) > 1:
				rulebase_security.append('set rulebase security rules \"{}\" source {}'.format(term,source_address))
			else:
				rulebase_security.append('set rulebase security rules \"{}\" source {}'.format(term,source_address[0]))
			if len(destination_address) > 1:
				rulebase_security.append('set rulebase security rules \"{}\" destination {}'.format(term,destination_address))
			else:
				rulebase_security.append('set rulebase security rules \"{}\" destination {}'.format(term,destination_address[0]))
			if len(source_user) > 1:
				rulebase_security.append('set rulebase security rules \"{}\" source-user {}'.format(term,source_user))
			else:
				rulebase_security.append('set rulebase security rules \"{}\" source-user {}'.format(term,source_user[0]))
			if len(category) > 1:
				rulebase_security.append('set rulebase security rules \"{}\" category {}'.format(term,category))
			else:
				rulebase_security.append('set rulebase security rules \"{}\" category {}'.format(term,category[0]))
			if len(application) > 1:
				rulebase_security.append('set rulebase security rules \"{}\" application {}'.format(term,application))
			else:
				rulebase_security.append('set rulebase security rules \"{}\" application {}'.format(term,application[0]))
			if len(application) > 1:
				rulebase_security.append('set rulebase security rules \"{}\" service {}'.format(term,service))
			else:
				rulebase_security.append('set rulebase security rules \"{}\" service {}'.format(term,service[0]))
			if acl.get('source_hip',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" source-hip {}'.format(term,source_hip[0]))
			if acl.get('destination_hip',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" destination-hip {}'.format(term,destination_hip[0]))
			if acl.get('tag',None) != None:
				if len(tag) > 1:
					rulebase_security.append('set rulebase security rules \"{}\" tag {}'.format(term,tag))
				else:
					rulebase_security.append('set rulebase security rules \"{}\" tag {}'.format(term,tag[0]))
			if acl.get('action',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" action {}'.format(term,action))
			if acl.get('description',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" description {}'.format(term,description))
			if acl.get('log_start',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" log-start {}'.format(term,log_start))
			if acl.get('log_end',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" log-end {}'.format(term,log_end))
			if acl.get('log_setting',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" log-setting {}'.format(term,log_setting))
			if acl.get('rule_type',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" rule-type {}'.format(term,rule_type))
			if acl.get('group_tag',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" group-tag {}'.format(term,group_tag))
			if acl.get('disabled',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" disabled {}'.format(term,disabled))
			if acl.get('profile_setting',None) != None:
				rulebase_security.append('set rulebase security rules \"{}\" profile-setting group {}'.format(term,profile_setting))
	"""
		Removing any duplicates set_address from list.
	"""
	set_service_group = list(dict.fromkeys(set_service_group))
	set_service = list(dict.fromkeys(set_service))
	set_address_group = list(dict.fromkeys(set_address_group))
	set_address = list(dict.fromkeys(set_address))
	for service_group in set_service_group:
		commands.append(service_group)
	for service in set_service:
		commands.append(service)
	for address_group in set_address_group:
		commands.append(address_group)
	for address in set_address:
		commands.append(address)
	for config_line in rulebase_security:
		commands.append(config_line.replace('\'',' ').replace(',','').replace('   ',' '))

	return commands 

def create_object_group_network(path_networks,set_address,set_address_group):
	with open('{}'.format(path_networks), 'r') as file:
		object_group_network_string = file.read()
		all_object_group_network_list = object_group_network_string.split('\n')
	for object_group in all_object_group_network_list:
		if '=' in object_group:
			"""
				The below section will all object-groups. Object-groups are allowed to have a combination of IPv4 addresses as well as reference to other object-groups.
			"""
			element = all_object_group_network_list.index('{}'.format(object_group))
			element = element + 1
			list_group = ''
			str_set_address_group = 'set address-group {}static ['.format(object_group).replace('=','')
			str_set_address_group_single = 'set address-group {}static'.format(object_group).replace('=','')
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
			if len(address_group) > 1:
				for group in address_group:
					index_position = address_group.index(group)
					if len(address_group) - 1 == index_position:
						list_group = list_group + '{}'.format(group)
					else:
						list_group = list_group + '{} '.format(group)
				set_address_group.append('{} {} {}'.format(str_set_address_group,list_group,str_end_bracket))
			else:
				set_address_group.append('{} {}'.format(str_set_address_group_single,address_group[0]))
		else:
			"""
				The below code handles non object-groups. Non object-groups must be a valid IPv4 address. Any other strings will be ignored.
			"""
			if object_group == '':
				continue
			elif '#' in object_group:
				continue
			elif object_group == 'any':
				continue
			elif '/' in object_group:
				address_group = []
				str_set_address_host = 'set address H-{} ip-netmask {}'.format(object_group,object_group)
				str_set_address_network = 'set address N-{} ip-netmask {}'.format(object_group,object_group)
				ipv4 = check_ipv4_address('{}'.format(object_group))
				if ipv4:
					ip_address = object_group.split('/')[0]
					netmask = object_group.split('/')[1]
					"""
						The below code will check if it's a host or a network and create the neccessary address for it beginning with H for host or N for network.
					"""
					if netmask == '32':
						set_address.append(str_set_address_host)
						address_group.append(object_group)
					else:
						set_address.append(str_set_address_network)
						address_group.append(object_group)
				else:
					print('+ IP address \'{}\' is invalid. Please correct the address in the NETWORKS.net file.'.format(object_group))
					exit()
			else:
				continue
				
	return None

def create_object_group_service(path_services,set_service,set_service_group):
	with open('{}'.format(path_services), 'r') as file:
		object_group_service_string = file.read()
		all_object_group_service_list = object_group_service_string.split('\n')
	for object_group in all_object_group_service_list:
		if '=' in object_group:
			"""
				The below section will all object-groups. Object-groups are allowed to have a combination of services (ex. TCP_443) 
				as well as reference to other object-groups.
			"""
			element = all_object_group_service_list.index('{}'.format(object_group))
			element = element + 1
			list_group = ''
			str_set_service_group = 'set service-group {}members ['.format(object_group).replace('=','')
			str_set_service_group_single = 'set service-group {}members'.format(object_group).replace('=','')
			str_end_bracket = ']'
			address_group = []
			while all_object_group_service_list[element] != '':
				if '_' in all_object_group_service_list[element]:
					protocol = all_object_group_service_list[element].split('_')[0].lower()
					port = all_object_group_service_list[element].split('_')[1]
					str_set_service = 'set service {} protocol {} port {}'.format(all_object_group_service_list[element],protocol,port)
					set_service.append(str_set_service)	
					address_group.append(all_object_group_service_list[element])
					element = element + 1
				elif all_object_group_service_list[element] == 'service-http' or all_object_group_service_list[element] == 'service-https':
					address_group.append(all_object_group_service_list[element])
					element = element + 1
					continue
				else:
					if '{} ='.format(all_object_group_service_list[element]) in all_object_group_service_list:
						address_group.append(all_object_group_service_list[element])
						element = element + 1
					else:
						print('+ object-group \'{}\' was not found in SERVICES.net file. Please create or correct the name.'.format(all_object_group_service_list[element]))
						exit()
			if len(address_group) > 1:
				for group in address_group:
					index_position = address_group.index(group)
					if len(address_group) - 1 == index_position:
						list_group = list_group + '{}'.format(group)
					else:
						list_group = list_group + '{} '.format(group)
				set_service_group.append('{} {} {}'.format(str_set_service_group,list_group,str_end_bracket))
			else:
				set_service_group.append('{} {}'.format(str_set_service_group_single,address_group[0]))
		else:
			"""
				The below code handles non object-groups. Non object-groups must be a valid service (ex. TCP_443). Any other strings will be ignored.
			"""
			if object_group == '':
				continue
			elif '#' in object_group: 
				continue
			elif object_group == 'any':
				continue
			elif object_group == 'service-http' or object_group == "service-https" or object_group == 'application-default':
				continue
			elif '_' in object_group:
				address_group = []
				protocol = object_group.split('_')[0].lower()
				port = object_group.split('_')[1]
				str_set_service = 'set service {} protocol {} port {}'.format(object_group,protocol,port)
				set_service.append('{}'.format(str_set_service))
			else:
				continue
			
	return None

def check_ipv4_address(ipv4_address):
	try:
		ipaddress.IPv4Network(ipv4_address)
		return True
	except ValueError:
		return False
	return None

def check_acl_group_exist(path_networks,path_services,path_applications,path_source_device,path_source_user,path_zones,term,to_zone,from_zone,source_address,destination_address,source_user,category,application,service,source_hip,destination_hip):
	with open('{}'.format(path_networks), 'r') as file:
		object_group_network_string = file.read()
		all_object_group_network_list = object_group_network_string.split('\n')
	with open('{}'.format(path_applications), 'r') as file:
		application_group_string = file.read()
		all_application_group_list = application_group_string.split('\n')
	with open('{}'.format(path_services), 'r') as file:
		service_group_string = file.read()
		all_service_group_list = service_group_string.split('\n')
	with open('{}'.format(path_source_user), 'r') as file:
		source_user_group_string = file.read()
		all_source_user_group_list = source_user_group_string.split('\n')
	with open('{}'.format(path_source_device), 'r') as file:
		source_hip_group_string = file.read()
		all_souce_hip_group_list = source_hip_group_string.split('\n')
	with open('{}'.format(path_zones), 'r') as file:
		zone_group_string = file.read()
		all_zone_group_list = zone_group_string.split('\n')
	for source in source_address:
		if '{} ='.format(source) in set(all_object_group_network_list) or source in set(all_object_group_network_list):
			continue
		else:
			print('+ source object \'{}\' in policy file under term; \'{}\', does not exist in the NETWORKS.net file. Please ensure the object is present.'.format(source,term))
			exit()
	for destination in destination_address:
		if '{} ='.format(destination) in set(all_object_group_network_list) or destination in set(all_object_group_network_list):
			continue
		else:
			print('+ destination object \'{}\' in policy file under term; \'{}\', does not exist in the NETWORKS.net file. Please ensure the object is present.'.format(destination,term))
			exit()
	for app in application:
		if '{} ='.format(app) in set(all_application_group_list) or app in set(all_application_group_list):
			continue
		else:
			print('+ application object \'{}\' in policy file under term; \'{}\', does not exist in the APPLICATIONS.net file. Please ensure the object is present.'.format(app,term))
			exit()
	for serv in service:
		if '{} ='.format(serv) in set(all_service_group_list) or serv in set(all_service_group_list):
			continue
		else:
			print('+ service object \'{}\' in policy file under term; \'{}\', does not exist in the SERVICES.net file. Please ensure the object is present.'.format(serv,term))
			exit()
	for source_device in service:
		if '{} ='.format(serv) in set(all_service_group_list) or serv in set(all_service_group_list):
			continue
		else:
			print('+ service object \'{}\' in policy file under term; \'{}\', does not exist in the SERVICES.net file. Please ensure the object is present.'.format(serv,term))
			exit()
	for zone in to_zone:
		if '{} ='.format(zone) in set(all_zone_group_list) or zone in set(all_zone_group_list):
			continue
		else:
			print('+ to_zone object \'{}\' in policy file under term; \'{}\', does not exist in the ZONES.net file. Please ensure the object is present.'.format(zone,term))
			exit()
	for zone in from_zone:
		if '{} ='.format(zone) in set(all_zone_group_list) or zone in set(all_zone_group_list):
			continue
		else:
			print('+ from_zone object \'{}\' in policy file under term; \'{}\', does not exist in the ZONES.net file. Please ensure the object is present.'.format(zone,term))
			exit()

	return True
