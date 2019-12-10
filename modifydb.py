# THIS MODULE ALLOWS MODIFICATION TO BE MADE TO THE DATABASE FILE
# APPEND FUNCTION ALLOWS USERS TO ADD DEVICE TO DATABASE WITHOUT MANUALLY OPENING UP THE YAML FILE
# REMOVE FUNCTION DELETES A NODE BY HOSTNAME OR IP FROM THE YAML FILE

from processdb import process_nodes
from snmp import snmp
import yaml

def append(args):

	argument_node = args.ip
	device = snmp(argument_node)
	new_node = yaml.dump(device,default_flow_style = False)
	with open('/database/nodes.yaml','a') as f:
		f.write(new_node)

	database = process_nodes()
	database.sort()
	updated_database = yaml.dump(database,default_flow_style = False)
	with open('/database/nodes.yaml','w') as f:
		f.write(updated_database)

	print("[+] NEW NODE SUCCESSFULLY APPENDED TO DATABASE")

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
	with open('/database/nodes.yaml','w') as f:
		f.write(updated_database)
		print("[-] NODE SUCCESSFULLY REMOVED FROM DATABASE")
	

