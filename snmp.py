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
	device = (argument_node,SNMP_COMMUNITY_STRING,SNMP_PORT)
	snmp_name = snmp_data(device,HOSTNAME_OID,SNMP_PORT)
	snmp_platform_name = snmp_data(device,PLATFORM_OID,SNMP_PORT)
	platform_name = snmp_parse_platform_name(snmp_platform_name,device,SNMP_PORT)
	hardware_vendor = get_hardware_vendor(snmp_platform_name)
	mgmt_ip4 = snmp_ip(snmp_name)
	operating_system = snmp_parse_opersys(snmp_platform_name)
	type = snmp_parse_type(snmp_platform_name)
	role_name = snmp_parse_role_name(snmp_platform_name)
	SERIAL_NUM_OID = get_serial_oid(snmp_platform_name)
	serial_num = snmp_data(device,SERIAL_NUM_OID,SNMP_PORT)
	data = [{
		'created_at': '{}'.format(timestamp()),
		'created_by': '{}'.format(os.environ.get('USER')),
		'domain_name': 'null',
		'hardware_vendor':'{}'.format(hardware_vendor),
		'location_name': 'null',
		'lifecycle_status': 'null',
		'mgmt_con_ip4': 'null',
		'mgmt_ip4': "{}".format(mgmt_ip4),
		'mgmt_oob_ip4': 'null',
		'mgmt_snmp_community4': 'null',
		'name': '{}'.format(snmp_name),
		'oncall_team':'network',
		'opersys':'{}'.format(operating_system),
		'platform_name':'{}'.format(platform_name),
		'ports':[snmp_interface(argument_node,SNMP_COMMUNITY_STRING,snmp_name)][0],
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

def snmp_interface(argument_node,SNMP_COMMUNITY_STRING,snmp_name):
	interface = []
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.2.2.1.2'.format(SNMP_COMMUNITY_STRING,argument_node),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	for index in oids:
		if '' == index:
			pass
		else:
			interface_name = index.split()[3].strip('"')
			interface_data = {
				'access_vlan': 'null',
				'acl4_in': 'null',
				'acl4_out': 'null',
				'admin_status': '{}'.format(snmp_interface_admin_status(interface_name,SNMP_COMMUNITY_STRING,argument_node)),
				'created_at': '{}'.format(timestamp()),
				'created_by': '{}'.format(os.environ.get('USER')),
				'data': 'null',
				'drain_status': 'none',
				'farend_name': 'null',
				'if_speed': 'null',
				'ip4': '{}'.format(snmp_interface_ip(interface_name,SNMP_COMMUNITY_STRING,argument_node)),
				'management': 'null',
				'mtu': 'null',
				'name': '{}'.format(interface_name),
				'node_name': '{}'.format(snmp_name),
				'portrole_name': 'null',
				'type': 'null',
				'updated_at': 'null',
				'updated_by': 'null',
				'wan_link': 'null'
			}
			interface.append(interface_data)

	return interface

def snmp_interface_ip(interface_name,SNMP_COMMUNITY_STRING,argument_node):
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.4.20.1.1'.format(SNMP_COMMUNITY_STRING,argument_node),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	for index in oids:
		if '' == index:
			pass
		else:
			ip4 = index.split()[3]
			snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.4.20.1.2.{}'.format(SNMP_COMMUNITY_STRING,argument_node,ip4),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			oids = snmpwalk.stdout.read()
			oids = oids.decode().split('\n')
			for index in oids:
				if '' == index:
					pass
				else:
					interface_index = index.split()[3]
					snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.2.2.1.2.{}'.format(SNMP_COMMUNITY_STRING,argument_node,interface_index),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
					oids = snmpwalk.stdout.read()
					oids = oids.decode().split('\n')
					for index in oids:
						if '' == index:
							pass
						else:
							interface_name_lookup = index.split()[3].strip('"')
							if interface_name.strip('"') == interface_name_lookup:
								return ip4
							else:
								continue

	return 'None'

def snmp_interface_admin_status(interface_name,SNMP_COMMUNITY_STRING,argument_node):
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.2.2.1.7'.format(SNMP_COMMUNITY_STRING,argument_node),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	for index in oids:
		if '' == index:
			pass
		else:
			interface_admin_status_index = index.split()[3]
			if interface_admin_status_index == '1':
				interface_admin_status = 'up'
			else:
				interface_admin_status = 'down'
			oids_split = index.split(' ')
			interface_index = oids_split[0].split('.')[10]
			snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.2.2.1.2.{}'.format(SNMP_COMMUNITY_STRING,argument_node,interface_index),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			oids = snmpwalk.stdout.read()
			oids = oids.decode().split('\n')
			for index in oids:
				if '' == index:
					pass
				else:
					interface_name_lookup = index.split()[3].strip('"')
				if interface_name.strip('"') == interface_name_lookup:
					return interface_admin_status
				else:
					continue

def snmp_data(device,oid,port):
	snmp_data = snmp_get_oid(device,oid,display_errors=True)
	snmp_property = snmp_extract(snmp_data)

	return snmp_property

def snmp_ip(snmp_name):
	mgmt_ip4 = socket.gethostbyname(snmp_name)

	return mgmt_ip4

def snmp_parse_platform_name(snmp_platform_name,device,SNMP_PORT):
	PLATFORM_NAME_OID = {
			'CISCO_ASA_OID':'1.3.6.1.2.1.47.1.1.1.1.13.1',
			'CISCO_CATALYST_OID':'1.3.6.1.2.1.47.1.1.1.1.2.1001'
		}
	platform_name = snmp_platform_name.lower() 
	device_platform_name = ''
	platforms = {
			'firefly-perimeter':'firefly-perimeter',
			'c3750':'{}'.format(snmp_data(device,PLATFORM_NAME_OID['CISCO_CATALYST_OID'],SNMP_PORT)),
			'adaptive security appliance':'{}'.format(snmp_data(device,PLATFORM_NAME_OID['CISCO_ASA_OID'],SNMP_PORT)),
			'big-ip':'f5',
		}
	for platform in platforms:
		if platform in platform_name:
			device_platform_name = platforms[platform]
			break
		else:
			device_platform_name = 'null'
	
	return device_platform_name

def get_hardware_vendor(snmp_platform_name):
	vendor_name = snmp_platform_name.split()[0].lower()
	device_vendor = vendor_name

	return vendor_name

def snmp_parse_opersys(snmp_platform_name):
	platform_name = snmp_platform_name.lower() 
	device_opersys = ''
	operating_systems = {
			'juniper':'junos',
			'ios':'ios',
			'nx-os':'nxos',
			'adaptive security appliance':'asa',
			'vyatta':'vyos',
			'f5':'tmsh'
		}
	for vendor in operating_systems:
		if vendor in platform_name:
			device_opersys = operating_systems[vendor]
			break
		else:
			device_opersys = 'null'

	return device_opersys

def snmp_parse_type(snmp_platform_name):
	platform_name = snmp_platform_name.lower() 
	device_type = ''
	models = {
			'firefly-perimeter':'vfirewall',
			'c3750':'switch',
			'adaptive security appliance':'firewall',
			'big-ip':'load-balancer',
		}
	for model in models:
		if model in platform_name:
			device_type = models[model]
			break
		else:
			device_type = 'null'

	return device_type

def snmp_parse_role_name(snmp_platform_name):
	platform_name = snmp_platform_name.lower() 
	device_role_name = ''
	role_names = {
			'firefly-perimeter':'datacenter-vfirewall',
			'c3750':'datacenter-switch',
			'adaptive security appliance':'datacenter-firewall',
			'big-ip':'datacenter-load-balancer',
		}
	for role_name in role_names:
		if role_name in platform_name:
			device_role_name = role_names[role_name]
			break
		else:
			device_role_name = 'null'

	return device_role_name

def get_serial_oid(snmp_platform_name):
	platform_name = snmp_platform_name.lower() 
	device_serial = ''
	SERIAL_OID = {
			'firefly-perimeter':'1.3.6.1.4.1.2636.3.1.3.0',
			'c3750':'1.3.6.1.4.1.9.5.1.2.19.0',
			'adaptive security appliance':'1.3.6.1.2.1.47.1.1.1.1.11.1'
		}
	for model in SERIAL_OID:
		if model in platform_name:
			device_serial_oid = SERIAL_OID[model]
			break
		else:
			device_serial_oid = 'null'

	return device_serial_oid 

def timestamp():
	time_stamp =time.time()
	date_time = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')

	return date_time
