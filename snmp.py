"""
	This module fetches information from the device via snmp
"""
from snmp_helper import snmp_get_oid
from snmp_helper import snmp_extract 
from processdb import process_models
import datetime
import re
import subprocess
import socket
import time
import os

def snmp(argument_node):
	index = 0
	SNMP_COMMUNITY_STRING = os.environ.get('SNMP_COMMUNITY_STRING')
	SNMP_PORT = 161
	HOSTNAME_OID = '1.3.6.1.2.1.1.5.0'
	PLATFORM_OID = '1.3.6.1.2.1.1.1.0' 
	SERIAL_OID = {
			'JUNIPER_OID':'1.3.6.1.4.1.2636.3.1.3.0',
			'CISCO_OID':'1.3.6.1.4.1.9.5.1.2.19.0',
			'CISCO_ASA_OID':'1.3.6.1.2.1.47.1.1.1.1.11.1'
		}
	device = (argument_node,SNMP_COMMUNITY_STRING,SNMP_PORT)
	snmp_name = snmp_data(device,HOSTNAME_OID,SNMP_PORT)
	snmp_platform_name = snmp_data(device,PLATFORM_OID,SNMP_PORT)
	mgmt_ip4 = snmp_ip(snmp_name)
	platform_name = snmp_parse_platform_name(snmp_platform_name)
	operating_system = snmp_parse_opersys(platform_name,snmp_name)
	type = snmp_parse_type(platform_name,snmp_name)
	role_name = snmp_parse_role_name(snmp_name)
	SERIAL_NUM_OID = get_serial_oid(platform_name,type,SERIAL_OID)
	serial_num = snmp_data(device,SERIAL_NUM_OID,SNMP_PORT)
	data = [{
		'created_at': '{}'.format(timestamp()),
		'created_by': '{}'.format(os.environ.get('USER')),
		'domain_name': 'null',
		'location_name': 'null',
		'lifecycle_status': 'null',
		'mgmt_con_ip4': 'null',
		'mgmt_ip4': "{}".format(mgmt_ip4),
		'mgmt_oob_ip4': 'null',
		'mgmt_snmp_community4': 'null',
		'name': '{}'.format(snmp_name),
		'opersys':'{}'.format(operating_system),
		'platform_name':'{}'.format(platform_name),
		'role_name':'{}'.format(role_name),
		'serial_num':'{}'.format(serial_num),
		'software_image':'null',
		'software_version':'null',
		'status':'online',
		'type':'{}'.format(type),
		'updated_at':'null',
		'updated_by': 'null'
		}
	]

	return data

def snmp_data(device,oid,port):
	snmp_data = snmp_get_oid(device,oid,display_errors=True)
	snmp_property = snmp_extract(snmp_data)

	return snmp_property

def snmp_ip(snmp_name):
	mgmt_ip4 = socket.gethostbyname(snmp_name)

	return mgmt_ip4

def snmp_parse_platform_name(snmp_platform_name):
	platform_name = snmp_platform_name.split(' ')[0].lower() 
	if platform_name == 'big-ip':
		platform_name = 'f5'
	
	return platform_name

def snmp_parse_opersys(platform_name,snmp_name):
	device_opersys = ''
	operating_systems = {
			'juniper':'junos',
			'cisco':'ios',
			'vyatta':'vyos',
			'f5':'tmsh'
		}
	for vendor in operating_systems:
		if vendor == platform_name and 'fw' in snmp_name:
			device_opersys = 'asa' 
			break
		elif vendor == platform_name:
			device_opersys = operating_systems[vendor]
			break
		else:
			device_opersys = 'invalid'

	return device_opersys

def snmp_parse_type(snmp_platform_name,snmp_name):
	models = {
			'juniper':'vfirewall',
			'cisco':'switch',
			'f5':'loadbalancer'
		}
	for model in models:
		if model == snmp_platform_name and 'fw' in snmp_name:
			device_type = 'firewall'
			break
		elif model in snmp_platform_name:
			device_type = models[model]
			break
		else:
			device_type = 'invalid'

	return device_type

def snmp_parse_role_name(snmp_name):
	device_role_name = ''
	role_names = {
	'fw':'fw',
	'sw':'sw',
	'vsrx':'vsrx',
	'NAS':'NAS',
	'SRV':'SRV'
	}
	for role_name in role_names:
		if role_name in snmp_name:
			device_role_name = role_names[role_name]
			break
		else:
			device_role_name = 'invalid'

	return device_role_name

def get_serial_oid(platform_name,type,SERIAL_OID):
	serial_oid = ''
	if platform_name == 'juniper':
		serial_oid = SERIAL_OID['JUNIPER_OID']
	elif platform_name == 'cisco' and type == 'switch':
		serial_oid = SERIAL_OID['CISCO_OID']
	elif platform_name == 'cisco' and type == 'firewall':
		serial_oid = SERIAL_OID['CISCO_ASA_OID']

	return serial_oid

def timestamp():
	time_stamp =time.time()
	date_time = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

	return date_time
