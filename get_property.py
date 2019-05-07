# THIS FUNCTION GETS THE CORRECT PORTS BASED ON DEVICE TYPE.

def get_port(node_object,element,ssh_id):

	### THIS IS SOLELY FOR MY OWN NETWORK. USERS MAY MODIFY THE PORTS OR COMPLETELY REMOVE THE STATMENTS BELOW
	if(node_object[element[ssh_id]]['type'] == 'switch'):
		port = '65500'
	else:
		port = '22'

	return port

def get_type(hostname):

	### THIS WILL EVALUATE BASED ON HOSTNAME STANDARDS

	if 'fw' in hostname:
		device_type = 'firewall'
	elif 'rt' in hostname:
		device_type = 'router'
	elif 'sw' in hostname:
		device_type = 'switch'

	return device_type
