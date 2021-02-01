"""
	This module provides ssh session for users.
"""
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
import os

def ssh_connect(args):
	argument_node = args.name
	auditcreeper = False
	commands = initialize.configuration
	username = os.environ.get('USERNAME')
	"""
		:param argument_node: Argument accepted as regular expression.
		:type augument_node: str
		
		:param auditcreeper: When auditcreeper is active/non-active.
		:type auditcreeper: bool
		
		:param commands: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list
		
		:param username: Pulled from environment variable.  
		:type ext: str
	"""
	node_object = process_nodes()
	match_node = search_node(argument_node,node_object)
	"""
		:param node_object: All node(s) in the database with all attributes.
		:type node_object: list

		:param match_node: Nodes that matches the arguements passed in by user.
		:type match_node: list
	"""
	try:
		if len(match_node) == 0:
			print('+ No matching nodes found in database.')
			print('')
		else:
			node_element(match_node,node_object)
			id = 1
			ssh_id = 0
			print('{} {: >27} {: >28} {: >26}'.format('id','name','address','platform'))
			for index in initialize.element:
				print('{id: {align}{space}} {name: {align}{space}} {mgmt_ip4: {align}{space}} {platform_name: {align}{space}}'.format(id = id,name = node_object[index]['name'],mgmt_ip4 = node_object[index]['mgmt_ip4'],platform_name = node_object[index]['hardware_vendor'],align = '<',space = 25))
				id = id + 1
			port = get_port(node_object,initialize.element,ssh_id)
			try:
				if(len(initialize.element) == 1):
			 		subprocess.call('ssh {}@{} -p {}'.format(username,node_object[initialize.element[ssh_id]]['mgmt_ip4'],port), shell=True)
				else:
					try:
						ssh_id = int(input('Enter ID to SSH to: '))
						ssh_id = ssh_id - 1
						if ssh_id + 1 < 1:
							print('IndexError: incorrect connection id')
					except KeyboardInterrupt as error:
						print('')
						print('Terminating...')
					else:
						port = get_port(node_object,initialize.element,ssh_id)
						subprocess.call('ssh {}@{} -p {}'.format(username,node_object[initialize.element[ssh_id]]['mgmt_ip4'],port), shell=True)
			except IndexError:
				print('IndexError: incorrect connection id')
	except ValueError as error:
		print('ValueError: expected an integer')
