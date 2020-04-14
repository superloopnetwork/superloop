### THIS MODULE DISPLAYS THE ATTRIBUTES OF THE SEARCHED NODES IN DICTIONARY FORMAT
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from processdb import process_nodes
from processdb import process_templates
from search import node_element
from search import search_node
from search import search_template
from node_create import node_create
from get_property import get_updated_list
import initialize

def node_list(args):

	element_position = 1
	argument_node = args.hostname
	template_list = []
	template_list_copy = template_list
	auditcreeper_flag = True

	### NODE_OBJECT IS A LIST OF ALL THE NODES IN THE DATABASE WITH ALL ATTRIBUTES
	node_object = process_nodes()

	### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
	match_node = search_node(argument_node,node_object)

	### NODE_TEMPLATE IS A LIST OF ALL THE TEMPLATES BASED ON PLATFORMS AND DEVICE TYPE
	node_template = process_templates()
	
	### MATCH_TEMPLATE IS A LIST OF 'MATCH' AND/OR 'NO MATCH' IT WILL USE THE MATCH_NODE
	### RESULT, RUN IT AGAINST THE NODE_OBJECT AND COMPARES IT WITH NODE_TEMPLATE DATABASE
	### TO SEE IF THERE IS A TEMPLATE FOR THE SPECIFIC PLATFORM AND TYPE.
	match_template = search_template(template_list,match_node,node_template,node_object,auditcreeper_flag)
	### THIS WILL PARSE OUT THE GENERATED CONFIGS FROM THE *.JINJA2 FILE TO A LIST

	if(len(match_node) == 0):
		print("[+] [NO MATCHING NODES AGAINST DATABASE]")
		print("")

	else:
		print("[")
		template_list = template_list_copy[0]

		for index in initialize.element:

			print("    {")
			print("\t\"hostname\": \"{}\"\n" \
				  "\t\"os\": \"{}\"\n" \
				  "\t\"platform\": \"{}\"\n" \
				  "\t\"type\": \"{}\"".format(node_object[index]['hostname'],node_object[index]['os'],node_object[index]['platform'],node_object[index]['type'])) + "\n" \
				  "\t\"data\": {\n" \
				  "\t    \"managed_configs\": {" \

			for template in template_list:
				print ("\t\t   \"{}\"".format(template))
			print("\t     }")
			print("\t }")

			template_list = get_updated_list(template_list_copy)

#			if(len(template_list_copy) != 1):
#				template_list_copy.pop(0)
#				template_list = template_list_copy[0]

			if(element_position == len(initialize.element)):
				print("    }")
			else:
				print("    },")

			element_position = element_position + 1
		print("]")
