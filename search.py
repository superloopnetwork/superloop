### THE FUNCTION SEARCH_NODE WILL SEARCH THROUGH THE LIST OF NODES FROM THE USER'S
### QUERY (WHICH CAN SUPPORT REGULAR EXPRESSIONS) AND MATCH A SINGLE OR MULTIPLE NODE

### EXTRACT_NODES WILL EXTRACT ALL THE NODES FROM THE DATABASE OF NODE_OBJECTS SO THAT 
### IT CAN RUN THE SEARCH AGAINST THE LIST OF NODES

### SEARCH_TEMPLATE WILL TAKE THE SEARCH RESULTS FROM THE LIST OF NODES AND RUN IT AGAINST
### NODE_OBJECT TO DETERMINE THE PLATFORM AND TYPE AND COMPARE WITH THE NODE_TEMPLATE
### DATABASE TO MATCH. ONCE MATCHED, IT WILL CHECK TO VERIFY AN EXISTING TEMPLATE IS AVAILABLE

### NODE_ELEMENT APPENDS THE POSITION INDEX OF THE MATCH RESULTS (MATCH_NODE) AGAINST THE OVERALL NODE_OBJECTS

import re
import initialize
from directory import get_directory

def search_node(argument_node,node_object):

	node_list = extract_nodes(node_object)

	query = re.compile(argument_node)

	search_result = list(filter(query.match,node_list))

	return search_result

def extract_nodes(node_object):

    node_list = []
    index = 0

    for node in node_object:

		hostname = node_object[index]['hostname']

		node_list.append(hostname)

		index = index + 1

    return node_list	

def search_template(template_list,match_node,node_template,node_object,auditcreeper):

	search_result = []
	index = 0
	element = 0

	for node in match_node:
		for node_obj in node_object:
			if(node in node_obj['hostname']):

				### INDEX GETS THE POSITION IN THE LIST AND APPENDS IT TO THE GLOBAL VARIABLE ELEMENT
				index = node_object.index(node_obj)
				initialize.element.append(index)

				### TYPE GETS THE TYPE OF DEVICE AND APPENDS IT TO THE GLOBAL VARIABLE TYPE
#				type = node_object[index]['type']
#				initialize.type.append(type)
				for node_temp in node_template:
					if(node_obj['platform'] == node_temp['platform'] and node_obj['os'] == node_temp['os'] and node_obj['type'] == node_temp['type']):

#						print("NODE_TEMP: {}".format(node_temp['templates']))
						if(auditcreeper):
							template_node_list = []
#							print("THIS IS NODE_TEMP['TEMPLATE'] for NODE {}".format(node) + ": {}".format(node_temp['templates'],))
							for template_dir_name in node_temp['templates']:
								template_name = template_dir_name.split('/')[-1]
								template_node_list.append(template_name)
							template_list.append(template_node_list)
#							print("THIS IS THE TEMPLATE_NODE_LIST FOR HOST {} : {}".format(node,template_node_list))
#							print("THIS IS THE TEMPLATE_LIST IN SEARCH.PY : {}".format(template_list))
						else:
							### THIS CALLS THE DIRECTORY MODULE WHICH WILL RETURN THE CORRECT DIRECTORY PATH BASED ON DEVICE PLATFORM, OS AND TYPE
							directory = get_directory(node_obj['platform'],node_obj['os'],node_obj['type'])
							file = directory + template_list[element]
							if(file in node_temp['templates']):
								search_result.append("MATCH")	
							else:
								print("! [NO ASSOCIATING TEMPLATE {}".format(template_list[element]) + " FOR NODE {}]".format(node))
								search_result.append("NO MATCH")
								
					else:
						continue	
			else:
				continue	

#	print("TEMPLATE_LIST IN SEARCH.PY: {}".format(template_list))
	return search_result 

def node_element(match_node,node_object):

	index = 0

	for node in match_node:
		for node_obj in node_object:
			if(node in node_obj['hostname']):
				index = node_object.index(node_obj)
				initialize.element.append(index)
