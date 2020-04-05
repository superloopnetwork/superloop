### THIS MODULE ALLOWS THE SSH SESSION FOR USERS.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.

from lib.objects.basenode import BaseNode
from processdb import process_nodes
from processdb import process_templates
from search import node_element
from search import search_node
from search import search_template 
from node_create import node_create
from multithread import multithread_engine
from get_property import get_port
import initialize
import subprocess

def ssh_connect(args):

	auditcreeper = False
	commands = initialize.configuration
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
		id = 1
		ssh_id = 0

		print("ID\tname\t\t\taddress\t\tplatform")

		for index in initialize.element:

			print("{}\t{}\t{}\t{}".format(id,node_object[index]['hostname'],node_object[index]['ip'],node_object[index]['platform']))
			id = id + 1

		port = get_port(node_object,initialize.element,ssh_id)

		if(len(initialize.element) == 1):
			subprocess.call("ssh admin@{} -p {}".format(node_object[initialize.element[ssh_id]]['ip'],port), shell=True)

		else:
			ssh_id = int(raw_input("Enter ID to SSH to: "))

			### NODE_ID WILL MAP TO THE CORRECT NODE_OBJECT HOST TO CONNECT TO.
			ssh_id = ssh_id - 1

			port = get_port(node_object,initialize.element,ssh_id)
			subprocess.call("ssh admin@{} -p {}".format(node_object[initialize.element[ssh_id]]['ip'],port), shell=True)
