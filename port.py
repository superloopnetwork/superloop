
def get_port(node_object,element,ssh_id):

	### THIS IS SOLELY FOR MY OWN NETWORK. USERS MAY MODIFY THE PORTS OR COMPLETELY REMOVE THE STATMENTS BELOW
	if(node_object[element[ssh_id]]['type'] == 'switch'):
		port = '65500'
	else:
		port = '22'

	return port
