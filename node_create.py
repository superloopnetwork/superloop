"""
	This module controls the creation of objects from the database.
"""
import initialize
from lib.objects.basenode import BaseNode 

def node_create(match_node,node_object):
	node_list = []
	for index in initialize.element:
		node = BaseNode(
			node_object[index]['created_at'],
			node_object[index]['created_by'],
			node_object[index]['domain_name'],
			node_object[index]['lifecycle_status'],
			node_object[index]['location_name'],
			node_object[index]['mgmt_ip4'],
			node_object[index]['mgmt_con_ip4'],
			node_object[index]['mgmt_oob_ip4'],
			node_object[index]['mgmt_snmp_community4'],
			node_object[index]['name'],
			node_object[index]['opersys'],
			node_object[index]['platform_name'],
			node_object[index]['serial_num'],
			node_object[index]['software_image'],
			node_object[index]['software_version'],
			node_object[index]['status'],
			node_object[index]['type'],
			node_object[index]['role_name'],
			node_object[index]['updated_at'],
			node_object[index]['updated_by']
		)
		initialize.ntw_device.append(node)

	return None
