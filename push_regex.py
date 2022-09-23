"""
	This module provides ssh session for users.
"""
from processdb import process_nodes
from search import node_element
from search import search_node

def push_regex(args):
	argument_node = args.regex
	"""
		:param argument_node: Argument accepted as regular expression.
		:type augument_node: str
	"""
	node_object = process_nodes()
	match_node = search_node(argument_node,node_object)
	"""
		:param node_object: All node(s) in the database with all attributes.
		:type node_object: list
		:param match_node: Nodes that matches the arguements passed in by user.
		:type match_node: list
	"""
	if len(match_node) == 0:
		print('+ No matching nodes found in database.')
		print('')
	else:
		print('[>] Affected Nodes:')
		for node in match_node:
			print(node)
