"""
	This module controls the searching of nodes and templates.
"""
import re
import initialize
from processdb import process_json
from get_property import get_template_directory
from get_property import get_policy_directory
from get_property import get_home_directory

def search_node(argument_node,node_object):
	"""
		The function search_node will search through the list of nodes 
		from the user's query and match a single or multiple node(s).
	"""
	node_list = extract_nodes(node_object)
	query = re.compile(argument_node)
	search_result = list(filter(query.match,node_list))

	return search_result

def extract_nodes(node_object):
	"""
		This function will extract all the nodes from the 
		database of node_objects so that it can run the search against 
		the list of node(s).

	"""
	node_list = []
	index = 0
	for node in node_object:
		name = node_object[index]['name']
		node_list.append(name)
		index = index + 1

	return node_list	

def search_template(template_list,safe_push_list,match_node,node_template,node_object,auditcreeper,push_cfgs):
	"""
		This function will take the search results from the list of nodes 
		and run it against node_object to determine the hardware vendor and type 
		and compare with the node_template database to match. Once matched, 
		it will check to verify an existing template is available.
	"""
	search_result = []
	index = 0
	element = 0
	for node in match_node:
		for node_obj in node_object:
			if node == node_obj['name']:
				"""
					index variable gets the position in the list and appends it to the global variable 'element'.
				"""
				index = node_object.index(node_obj)
				initialize.element.append(index)
				"""
					This section will pull out all the templates belonging to the specific
					hardware vendor, operating system and type from the template database.
				"""
				for node_temp in node_template:
					if node_obj['hardware_vendor'] == node_temp['hardware_vendor'] and node_obj['opersys'] == node_temp['opersys'] and node_obj['type'] == node_temp['type']:
						if auditcreeper:
							template_node_list = []
							for template_dir_name in node_temp['templates']:
								template_name = list(template_dir_name)[0].split('/')[-1]
								template_node_list.append(template_name)
								safe_push = list(template_dir_name.values())[0]
								safe_push_list.append(safe_push)
							if 'disabled' in safe_push_list and push_cfgs:
								run_time = 1
								first_run = True
								disabled_templates = disabled_safe_push_element(safe_push_list,template_node_list,node_obj)
								for index in disabled_templates:
									if first_run:
										template_node_list.pop(index)
										first_run = False
									else:
										template_node_list.pop(index - run_time)
										run_time = run_time + 1
							"""
								If all templates are disabled, exit.
							"""
							if len(template_node_list) == 0:
								exit()
							template_list.append(template_node_list)
							del safe_push_list[:]
						else:
							directory = get_template_directory(node_obj['hardware_vendor'],node_obj['opersys'],node_obj['type'])
							file = directory + template_list[element]
							template_index = 0
							template_node_list = []
							node_templates = node_temp['templates'].copy()
							for template_path in node_temp['templates']:
								template_name = list(template_path)[0].split('/')[-1]
								template_node_list.append(template_name)
								node_temp['templates'][template_index] = list(template_path)[0].replace('~','{}'.format(get_home_directory()))
								safe_push = list(template_path.values())[0]
								safe_push_list.append(safe_push)
								template_index = template_index + 1
							try:
								template_index = template_node_list.index(template_list[element])
								if safe_push_list[template_index] != 'enabled' and push_cfgs:
									print('Template {} has been disabled for {}.'.format(template_node_list[template_index],node_obj['name']))
									exit()
							except Exception as error:
								pass
							if file in node_temp['templates']:
								search_result.append("MATCH")	
								node_temp['templates'] = node_templates.copy()
							else:
								print('+ No associating template {}'.format(template_list[element]) + ' for node {}'.format(node))
								search_result.append("NO MATCH")
								node_temp['templates'] = node_templates.copy()
					else:
						continue	
			else:
				continue	
	return search_result 

def search_policy(policy_list,safe_push_list,match_node,node_policy,node_object,auditcreeper,push_acl):
	"""
		This function will take the search results from the list of nodes 
		and run it against node_object to determine the hardware vendor, operating system and type 
		and compare with the node_policy database to match. If a node is not 
		deemed as a firewall, it will not allow a policy push.
	"""
	search_result = []
	index = 0
	element = 0
	for node in match_node:
		for node_obj in node_object:
			if node == node_obj['name']:
				"""
					index variable gets the position in the list and appends it to the global variable 'element'.
				"""
				index = node_object.index(node_obj)
				initialize.element.append(index)
				"""
					This section will pull out all the policies belonging to the specific
					hardware vendor, operating system and type from the policy database.
				"""
				for node_pol in node_policy:
					if node == node_pol['name']:
	#					policy_index = node_policy.index(node_pol)
	#					initialize.element_policy.append(policy_index)
						if auditcreeper:
							policy_node_list = []
							for policy_dir_name in node_pol['policy']:
								policy_name = list(policy_dir_name)[0].split('/')[-1]
								policy_node_list.append(policy_name)
								safe_push = list(policy_dir_name.values())[0]
								safe_push_list.append(safe_push)
							if 'disabled' in safe_push_list and push_acl:
								run_time = 1
								first_run = True
								disabled_policies = disabled_safe_push_element(safe_push_list,policy_node_list,node_obj)
								for index in disabled_policies:
									if first_run:
										policy_node_list.pop(index)
										first_run = False
									else:
										policy_node_list.pop(index - run_time)
										run_time = run_time + 1
							"""
								If all policies are disabled.
							"""
							if len(policy_node_list) == 0:
								exit()
							policy_list.append(policy_node_list)
							del safe_push_list[:]
						else:
							directory = get_policy_directory(node_obj['hardware_vendor'],node_obj['opersys'],node_obj['type'])
							file = directory + policy_list[element]
							policy_index = 0
							policy_node_list = []
							node_policy = node_pol['policy'].copy()
							for policy_path in node_pol['policy']:
								policy_name = list(policy_path)[0].split('/')[-1]
								policy_node_list.append(policy_name)
								node_pol['policy'][policy_index] = list(policy_path)[0].replace('~','{}'.format(get_home_directory()))
								safe_push = list(policy_path.values())[0]
								safe_push_list.append(safe_push)
								policy_index = policy_index + 1
							try:
								policy_index = policy_node_list.index(policy_list[element])
								if safe_push_list[policy_index] != 'enabled':
									print('Policy {} has been disabled for {}.'.format(policy_node_list[policy_index],node_obj['name']))
									exit()
							except Exception as error:
								pass
							if file in node_pol['policy']:
								search_result.append("MATCH")	
								node_pol['policy'] = node_policy.copy()
							else:
								print('+ No associating policy {}'.format(policy_list[element]) + ' for node {}'.format(node))
								search_result.append("NO MATCH")
								node_pol['policy'] = node_policy.copy()
					else:
						continue	
			else:
				continue	
	return search_result 

def node_element(match_node,node_object):
	"""
		This function appends the position index of the match results (match_node) against 
 		the overall node_objects. This function call is only needed when search_template
 		function is not used.
	"""
	index = 0
	for node in match_node:
		for node_obj in node_object:
			if node == node_obj['name']:
				index = node_object.index(node_obj)
				initialize.element.append(index)

	return None

def disabled_safe_push_element(safe_push_list,template_node_list,node_obj):
	"""
		This function appends the position index of the match results (match_node) against 
 		the overall node_objects. This function call is only needed when search_template
 		function is not used.
	"""
	index = 0
	disabled_templates = []
	for element in safe_push_list:
		if element == 'disabled':
			print('Template {} has been disabled for {}.'.format(template_node_list[index],node_obj['name']))
			disabled_templates.append(index)
		index = index + 1

	return disabled_templates 
