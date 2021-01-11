"""
	This module allows modification to be made to the database.
"""
import os
from processdb import process_nodes
from snmp import snmp
import yaml

home_directory = os.environ.get('HOME')

def append(args):
	argument_node = args.ip
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
			database.sort(key=sorted)
			updated_database = yaml.dump(database,default_flow_style = False)
			with open('{}/database/nodes.yaml'.format(home_directory),'w') as file:
				file.write('---\n')
				file.write(updated_database)
		
			print('\u2713 SNMP discovery successful.')
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
