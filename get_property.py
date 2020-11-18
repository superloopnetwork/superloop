"""
	This module holds properties that superloop is required to retrieve.
"""
import os

home_directory = os.environ.get('HOME')

def get_port(node_object,element,ssh_id):
	if node_object[element[ssh_id]]['type'] == 'switch':
		port = '22'
	elif node_object[element[ssh_id]]['type'] == 'nas':
		port = '2222'
	else:
		port = '22'

	return port

def get_type(hostname):
	if('fw' in hostname):
		device_type = 'firewall'
	elif('rt' in hostname):
		device_type = 'router'
	elif('sw' in hostname):
		device_type = 'switch'

	return device_type

def get_template_directory(platform,opersys,device_type):
	"""
		This will return the appropreiate directory based on the device
		platform, operating system and type
	"""
	directory = ''
	if platform == 'cisco' and opersys == 'asa' and device_type == 'firewall':
		directory = '{}/templates/cisco/asa/firewall/'.format(home_directory)
	elif platform == 'cisco' and opersys == 'ios'and device_type == 'router':
		directory = '{}/templates/cisco/ios/router'.format(home_directory)
	elif platform == 'cisco' and opersys == 'ios'and device_type == 'switch':
		directory = '{}/templates/cisco/ios/switch/'.format(home_directory)
	elif platform == 'cisco' and opersys == 'nxos'and device_type == 'switch':
		directory = '{}/templates/cisco/nxos/switch/'.format(home_directory)
	elif platform == 'cisco' and opersys == 'nxos'and device_type == 'router':
		directory = '{}/templates/cisco/nxos/router/'.format(home_directory)
	elif platform == 'juniper' and opersys == 'junos' and device_type == 'vfirewall':
		directory = '{}/templates/juniper/junos/vfirewall/'.format(home_directory)
	elif platform == 'juniper' and opersys == 'junos' and device_type == 'router':
		directory = '{}/templates/juniper/junos/router/'.format(home_directory)
	elif platform == 'f5' and opersys == 'tmsh' and device_type == 'loadbalancer':
		directory = '{}/templates/f5/tmsh/ltm/'.format(home_directory)

	return directory

def get_policy_directory(platform,opersys,device_type):
	directory = ''
	if platform == 'cisco' and os == 'ios' and device_type == 'firewall':
		directory = '{}/policy/cisco/ios/firewall/'.format(home_directory)
	elif platform == 'juniper' and os == 'junos' and device_type == 'vfirewall':
		directory = '{}/policy/juniper/junos/firewall/'.format(home_directory)

	return directory

def get_updated_list(list_copy):
	"""
		This will get the current template list from the list. 
		Example: ['base.jinja'],['snmp.jinja','tacacs.jinja']]. 
		It will continue to pop off the 1st element until there 
		are only one element left.
	"""
	updated_list = []
	if len(list_copy) != 1:
		list_copy.pop(0)
		updated_list = list_copy[0]

	return updated_list

def get_syntax(node_object,index):
	"""
		This will return the correct syntax used for CiscoConfParse
		based on device platform.
	"""
	syntax = ''
	if node_object[index]['platform'] == 'cisco' and node_object[index]['type'] == 'firewall':
		syntax = 'asa'
	elif node_object[index]['platform'] == 'cisco' and node_object[index]['type'] == 'switch':
		syntax = 'ios'
	elif node_object[index]['platform'] == 'juniper' and node_object[index]['type'] == 'switch':
		syntax = 'junos'

	return syntax

def get_sorted_juniper_template_list(template_list):

	""" This will sort the Juniper template list from top configuration
		in the order they appear in a 'show configuration' juniper output.
		For example: groups, systems, chassis, security, snmp etc...
	"""
	sorted_juniper_template_list = []
	sorted_juniper_template_list_index = []
	config_order = {
					'groups.jinja2': 0 ,
					'system.jinja2': 1 ,
					'interfaces.jinja2': 2,
					'chassis.jinja2': 3 ,
					'snmp.jinja2': 4 ,
					'routing-options.jinja2': 5 ,
					'protocols.jinja2': 6 ,
					'policy-options.jinja2': 7 ,
					'security.jinja2': 8 ,
					'routing-instances.jinja2': 9
		}			 
	for template in template_list:         
		if template in config_order.keys():   
			sorted_juniper_template_list_index.append(config_order[template]) 

	"""
		Sorting the order of how the templates should be in comparison with
		with the Juniper 'show configuration' output.
	"""
	sorted_juniper_template_list_index.sort()
	"""
		Building the sorted template list and returning
	"""
	for element in sorted_juniper_template_list_index:
		template = list(config_order.keys())[list(config_order.values()).index(element)]
		sorted_juniper_template_list.append(template)

	return sorted_juniper_template_list

def get_location_directory(hostname,platform,type):
	directory = ''
	datacenter_location = ''
	if type == 'firewall':
		location_list = hostname.split('-')    
		datacenter_location = location_list[3]
	elif type == 'switch' or type == 'router' or type == 'vfirewall':
		location_list = hostname.split('.')    
		datacenter_location = location_list[3]

	directory = '{}/templates/{}/common/{}/'.format(home_directory,platform,datacenter_location)

	return directory 
