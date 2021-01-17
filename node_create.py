"""
	This module controls the creation of objects from the database.
"""
import initialize
from lib.objects.basenode import BaseNode 

def node_create(match_node,node_object):
	node_list = []
	for index in initialize.element:
		node = BaseNode(node_object[index]['created_at'],node_object[index]['created_by'],node_object[index]['ip'],node_object[index]['hostname'],node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'],node_object[index]['role'])
		initialize.ntw_device.append(node)

	return None
