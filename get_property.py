"""
	This module holds properties that superloop is required to retrieve.
"""
import datetime
import hvac
import os
import socket
import time

def get_home_directory():
	home_directory = os.getenv('HOME')

	return home_directory

def get_real_path():
	real_path = os.path.dirname(os.path.realpath(__file__))

	return real_path

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
		directory = '{}/superloop_code/templates/hardware_vendors/cisco/asa/firewall/'.format(get_home_directory())
	elif hardware_vendor == 'cisco' and opersys == 'ios'and device_type == 'router':
		directory = '{}/superloop_code/templates/hardware_vendors/cisco/ios/router'.format(get_home_directory())
	elif hardware_vendor == 'cisco' and opersys == 'ios'and device_type == 'switch':
		directory = '{}/superloop_code/templates/hardware_vendors/cisco/ios/switch/'.format(get_home_directory())
	elif hardware_vendor == 'cisco' and opersys == 'nxos'and device_type == 'switch':
		directory = '{}/superloop_code/templates/hardware_vendors/cisco/nxos/switch/'.format(get_home_directory())
	elif hardware_vendor == 'cisco' and opersys == 'nxos'and device_type == 'router':
		directory = '{}/superloop_code/templates/hardware_vendors/cisco/nxos/router/'.format(get_home_directory())
	elif hardware_vendor == 'juniper' and opersys == 'junos' and device_type == 'vfirewall':
		directory = '{}/superloop_code/templates/hardware_vendors/juniper/junos/vfirewall/'.format(get_home_directory())
	elif hardware_vendor == 'juniper' and opersys == 'junos' and device_type == 'router':
		directory = '{}/superloop_code/templates/hardware_vendors/juniper/junos/router/'.format(get_home_directory())
	elif hardware_vendor == 'citrix' and opersys == 'netscaler' and device_type == 'loadbalancer':
		directory = '{}/superloop_code/templates/hardware_vendors/citrix/netscaler/vpx/'.format(get_home_directory())
	elif hardware_vendor == 'f5' and opersys == 'tmsh' and device_type == 'loadbalancer':
		directory = '{}/superloop_code/templates/hardware_vendors/f5/tmsh/ltm/'.format(get_home_directory())

	return directory

def get_policy_directory(hardware_vendor,opersys,device_type):
	directory = ''
	if hardware_vendor == 'cisco' and opersys == 'asa' and device_type == 'firewall':
		directory = '{}/superloop_code/policy/cisco/ios/firewall/'.format(get_home_directory())
	elif hardware_vendor == 'juniper' and opersys == 'junos' and device_type == 'vfirewall':
		directory = '{}/superloop_code/policy/juniper/junos/firewall/'.format(get_home_directory())

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

def get_standards_directory(name,hardware_vendor,type):
	directory = '{}/superloop_code/templates/standards/'.format(get_home_directory())

	return directory 

def timestamp():
    time_stamp =time.time()
    date_time = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

    return date_time

def get_resolve_hostname(fqdn):
	try:
		mgmt_ip4 = socket.gethostbyname(fqdn)

		return mgmt_ip4

	except socket.error:
		mgmt_ip4 = 'null'

	return mgmt_ip4


def get_serial_oid(snmp_platform_name):
	platform_name = snmp_platform_name.lower() 
	device_serial = ''
	SERIAL_OID = {
			'firefly-perimeter':'1.3.6.1.4.1.2636.3.1.3.0',
			'c3750':'1.3.6.1.4.1.9.5.1.2.19.0',
			'adaptive security appliance':'1.3.6.1.2.1.47.1.1.1.1.11.1',
			'cisco nx-os':'1.3.6.1.2.1.47.1.1.1.1.11.22',
			'netscaler':'1.3.6.1.4.1.5951.4.1.1.14.0'
		}
	for model in SERIAL_OID:
		if model in platform_name:
			device_serial_oid = SERIAL_OID[model]
			break
		else:
			device_serial_oid = 'null'

	return device_serial_oid 

def get_secrets():
	client = hvac.Client()
	data = client.auth.approle.login(
			role_id = os.environ.get('VAULT_ROLE_ID'),
			secret_id = os.environ.get('VAULT_SECRET_ID')
		)
	VAULT_TOKEN = data['auth']['client_token']
	secret_data = client.read('{}'.format(os.environ.get('VAULT_PATH')))
	secrets = secret_data['data']['data']

	return secrets
