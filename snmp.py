# THIS MODULE FETCHES INFORMATION FROM THE DEVICE VIA SNMP
# SNMP_PARSE_OS WILL POPULATE THE OS NAME BASED ON IT'S PLATFORM VIA SNMP

from snmp_helper import snmp_get_oid
from snmp_helper import snmp_extract 
from processdb import process_encrypted
from processdb import process_models
import re
import pybase64
import subprocess

def snmp(argument_node):

	USERNAME_STRING = pybase64.b64decode(process_encrypted()['username'])
	PASSWORD_STRING = process_encrypted()['password']
	COMMUNITY_STRING = process_encrypted()['snmp']
	SNMP_PORT = 161

	HOSTNAME_OID = '1.3.6.1.2.1.1.5.0'
	PLATFORM_OID = '1.3.6.1.2.1.1.1.0' 
	device = (argument_node,pybase64.b64decode(COMMUNITY_STRING),SNMP_PORT)
	snmp_hostname = snmp_data(device,HOSTNAME_OID,SNMP_PORT)
	snmp_platform = snmp_data(device,PLATFORM_OID,SNMP_PORT)

	platform = snmp_parse_platform(snmp_platform)
	operating_system = snmp_parse_os(platform)
	type = snmp_parse_type(snmp_platform)

	data = [{
		'hostname': '{}'.format(snmp_hostname),
		'ip': "{}".format(argument_node),
		'username':'{}'.format(USERNAME_STRING),
		'password': '{}'.format(PASSWORD_STRING),
		'platform':'{}'.format(platform),
		'os':'{}'.format(operating_system),
		'type':'{}'.format(type)
		}
	]

	return data

def snmp_data(device,oid,port):

	snmp_data = snmp_get_oid(device,oid,display_errors=True)
	snmp_property = snmp_extract(snmp_data)

	return snmp_property

def snmp_parse_platform(snmp_platform):

	platform = snmp_platform.split(' ')[0].lower() 

	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print("SNMP_PLATFORM: {}".format(platform))
	
	return platform

def snmp_parse_os(platform):

	os = ''

	if(platform == 'cisco'):
		os = 'nxos'
	elif(platform == 'juniper'):
		os = 'junos'
	elif(platform == 'vyatta'):
		os = 'vyos'
	elif(platform == 'big-ip'):
		os = 'bigip'

	return os

def snmp_parse_type(snmp_platform):

    snmp_platform = snmp_platform.lower()
    models = process_models()
    models_list = models.keys()

    for model in models_list:
        if(model in snmp_platform):
            device_type = models[model]
            break
        else:
            device_type = 'invalid'

    return device_type
