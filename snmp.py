# THIS MODULE FETCHES INFORMATION FROM THE DEVICE VIA SNMP

from snmp_helper import snmp_get_oid
from snmp_helper import snmp_extract 
from processdb import process_encrypted
import base64

def snmp(argument_node):

	index = 0
	USERNAME_STRING = base64.b64decode(process_encrypted()[index]['username'])
	PASSWORD_STRING = process_encrypted()[index]['password']
	COMMUNITY_STRING = process_encrypted()[index]['snmp']
	SNMP_PORT = 161

	HOSTNAME_OID = '1.3.6.1.2.1.1.5.0'
	device = (argument_node,base64.b64decode(COMMUNITY_STRING),SNMP_PORT)
	snmp_hostname = snmp_data(device,HOSTNAME_OID,SNMP_PORT)

	data = [{
		'hostname': '{}'.format(snmp_hostname),
		'ip': "{}".format(argument_node),
		'username':'{}'.format(USERNAME_STRING),
		'password': '{}'.format(PASSWORD_STRING),
		'platform':'cisco',
		'os':'ios',
		'type':'ios'
		}
	]

	return data

def snmp_data(device,oid,port):

	snmp_data = snmp_get_oid(device,oid,display_errors=True)
	snmp_hostname = snmp_extract(snmp_data)

	return snmp_hostname 
