# THIS MODULE ALLOWS MODIFICATION TO BE MADE TO THE DATABASE FILE
# APPEND FUNCTION ALLOWS USERS TO ADD DEVICE TO DATABASE WITHOUT MANUALLY OPENING UP THE YAML FILE
# REMOVE FUNCTION DELETES A NODE BY HOSTNAME OR IP FROM THE YAML FILE

from processdb import process_nodes
from snmp import snmp
import yaml
import os

home_directory = os.environ.get('HOME')

def append(args):

	match_node = []
	index = 0
	argument_node = args.ip
	device = snmp(argument_node)
	new_node = yaml.dump(device,default_flow_style = False)
	database = process_nodes()
	# CHECK IF NEW NODE CURRENTLY EXIST IN DATABASE
	for node in database:
		if(device[index]['ip'] == node['ip']):
			match_node.append("MATCH")	
			break
		else:
			continue
	if('MATCH' in match_node):
		print("[x] NODE CURRENTLY EXIST IN DATABASE")
	else:
		with open('{}/database/nodes.yaml'.format(home_directory),'a') as file:
			file.write(new_node)
		database = process_nodes()
		database.sort(key=sorted)
		updated_database = yaml.dump(database,default_flow_style = False)
		with open('{}/database/nodes.yaml'.format(home_directory),'w') as file:
			file.write('---\n')
			file.write(updated_database)
	
		print('[\u2713] SNMP DISCOVERY SUCCESSFUL')
		print('[+] NEW NODE APPENDED TO DATABASE')

def remove(args):

	# RE-USING PREVIOUSLY CODED FUNCTION
	database = process_nodes()
	# TRACK WHICH ELEMENT MATCHES
	index = 0

	for element in database:
		if (element['hostname'] == args.argument) or (element['ip'] == args.argument):
			break

		else:
			index = index + 1
	# DELETES NODES FROM LIST
	database.pop(index)
	# WRITES TO DATABASE FILE
	updated_database = yaml.dump(database,default_flow_style = False)
	with open('{}/database/nodes.yaml'.format(home_directory),'w') as file:
		file.write('---\n')
		file.write(updated_database)
		print('[-] NODE SUCCESSFULLY REMOVED FROM DATABASE')
	

