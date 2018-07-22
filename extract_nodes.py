### THIS MODULE EXTRACTS ALL THE HOSTNAME AND APPENDS THEM TO A LIST
### FOR THE SEARCH MODULE TO QUERY AGAINST.

def extract_nodes(node_object):

	node_list = []
	index = 0

	for node in node_object:

		hostname = node_object[index]['hostname']

		node_list.append(hostname)

		index = index + 1

	return node_list
