"""
	This module controls the creation of objects from the database.
"""
import initialize
from lib.objects.basenode import BaseNode 

def node_create(match_node,node_object):
	node_list = []
	for index in initialize.element:
		node = BaseNode(node_object[index]['created_at'],node_object[index]['created_by'],node_object[index]['ip'],node_object[index]['name'],node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'],node_object[index]['role'],node_object[index]['serial_num'],node_object[index]['status'],node_object[index]['updated_at'],node_object[index]['updated_by'])
		initialize.ntw_device.append(node)

	return None
