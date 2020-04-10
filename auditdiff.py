### THIS MODULE CONTROLS THE PUSHING OF THE TEMPLATES.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_templates
from search import search_node
from search import search_template
from auditdiff_engine import auditdiff_engine
from node_create import node_create
from confirm_push import confirm_push
import initialize

def auditdiff(args):

	redirect = []
	redirect.append('exec_command')
	index = 0
	ext = '.jinja2'
	auditcreeper_flag = False
	output = True
	commands = initialize.configuration	
	argument_node = args.node
	remediation = False 

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
		print("[+] [INVALID MATCHING NODES AGAINST DATABASE]")
		print("")

	elif('NO MATCH' in match_template):
#		print("+ [NO MATCHING TEMPLATE AGAINST DATABASE]")
		print("")

	else:
		node_create(match_node,node_object)
		auditdiff_engine(template_list,node_object,auditcreeper_flag,output,remediation)
#		print ("THESE ARE THE COMMANDS: {}".format(commands))
		if(len(initialize.configuration) == 0):
			pass	

		else:
			if(remediation):
				confirm_push(redirect,commands)
#			multithread_engine(initialize.ntw_device,controller,commands)
			print("")
#			proceed = raw_input("PROCEED TO REMEDIATE? [Y/N]: ")
#
#			if(proceed == 'y' or proceed == 'Y'):
#				print("")
#				print("PUSHING CODE...")
#				multithread_engine(initialize.ntw_device,controller,commands)
#		
#			elif(proceed == 'n' or proceed == 'N'):
#				print("")
#				print("ABORT...")
	
