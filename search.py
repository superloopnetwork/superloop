### THE FUNCTION SEARCH_NODE WILL SEARCH THROUGH THE LIST OF NODES FROM THE USER'S
### QUERY (WHICH CAN SUPPORT REGULAR EXPRESSIONS) AND MATCH A SINGLE OR MULTIPLE NODE

### EXTRACT_NODES WILL EXTRACT ALL THE NODES FROM THE DATABASE OF NODE_OBJECTS SO THAT 
### IT CAN RUN THE SEARCH AGAINST THE LIST OF NODES

### SEARCH_TEMPLATE

import re

def search_node(args,node_object):

	node_list = extract_nodes(node_object)

	query = re.compile(args.node)

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

def search_template(template,match_node,node_template,node_object):

	search_result = []

	for node in match_node:
		for node_obj in node_object:
			if(node in node_obj['hostname']):
				for node_temp in node_template:
					if(node_obj['platform'] == node_temp['platform'] and node_obj['type'] == node_temp['type']):
						if(template in node_temp['templates']):
							search_result.append("MATCH")	
						else:
							print("! [NO ASSOCIATING TEMPLATE {}".format(template) + " FOR NODE {}".format(node))
							search_result.append("NO MATCH")
							
					else:
						continue	
			else:
				continue	

	return search_result 
