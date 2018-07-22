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

#def search_template(args,match_node,node_template,node_object):
#
#	index = 0
#	file_ext = '.jinja2'
#
#	template = args.file + file_ext
#
#	for template in node_template:

		

