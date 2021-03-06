"""
	This module holds properties that superloop is required to retrieve.
"""
import datetime
import os
import time

def get_home_directory():
	home_directory = os.getenv('HOME')

	return home_directory

def get_port(node_object,element,ssh_id):
	if node_object[element[ssh_id]]['type'] == 'switch':
		port = '22'
	elif node_object[element[ssh_id]]['type'] == 'nas':
		port = '2222'
	else:
		port = '22'

	return port

def get_type(name):
	if('fw' in name):
		device_type = 'firewall'
	elif('rt' in name):
		device_type = 'router'
	elif('sw' in name):
		device_type = 'switch'

	return device_type

def get_template_directory(hardware_vendor,opersys,device_type):
	"""
		This will return the appropreiate directory based on the device
		hardware_vendor, operating system and type
	"""
	directory = ''
	if hardware_vendor == 'cisco' and opersys == 'asa' and device_type == 'firewall':
		directory = '{}/templates/cisco/asa/firewall/'.format(get_home_directory())
	elif hardware_vendor == 'cisco' and opersys == 'ios'and device_type == 'router':
		directory = '{}/templates/cisco/ios/router'.format(get_home_directory())
	elif hardware_vendor == 'cisco' and opersys == 'ios'and device_type == 'switch':
		directory = '{}/templates/cisco/ios/switch/'.format(get_home_directory())
	elif hardware_vendor == 'cisco' and opersys == 'nxos'and device_type == 'switch':
		directory = '{}/templates/cisco/nxos/switch/'.format(get_home_directory())
	elif hardware_vendor == 'cisco' and opersys == 'nxos'and device_type == 'router':
		directory = '{}/templates/cisco/nxos/router/'.format(get_home_directory())
	elif hardware_vendor == 'juniper' and opersys == 'junos' and device_type == 'vfirewall':
		directory = '{}/templates/juniper/junos/vfirewall/'.format(get_home_directory())
	elif hardware_vendor == 'juniper' and opersys == 'junos' and device_type == 'router':
		directory = '{}/templates/juniper/junos/router/'.format(get_home_directory())
	elif hardware_vendor == 'f5' and opersys == 'tmsh' and device_type == 'loadbalancer':
		directory = '{}/templates/f5/tmsh/ltm/'.format(get_home_directory())

	return directory

def get_policy_directory(hardware_vendor,opersys,device_type):
	directory = ''
	if hardware_vendor == 'cisco' and os == 'ios' and device_type == 'firewall':
		directory = '{}/policy/cisco/ios/firewall/'.format(get_home_directory())
	elif hardware_vendor == 'juniper' and os == 'junos' and device_type == 'vfirewall':
		directory = '{}/policy/juniper/junos/firewall/'.format(get_home_directory())

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
		based on device hardware vendor.
	"""
	syntax = ''
	if node_object[index]['hardware_vendor'] == 'cisco' and node_object[index]['type'] == 'firewall':
		syntax = 'asa'
	elif node_object[index]['hardware_vendor'] == 'cisco' and node_object[index]['type'] == 'switch':
		syntax = 'ios'
	elif node_object[index]['hardware_vendor'] == 'juniper' and node_object[index]['type'] == 'switch':
		syntax = 'junos'
	elif node_object[index]['hardware_vendor'] == 'f5' and node_object[index]['type'] == 'loadbalancer':
		syntax = 'ios'

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

def get_location_directory(name,hardware_vendor,type):
	directory = ''
	datacenter_location = ''
	if type == 'firewall':
		location_list = name.split('-')    
		datacenter_location = location_list[3]
	elif type == 'switch' or type == 'router' or type == 'vfirewall':
		location_list = name.split('.')    
		datacenter_location = location_list[3]

	directory = '{}/templates/{}/common/{}/'.format(get_home_directory(),hardware_vendor,datacenter_location)

	return directory 

def timestamp():
    time_stamp =time.time()
    date_time = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

    return date_time
