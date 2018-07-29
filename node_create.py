### THIS MODULE CREATES THE NODE FROM RECEIVED FROM THE YAML FILE
### IN THE FORM OF A LIST AND PROCESSES EACH ELEMENT AS AN OBJECT

from lib.objects.basenode import BaseNode 
import initialize

def node_create(match_node,node_object):

	node_list = []

	for index in initialize.element:
	
		node = BaseNode(node_object[index]['ip'],node_object[index]['hostname'],node_object[index]['username'],node_object[index]['password'],node_object[index]['platform'],node_object[index]['type'])
	
		initialize.ntw_device.append(node)
