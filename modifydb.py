"""
	This module allows modification to be made to the database.
"""
import os
from get_property import timestamp
from processdb import process_nodes
from snmp import snmp
import yaml

home_directory = os.environ.get('HOME')

def append(args):
	argument_node = args.argument
	database = process_nodes()
	device = snmp(argument_node)
	index = 0
	match_node = []
	new_node = yaml.dump(device,default_flow_style = False)
	"""
		Check if new node currently exist in database.
	"""
	for node in database:
		if device[index]['ip'] == node['ip']:
			match_node.append('MATCH')	
			break
		else:
			continue
	try:
		if 'MATCH' in match_node:
			print('+ Node currently present in database.')
		else:
			with open('{}/database/nodes.yaml'.format(home_directory),'a') as file:
				file.write(new_node)
			database = process_nodes()
			sorted_database = sortdb(database)
			updated_database = yaml.dump(sorted_database,default_flow_style = False)
			with open('{}/database/nodes.yaml'.format(home_directory),'w') as file:
				file.write('---\n')
				file.write(updated_database)
			print('+ SNMP discovery successful.')
			print('+ New node appended to database.')
	except FileNotFoundError as error:
		print('FileNotFoundError: file cannot be found')
		print(error)

	return None

def remove(args):
	database = process_nodes()
	index = 0
	try:
		for element in database:
			if element['hostname'] == args.argument or element['ip'] == args.argument:
				break
			else:
				index = index + 1
		"""
			Delete node from list.
		"""
		database.pop(index)
		updated_database = yaml.dump(database,default_flow_style = False)
		try:
			with open('{}/database/nodes.yaml'.format(home_directory),'w') as file:
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
	attribute = args.attribute
	amend = args.amend
	database = process_nodes()
	index = 0
	try:
		for element in database:
			if element['hostname'] == args.argument or element['ip'] == args.argument:
				break
			else:
				index = index + 1
		"""
			Identified node from list.
		"""
		try:
			if attribute == 'data':
				return print('+ Attribute \'data\' cannot be modified via host update.')
			else:
				check = str(input('Please confirm you would like to change the value from {} : {} : {} to {} : {} : {}. [y/N]: '.format(database[index]['hostname'],attribute,database[index][attribute],database[index]['hostname'],attribute,amend))) 
				if check[0] == 'y':
					database[index][attribute] = amend
					database[index]['updated_at'] = timestamp()
					database[index]['updated_by'] = '{}'.format(os.environ.get('USER'))
					updated_database = yaml.dump(database,default_flow_style = False)
					try:
						with open('{}/database/nodes.yaml'.format(home_directory),'w') as file:
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
				print('+ Invalid attribute \'{}\' for \'{}\'. Please check node details via \'superloop node list {}\''.format(attribute,database[index]['hostname'],database[index]['hostname']))
	except IndexError as error:
		print('+ Node does not exist in database.')
	
def sortdb(database):
	sorted_database = []
	hostnames = []

	for node in database:
		hostnames.append(node['hostname'])
	hostnames.sort()
	for hostname in hostnames:
		for node in database:
			if hostname == node['hostname']:
				sorted_database.append(node)
			else:
				continue

	return sorted_database 
