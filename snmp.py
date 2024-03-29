"""
	This module fetches information from the device via snmp
"""
from get_property import get_serial_oid
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
#		'bgp':[snmp_bgp(SNMP_COMMUNITY_STRING,argument_node)][0],
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
#		'ospf':[snmp_ospf(SNMP_COMMUNITY_STRING,argument_node)][0],
		'platform_name':'{}'.format(platform_name),
#		'ports':[snmp_interface(operating_system,argument_node,SNMP_COMMUNITY_STRING,snmp_name)][0],
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
	if snmp_name.lower() == 'netscaler':
		MGMT_IP_ADDRESS_OID = {
				'CITRIX_NETSCALER':'1.3.6.1.4.1.5951.4.1.1.2.0'
			}
		mgmt_ip4 = snmp_data(device,MGMT_IP_ADDRESS_OID['CITRIX_NETSCALER'],port)
	else:
		mgmt_ip4 = socket.gethostbyname(snmp_name)

	return mgmt_ip4

def snmp_parse_platform_name(snmp_platform_name,device,SNMP_PORT):
	PLATFORM_NAME_OID = {
			'CISCO_ASA_OID':'1.3.6.1.2.1.47.1.1.1.1.13.1',
			'CISCO_CATALYST_OID':'1.3.6.1.2.1.47.1.1.1.1.2.1001',
			'NEXUS_OID':'1.3.6.1.2.1.47.1.1.1.1.2.149',
			'CITRIX_NETSCALER':'1.3.6.1.4.1.5951.4.1.1.11.0',
			'PALO_ALTO':'1.3.6.1.2.1.47.1.1.1.1.13.1',
		}
	platform_name = snmp_platform_name.lower() 
	device_platform_name = ''
	platforms = {
			'firefly-perimeter':'firefly-perimeter',
			'c3750':'{}'.format(snmp_data(device,PLATFORM_NAME_OID['CISCO_CATALYST_OID'],SNMP_PORT)),
			'adaptive security appliance':'{}'.format(snmp_data(device,PLATFORM_NAME_OID['CISCO_ASA_OID'],SNMP_PORT)),
            'cisco nx-os':'{}'.format(snmp_data(device,PLATFORM_NAME_OID['NEXUS_OID'],SNMP_PORT)),
			'big-ip':'f5',
			'netscaler':'{}'.format(snmp_data(device,PLATFORM_NAME_OID['CITRIX_NETSCALER'],SNMP_PORT)),
			'nsmpx-8900':'{}'.format(snmp_data(device,PLATFORM_NAME_OID['CITRIX_NETSCALER'],SNMP_PORT)),
			'palo alto':'{}'.format(snmp_data(device,PLATFORM_NAME_OID['PALO_ALTO'],SNMP_PORT))
		}
	for platform in platforms:
		if platform in platform_name:
			device_platform_name = platforms[platform]
			break
		else:
			device_platform_name = 'null'
	
	return device_platform_name

def get_hardware_vendor(snmp_platform_name):
	if 'netscaler' in snmp_platform_name.lower():
		vendor_name = 'citrix'
	elif 'palo alto' in snmp_platform_name.lower():
		vendor_name = 'palo alto'
	else:
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
			'f5':'tmsh',
			'netscaler':'netscaler',
			'palo alto':'pan-os'
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
			'big-ip':'loadbalancer',
			'netscaler':'loadbalancer',
			'cisco nx-os':'switch',
			'palo alto':'firewall',
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
			'c3750':'datacenter-switch',
			'adaptive security appliance':'datacenter-firewall',
			'big-ip':'datacenter-load-balancer',
			'netscaler':'datacenter-load-balancer',
			'palo alto':'datacenter-firewall',
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
			'adaptive security appliance':'1.3.6.1.2.1.47.1.1.1.1.11.1',
			'cisco nx-os':'1.3.6.1.2.1.47.1.1.1.1.11.22',
			'netscaler':'1.3.6.1.4.1.5951.4.1.1.14.0',
			'palo alto':'1.3.6.1.4.1.25461.2.1.2.1.3'
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

"""
	snmp_interface() performs a recursive lookup on OIDs to extract data
	for certain attributes.
"""

