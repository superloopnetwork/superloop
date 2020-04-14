### PARSE_COMMANDS FUNCTION WILL GENERATE THE COMMANDS IN A FORM A LIST SO IT CAN BE
### FED INTO THE METHOD OF THE OBJECT CREATED.
### PARSE_FIREWALL_ACL FUNCTION WILL GENERATE FIREWALL ACLS BASED ON THE PLATFORM AND OS
from processdb import process_json
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
	AUDIT_FILTER_RE = r"\[.*\]"

	### THIS WILL OPEN THE JINJA2 TEMPLATE AND PARSE OUT THE AUDIT_FILTER SECTION VIA REGULAR EXPRESSION
	directory = get_template_directory(node_object[index]['platform'],node_object[index]['os'],node_object[index]['type'])
	f = open("{}".format(directory) + template, "r")
	parse_audit = f.readline()
	audit_filter = eval(re.findall(AUDIT_FILTER_RE, parse_audit)[0])

	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print("NODE_POLICY: {}".format(node_policy))
	acl_list = process_json(node_policy['platform'],node_policy['os'],node_policy['type'],policy)
	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print("ACL_LIST inside parse_firewall_acl: {}".format(acl_list))
	for acl in acl_list:
		term = acl['term']
		source_address = acl['source']
		destination_address = acl['destination']
		protocol = acl['protocol']
		destination_port = acl['destination-port']
		action = acl['action']
		if(node_policy['platform'] == 'cisco' or node_policy['platform'] == 'juniper'):
			print("{} {} {} {} {} {}".format(term,source_address,destination_address,protocol,destination_port,action))
			config_list = "{} {} {} {} {} {}".format(term,source_address,destination_address,protocol,destination_port,action) 
		acl_list = process_json(node_policy['platform'],node_policy['os'],node_policy['type'],policy)
	
	return config_list
