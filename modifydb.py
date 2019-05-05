# THIS MODULE ALLOWS MODIFICATION TO BE MADE TO THE DATABASE FILE

import yaml

def append(snmp_data):

	new_node = yaml.dump(snmp_data,default_flow_style = False)
	with open('nodes.yaml','a') as f:
		f.write(new_node)

	print("[+] NEW NODE SUCCESSFULLY APPENDED TO DATABASE")

#def remove(hostname):
#
#	with open('nodes.yaml','a') as f:
#		nodes = yaml.load(f)
#
#	for node in nodes:
#		if nodes['hostname'] == hostname:         
