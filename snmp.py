"""
	This module fetches information from the device via snmp
"""
from snmp_helper import snmp_get_oid
from snmp_helper import snmp_extract 
from processdb import process_models
import re
import subprocess
import socket
import os

def snmp(argument_node):
	index = 0
	SNMP_COMMUNITY_STRING = os.environ.get('SNMP_COMMUNITY_STRING')
	SNMP_PORT = 161
	HOSTNAME_OID = '1.3.6.1.2.1.1.5.0'
	PLATFORM_OID = '1.3.6.1.2.1.1.1.0' 
	device = (argument_node,SNMP_COMMUNITY_STRING,SNMP_PORT)
	snmp_hostname = snmp_data(device,HOSTNAME_OID,SNMP_PORT)
	snmp_platform = snmp_data(device,PLATFORM_OID,SNMP_PORT)
	ip = snmp_ip(snmp_hostname)
	platform = snmp_parse_platform(snmp_platform)
	operating_system = snmp_parse_opersys(platform)
	type = snmp_parse_type(snmp_platform)
	role = snmp_parse_role(snmp_hostname)
	data = [{
		'hostname': '{}'.format(snmp_hostname),
		'ip': "{}".format(ip),
		'platform':'{}'.format(platform),
		'opersys':'{}'.format(operating_system),
		'type':'{}'.format(type),
		'role':'{}'.format(role)
		}
	]

	return data

def snmp_data(device,oid,port):
	snmp_data = snmp_get_oid(device,oid,display_errors=True)
	snmp_property = snmp_extract(snmp_data)

	return snmp_property

def snmp_ip(snmp_hostname):
	ip = socket.gethostbyname(snmp_hostname)

	return ip

def snmp_parse_platform(snmp_platform):
	platform = snmp_platform.split(' ')[0].lower() 
	if platform == 'big-ip':
		platform = 'f5'
	
	return platform

def snmp_parse_opersys(platform):
	opersys = ''

	if platform == 'cisco':
		opersys = 'ios'
	elif platform == 'juniper':
		opersys = 'junos'
	elif platform == 'vyatta':
		opersys = 'vyos'
	elif(platform == 'f5'):
		opersys = 'tmsh'

	return opersys

def snmp_parse_type(snmp_platform):
    snmp_platform = snmp_platform.lower()
    models = process_models()
    models_list = models.keys()

    for model in models_list:
        if model in snmp_platform:
            device_type = models[model]
            break
        else:
            device_type = 'invalid'

    return device_type

def snmp_parse_role(snmp_hostname):
	if 'fw' in snmp_hostname:
		role = 'fw'
	elif 'rt' in snmp_hostname:
		role = 'rt'
	elif 'sw' in snmp_hostname:
		role = 'sw'
	elif 'SRV' in snmp_hostname:
		role = 'server'
	elif 'NAS' in snmp_hostname:
		role = 'storage'

	return role
