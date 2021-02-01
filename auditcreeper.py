"""
	This module executes auditcreeper, a continous auditing and remediating cycle.
"""
from processdb import process_nodes
from processdb import process_templates
from search import search_node
from search import search_template
from mediator import mediator
from node_create import node_create
from multithread import multithread_engine
import threading
import os
import initialize

def auditcreeper():
	argument_node = '.+'
	auditcreeper = True
	commands = initialize.configuration
	output = True 
	redirect = []
	template_list = []
	with_remediation = True
	"""
		:param argument_node: Argument accepted as regular expression.
		:type augument_node: str
		
		:param auditcreeper: When auditcreeper is active/non-active.
		:type auditcreeper: bool
		
		:param commands: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list
		
		:param output: Flag to output to stdout.  
		:type ext: bool 

		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list
		
		:param template_list_original: Take a duplicate copy of template_list
		:type template_list_original: list
		
		:param with_remediation: Current function to remediate or not remediate.  
		:type ext: bool 
	"""
	initialize.variables()
	redirect.append('push_cfgs') 
	os.system('clear')
	node_object = process_nodes()
	node_template = process_templates()
	match_node = search_node(argument_node,node_object)
	match_template = search_template(template_list,match_node,node_template,node_object,auditcreeper)
	"""
		:param node_object: All node(s) in the database with all attributes.
		:type node_object: list

		:param node_template: All templates based on hardware_vendor and device type.
		:type node_template: list

		:param match_node: Nodes that matches the arguements passed in by user.
		:type match_node: list

		:param match_template: Return a list of 'match' and/or 'no match'.
		:type match_template: list 
	"""
	node_create(match_node,node_object)
	mediator(template_list,node_object,auditcreeper,output,with_remediation)
	for index in initialize.element:
		redirect.append('push_cfgs')
	multithread_engine(initialize.ntw_device,redirect,commands)
	threading.Timer(5.0, auditcreeper).start()

if __name__ == "__main__":
	auditcreeper()
