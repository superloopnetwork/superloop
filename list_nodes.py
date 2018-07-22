
def list_nodes(node_object):

	nodes = []
	index = 0

	for element in search_results:

		

		for node in node_object:
	
			hostname = node_object[index]['hostname']
			nodes.append(hostname)
	
			initialize.node_position.append(index)
