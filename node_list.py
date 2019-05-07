### THIS MODULE DISPLAYS THE ATTRIBUTES OF THE SEARCHED NODES IN DICTIONARY FORMAT
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from processdb import process_nodes
from processdb import process_templates
from search import node_element
from search import search_node
from node_create import node_create
import initialize

def node_list(args):

	argument_node = args.hostname
	
	### NODE_OBJECT IS A LIST OF ALL THE NODES IN THE DATABASE WITH ALL ATTRIBUTES
	node_object = process_nodes()

	### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
	match_node = search_node(argument_node,node_object)

	if(len(match_node) == 0):
		print("[+] [NO MATCHING NODES AGAINST DATABASE]")
		print("")

	else:
		node_element(match_node,node_object)

		for index in initialize.element:

			print("[")
			print("    {")
			print("\thostname: {}\n" \
				  "\tos: {}\n" \
				  "\tplatform: {}\n" \
				  "\ttype: {}".format(node_object[index]['hostname'],node_object[index]['os'],node_object[index]['platform'],node_object[index]['type'])) 
			print("    }")
			print("]")
