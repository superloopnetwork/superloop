### THIS MODULE CONTROLS THE RENDERING OF THE TEMPLATES.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_templates
from search import search_node
from search import search_template 
from render import render
from node_create import node_create
from multithread import multithread_engine
import initialize

def render_config(args):

	ext = '.jinja2'
	auditcreeper = False
	commands = initialize.configuration
	auditcreeper_flag = False 
	output = True
	argument_node = args.node
	with_remediation = False

	if(args.file is None):
#		print("ARGS.FILE IS NONE")
		template_list = []
		auditcreeper_flag = True
	else:
#		print("ARGS.FILE IS VALID")
		template = args.file + ext
		template_list = []
		template_list.append(template)

	### NODE_OBJECT IS A LIST OF ALL THE NODES IN THE DATABASE WITH ALL ATTRIBUTES
	node_object = process_nodes()

	### NODE_TEMPLATE IS A LIST OF ALL THE TEMPLATES BASED ON PLATFORMS AND DEVICE TYPE
	node_template = process_templates()

	### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
	match_node = search_node(argument_node,node_object)

	### MATCH_TEMPLATE IS A LIST OF 'MATCH' AND/OR 'NO MATCH' IT WILL USE THE MATCH_NODE
	### RESULT, RUN IT AGAINST THE NODE_OBJECT AND COMPARES IT WITH NODE_TEMPLATE DATABASE
	### TO SEE IF THERE IS A TEMPLATE FOR THE SPECIFIC PLATFORM AND TYPE.
	match_template = search_template(template_list,match_node,node_template,node_object,auditcreeper_flag)

	### THIS WILL PARSE OUT THE GENERATED CONFIGS FROM THE *.JINJA2 FILE TO A LIST

	if(len(match_node) == 0):
		print("+ [NO MATCHING NODES AGAINST DATABASE]")
		print("")

	elif('NO MATCH' in match_template):
		print("+ [NO MATCHING TEMPLATE AGAINST DATABASE]")
		print("")

	else:
		render(template_list,node_object,auditcreeper_flag,output,with_remediation)