def snmp_interface(operating_system,argument_node,SNMP_COMMUNITY_STRING,snmp_name):
	print('+ Discovering switchport interfaces. ')
	interface = []
	arp_table = {}
	interface_admin_status_table = {}
	build_interface_admin_status_table(interface_admin_status_table,operating_system,SNMP_COMMUNITY_STRING,argument_node)
	build_arp_table(arp_table,operating_system,SNMP_COMMUNITY_STRING,argument_node)
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.2.2.1.2'.format(SNMP_COMMUNITY_STRING,argument_node),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	while '' in oids:
		oids.remove('')
		print(oids)
	for index in oids:
		if operating_system == 'asa':
			interface_name = index.split()[6].strip('"')
		else:	
			interface_name = index.split()[3].strip('"')
		admin_status = interface_admin_status_table['{}'.format(interface_name)]
		if interface_name in arp_table.keys():
			ip4 = arp_table['{}'.format(interface_name)]
		else:
			ip4 = 'None'
		interface_data = {
			'access_vlan': 'null',
			'acl4_in': 'null',
			'acl4_out': 'null',
			'admin_status': '{}'.format(admin_status),
			'created_at': '{}'.format(timestamp()),
			'created_by': '{}'.format(os.environ.get('USER')),
			'data': 'null',
			'drain_status': 'none',
			'farend_name': 'null',
			'if_speed': 'null',
			'ip4': '{}'.format(ip4),
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
		print('+ .... {} [complete]'.format(interface_name))

	return interface

def build_arp_table(arp_table,operating_system,SNMP_COMMUNITY_STRING,argument_node):
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
							if operating_system == 'asa':
								interface_name_lookup = index.split()[6].strip('"')
							else:
								interface_name_lookup = index.split()[3].strip('"')
							arp_table['{}'.format(interface_name_lookup)] = '{}'.format(ip4)
							break
					break

	return 'None'

def build_interface_admin_status_table(interface_admin_status_table,operating_system,SNMP_COMMUNITY_STRING,argument_node):
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
					if operating_system == 'asa':
						interface_name_lookup = index.split()[6].strip('"')
					else:
						interface_name_lookup = index.split()[3].strip('"')
					interface_admin_status_table['{}'.format(interface_name_lookup)] = '{}'.format(interface_admin_status)
					break

	return 'None'

"""
	snmp_ospf() performs a recursive lookup on OIDs to extract data
	for certain attributes.
"""

def snmp_ospf(SNMP_COMMUNITY_STRING,argument_node):
	print('+ Discovering OSPF data. ')
	ospf=[]
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.14.10.1.1'.format(SNMP_COMMUNITY_STRING,argument_node),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	for index in oids:
		if '' == index:
			break	
		elif 'No' in index:
			ospf_neighbor_id = '\'None\''
			ospf_data = {
				'neighbor_id': 'null',
				'area': 'null',
				'priority': 'null',
				'state': 'null'
			}
			ospf.append(ospf_data)
		else:
			ospf_neighbor_id = index.split()[3]
			ospf_data = {
				'neighbor_id': '{}'.format(ospf_neighbor_id),
				'area': '{}'.format(snmp_ospf_area(ospf_neighbor_id,SNMP_COMMUNITY_STRING,argument_node)),
				'priority': '{}'.format(snmp_ospf_priority(ospf_neighbor_id,SNMP_COMMUNITY_STRING,argument_node)),
				'state': '{}'.format(snmp_ospf_state(ospf_neighbor_id,SNMP_COMMUNITY_STRING,argument_node))
			}
			ospf.append(ospf_data)
		print('+ .... neighbor {} [complete]'.format(ospf_neighbor_id))

	return ospf 


def snmp_ospf_area(ospf_neighbor_id,SNMP_COMMUNITY_STRING,argument_node):
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.14.2.1.1'.format(SNMP_COMMUNITY_STRING,argument_node),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	while '' in oids:
		oids.remove('')
	for index in oids:
		if '' == index:
			ospf_area = 'null'
		else:
			ospf_area = index.split()[3]

	return ospf_area

def snmp_ospf_priority(ospf_neighbor_id,SNMP_COMMUNITY_STRING,argument_node):
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.14.10.1.5.{}'.format(SNMP_COMMUNITY_STRING,argument_node,ospf_neighbor_id) + '.0',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	while '' in oids:
		oids.remove('')
	for index in oids:
		if '' == index:
			ospf_area = 'null'
		else:
			ospf_priority = index.split()[3]

	return ospf_priority

def snmp_ospf_state(ospf_neighbor_id,SNMP_COMMUNITY_STRING,argument_node):
	ospf_state_index = {
		'1':'Down',
		'2':'Attempt',
		'3':'Init',
		'4':'2Way',
		'5':'ExchangeStart',
		'6':'Exchange',
		'7':'Loading',
		'8':'Full'
	}
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.14.10.1.6.{}'.format(SNMP_COMMUNITY_STRING,argument_node,ospf_neighbor_id) + '.0',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	while '' in oids:
		oids.remove('')
	for index in oids:
		if '' == index:
			return 'null'
		else:
			ospf_state = index.split()[3]

	return ospf_state_index['{}'.format(ospf_state)]

"""
	snmp_bgp() performs a recursive lookup on OIDs to extract data
	for certain attributes.
"""

def snmp_bgp(SNMP_COMMUNITY_STRING,argument_node):
	print('+ Discovering BGP data. ')
	bgp = []
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.15.3.1.7'.format(SNMP_COMMUNITY_STRING,argument_node),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	for index in oids:
		if '' == index:
			break	
		elif 'No' in index:
			bgp_peer = '\'None\''
			bgp_data = {
				'peer': 'null',
				'remote_as': 'null'
			}
			bgp.append(bgp_data)
		else:
			bgp_peer = index.split()[3]
			bgp_data = {
				'peer': '{}'.format(bgp_peer),
				'remote_as': '{}'.format(snmp_bgp_remote_as(bgp_peer,SNMP_COMMUNITY_STRING,argument_node))
			}
			bgp.append(bgp_data)
		print('+ .... peer {} [complete]'.format(bgp_peer))

	return bgp

def snmp_bgp_remote_as(bgp_peer,SNMP_COMMUNITY_STRING,argument_node):
	snmpwalk = subprocess.Popen('snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.15.3.1.9.{}'.format(SNMP_COMMUNITY_STRING,argument_node,bgp_peer),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	oids = snmpwalk.stdout.read()
	oids = oids.decode().split('\n')
	while '' in oids:
		oids.remove('')
	for index in oids:
		if '' == index:
			remote_as = 'null'
		else:
			remote_as = index.split()[3]

	return remote_as
