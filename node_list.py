"""
	This module displays the attributes of the searched node(s) in 
	dictionary format. 
"""
import initialize
from processdb import process_nodes
from processdb import process_templates
from search import node_element
from search import search_node
from search import search_template
from node_create import node_create
from get_property import get_updated_list

def node_list(args):
	argument_node = args.hostname
	auditcreeper = True
	element_position = 1
	template_list = []
	template_list_copy = template_list
	"""
		:param argument_node: Argument accepted as regular expression.
		:type augument_node: str
		
		:param auditcreeper: When auditcreeper is active/non-active.
		:type auditcreeper: bool
		
		:param element_position: Keeps track of the position.
		:type element_position: int 
		
		:param template_list: Initializing list of templates
		:type template_list: list
		
		:param template_list_copy: Memory reference to template_list
		:type ext: list
		
	"""
	node_object = process_nodes()
	match_node = search_node(argument_node,node_object)
	node_template = process_templates()
	match_template = search_template(template_list,match_node,node_template,node_object,auditcreeper)
	"""
		:param node_object: All node(s) in the database with all attributes.
		:type node_object: list

		:param node_template: All templates based on platforms and device type.
		:type node_template: list

		:param match_node: Nodes that matches the arguements passed in by user.
		:type match_node: list

		:param match_template: Return a list of 'match' and/or 'no match'.
		:type match_template: list 
	"""
	if len(match_node) == 0:
		print('+ No matching node(s) found in database.')
		print('')
	else:
		print('[')
		template_list = template_list_copy[0]
		for index in initialize.element:
			print('    {')
			print("\t\"hostname\": \"{}\"\n" \
				  "\t\"mgmt_ip\": \"{}\"\n" \
				  "\t\"os\": \"{}\"\n" \
				  "\t\"platform\": \"{}\"\n" \
				  "\t\"type\": \"{}\"".format(node_object[index]['hostname'],node_object[index]['ip'],node_object[index]['opersys'],node_object[index]['platform'],node_object[index]['type']) + "\n" \
				  "\t\"data\": {\n" \
				  "\t    \"managed_configs\": {" \
			)
			for template in template_list:
				print ("\t\t   \"{}\"".format(template))
			print('\t     }')
			print('\t }')
			template_list = get_updated_list(template_list_copy)
			if element_position == len(initialize.element):
				print('    }')
			else:
				print('    },')
			element_position = element_position + 1
		print(']')

	return None
