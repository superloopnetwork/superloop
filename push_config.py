### THIS MODULE CONTROLS THE PUSHING OF THE TEMPLATES.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_templates
from search import search_node
from search import search_template
from render_config import render_config

def push_config(args):

	ext = '.jinja2'
	template = args.file + ext
	
	### NODE_OBJECT IS A LIST OF ALL THE NODES IN THE DATABASE WITH ALL ATTRIBUTES
	node_object = process_nodes()

	### NODE_TEMPLATE IS A LIST OF ALL THE TEMPLATES BASED ON PLATFORMS AND DEVICE TYPE
	node_template = process_templates()

	### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
	match_node = search_node(args,node_object)

	match_template = search_template(template,match_node,node_template,node_object)
	configs = render_config(template,node_object)

	if(len(match_node) == 0):
		print("+ [NO MATCHING NODES AGAINST DATABASE]")
		print("")

	elif('NO MATCH' in match_template):
		print("+ [NO MATCHING TEMPLATE AGAINST DATABASE]")
		print("")
#		pass	

	else:
		print("THE FOLLOWING CODE WILL BE PUSHED:")
		print("{}".format(configs))
		print("MATCHING NODES:")
		print("{}".format(match_node))
		print("")
#		print("{}".format(match_template))
		print("")
		print("{}".format(node_object))
		print("")
#		print("{}".format(node_template))
		print("")
		proceed = raw_input("PROCEED? [Y/N]: ")
	
		if(proceed == 'y' or proceed == 'Y'):
			print("PUSHING CODE...")
	
		elif(proceed == 'n' or proceed == 'N'):
			print("ABORT...")
	
	#   print("pushing config to host: %s" % args.node)
