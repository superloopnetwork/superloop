### THE FUNCTION SEARCH_NODE WILL SEARCH THROUGH THE LIST OF NODES FROM THE USER'S
### QUERY (WHICH CAN SUPPORT REGULAR EXPRESSIONS) AND MATCH A SINGLE OR MULTIPLE NODE

### EXTRACT_NODES FUNCTION WILL EXTRACT ALL THE NODES FROM THE DATABASE OF NODE_OBJECTS SO 
### THAT IT CAN RUN THE SEARCH AGAINST THE LIST OF NODES

### SEARCH_TEMPLATE FUNCTION WILL TAKE THE SEARCH RESULTS FROM THE LIST OF NODES AND RUN IT 
### AGAINST NODE_OBJECT TO DETERMINE THE PLATFORM AND TYPE AND COMPARE WITH THE NODE_TEMPLATE
### DATABASE TO MATCH. ONCE MATCHED, IT WILL CHECK TO VERIFY AN EXISTING TEMPLATE IS AVAILABLE

### SEARCH_POLICY FUNCTION WILL TAKE THE SEARCH RESULTS FROM THE LIST OF NODES AND RUN IT 
### AGAINST NODE_OBJECT TO DETERMINE THE PLATFORM, OS AND TYPE AND COMPARE WITH THE NODE_POLICY
### DATABASE TO MATCH. IF A NODE IS NOT DEEMED AS A FIREWALL, IT WILL 

### NODE_ELEMENT FUNCTION APPENDS THE POSITION INDEX OF THE MATCH RESULTS (MATCH_NODE) AGAINST 
### THE OVERALL NODE_OBJECTS. THIS FUNCTION IS NEEDED TO BE CALLED ONLY WHEN SEARCH_TEMPLATE
### FUNCTION IS NOT USED

import re
import initialize
from processdb import process_json
from get_property import get_template_directory
from get_property import get_policy_directory

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

				### THIS SECTION WILL PULL OUT ALL THE TEMPLATES BELONGING TO THE SPECIFIC PLATFORM, OS AND TYPE OF DEVICE FROM THE TEMPLATE DATABASE
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
							directory = get_template_directory(node_obj['platform'],node_obj['os'],node_obj['type'])
							file = directory + template_list[element]
							if(file in node_temp['templates']):
								search_result.append("MATCH")	
							else:
								print("[!] [NO ASSOCIATING TEMPLATE {}".format(template_list[element]) + " FOR NODE {}]".format(node))
								search_result.append("NO MATCH")
								
					else:
						continue	
			else:
				continue	

#	print("TEMPLATE_LIST IN SEARCH.PY: {}".format(template_list))
	return search_result 

def search_policy(policy_list,match_node,node_policy,node_object,auditcreeper):

	search_result = []
	index = 0
	policy_index = 0
	element = 0
	for node in match_node:
		for node_obj in node_object:
			if(node == node_obj['hostname']):

				### THIS SECTION WILL PULL OUT ALL THE TEMPLATES BELONGING TO THE SPECIFIC PLATFORM, OS AND TYPE OF DEVICE FROM THE TEMPLATE DATABASE
				for node_pol in node_policy:
					if(node == node_pol['hostname']):

						### INDEX GETS THE POSITION IN THE LIST AND APPENDS IT TO THE GLOBAL VARIABLE ELEMENT
						index = node_object.index(node_obj)
						initialize.element.append(index)
						policy_index = node_policy.index(node_pol)
						initialize.element_policy.append(policy_index)
						###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#						print("INDEX: {}".format(initialize.element))
#						print("POLICY_INDEX: {}".format(initialize.element_policy))

						if(auditcreeper):
							policy_node_list = []
							for policy_dir_name in node_pol['policy']:
								policy_name = policy_dir_name.split('/')[-1]
								policy_node_list.append(policy_name)
							policy_list.append(policy_node_list)
							search_result.append("MATCH")	
						else:
							### THIS CALLS THE DIRECTORY MODULE WHICH WILL RETURN THE CORRECT DIRECTORY PATH BASED ON DEVICE PLATFORM, OS AND TYPE
							directory = get_policy_directory(node_pol['platform'],node_obj['os'],node_obj['type'])
							file = directory + policy_list[element]
							if(file in node_pol['policy']):
								###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#								print("NODE: {} NODE_POL['HOSTNAME']: {}".format(node,node_pol['hostname']))
								search_result.append("MATCH")	
							else:
								print("[!] [NO ASSOCIATING POLICY {}".format(policy_list[element]) + " FOR NODE {}]".format(node))
								search_result.append("NO MATCH")
						
					else:
						continue	
			else:
				continue	

#	print("POLICY_LIST IN SEARCH.PY: {}".format(policy_list))
	return search_result 

def node_element(match_node,node_object):

	index = 0

	for node in match_node:
		for node_obj in node_object:
			if(node in node_obj['hostname']):
				index = node_object.index(node_obj)
				initialize.element.append(index)
