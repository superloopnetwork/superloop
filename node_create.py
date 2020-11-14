"""
	This module controls the creation of objects from the database.
"""
import initialize
from lib.objects.basenode import BaseNode 

def node_create(match_node,node_object):
	node_list = []
	for index in initialize.element:
		node = BaseNode(node_object[index]['ip'],node_object[index]['hostname'],node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'])
		initialize.ntw_device.append(node)

	return None
