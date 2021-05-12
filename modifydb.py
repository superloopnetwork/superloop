"""
	This module allows modification to be made to the database.
"""
from get_property import get_home_directory 
from get_property import timestamp
from processdb import process_nodes
from snmp import snmp
import os
import socket
import yaml

def append(args):
	argument_node = args.node
	database = process_nodes()
	index = 0
	match_node = []
	mgmt_ip4 = socket.gethostbyname(argument_node)
	try:
		"""
			Check if new node currently exist in database.
		"""
		for node in database:
			if mgmt_ip4 == node['mgmt_ip4']:
				match_node.append('MATCH')
				break
			else:
				continue
		try:
			if 'MATCH' in match_node:
				print('+ Node currently present in database.')
			else:
				device = snmp(argument_node)
				new_node = yaml.dump(device,default_flow_style = False)
				with open('{}/database/nodes.yaml'.format(get_home_directory()),'a') as file:
					file.write(new_node)
				database = process_nodes()
				sorted_database = sortdb(database)
				updated_database = yaml.dump(sorted_database,default_flow_style = False)
				with open('{}/database/nodes.yaml'.format(get_home_directory()),'w') as file:
					file.write('---\n')
					file.write(updated_database)
				print('+ SNMP discovery successful.')
				print('+ New node appended to database.')
		except FileNotFoundError as error:
			print('FileNotFoundError: file cannot be found')
			print(error)
	except Exception as error:
		print('SNMP query timeout. Please ensure that FQDN or IP address is reachable via SNMP.')

	return None

def remove(args):
	database = process_nodes()
	index = 0
	try:
		for element in database:
			if element['name'] == args.node or element['mgmt_ip4'] == args.node:
				break
			else:
				index = index + 1
		"""
			Delete node from list.
		"""
		database.pop(index)
		updated_database = yaml.dump(database,default_flow_style = False)
		try:
			with open('{}/database/nodes.yaml'.format(get_home_directory()),'w') as file:
				file.write('---\n')
				file.write(updated_database)
				print('- Node successfully removed from database.')
		except FileNotFoundError as error:
			print("FileNotFoundError: file cannot be found")
			print(error)
	except IndexError as error:
		print('+ Node does not exist in database.')
	
	return None

def update(args):
	argument_node = args.node
	argument_attribute = args.attribute
	argument_amend = args.amend
	database = process_nodes()
	index = 0
	try:
		for element in database:
			if element['name'] == argument_node or element['mgmt_ip4'] == argument_node:
				break
			else:
				index = index + 1
		"""
			Identified node from list.
		"""
		try:
			if argument_attribute == 'data':
				return print('+ Attribute \'data\' cannot be modified via host update.')
			else:
				check = str(input('Please confirm you would like to change the value from {} : {} : {} to {} : {} : {}. [y/N]: '.format(database[index]['name'],argument_attribute,database[index][argument_attribute],database[index]['name'],argument_attribute,argument_amend))) 
				if check[0] == 'y':
					database[index][argument_attribute] = argument_amend
					database[index]['updated_at'] = timestamp()
					database[index]['updated_by'] = '{}'.format(os.environ.get('USER'))
					updated_database = yaml.dump(database,default_flow_style = False)
					try:
						with open('{}/database/nodes.yaml'.format(get_home_directory()),'w') as file:
							file.write('---\n')
							file.write(updated_database)
							print('+ Amendment to database was successful.')
					except FileNotFoundError as error:
						print("FileNotFoundError: file cannot be found")
						print(error)
				elif check[0] == 'N':
					return False
				else:
					print("RuntimeError: aborted at user request")
		except Exception as error:
				print('+ Invalid attribute \'{}\' for \'{}\'. Please check node details via \'superloop node list {}\''.format(argument_attribute,database[index]['name'],database[index]['name']))
	except IndexError as error:
		print('+ Node does not exist in database.')	

def discover(args):
	argument_node = args.node
	database = process_nodes()
	index = 0
#	try:
	for element in database:
		if element['name'] == argument_node or element['mgmt_ip4'] == argument_node:
			break
		else:
			index = index + 1
	"""
		Identified node from list.
	"""
#		try:
	device = snmp(argument_node)
#		except Exception as error:
#			print('SNMP query timeout. Please ensure that FQDN or IP address is reachable via SNMP.')
	for attribute in database[index]:
		if 'created_at' == attribute or 'created_by' == attribute:
			continue
		else:
			database[index][attribute] = device[0][attribute]
	database[index]['updated_at'] = timestamp()
	database[index]['updated_by'] = '{}'.format(os.environ.get('USER'))
	updated_database = yaml.dump(database,default_flow_style = False)
	with open('{}/database/nodes.yaml'.format(get_home_directory()),'w') as file:
		file.write('---\n')
		file.write(updated_database)
	print('+ SNMP discovery successful.')
#	except IndexError as error:
#		print('+ Node does not exist in database.')

def sortdb(database):
	sorted_database = []
	names = []

	for node in database:
		names.append(node['name'])
	names.sort()
	for name in names:
		for node in database:
			if name == node['name']:
				sorted_database.append(node)
			else:
				continue

	return sorted_database 
