### THIS MODULE CONSIST OF ALL THE PROPERTIES THAT SUPERLOOP IS REQUIRED TO RETRIEVE

def get_port(node_object,element,ssh_id):

	### THIS FUNCTION GETS THE CORRECT PORTS BASED ON DEVICE TYPE.
	### THIS IS SOLELY FOR MY OWN NETWORK. USERS MAY MODIFY THE PORTS OR COMPLETELY REMOVE THE STATMENTS BELOW
	if(node_object[element[ssh_id]]['type'] == 'switch'):
		port = '22'
	elif(node_object[element[ssh_id]]['type'] == 'nas'):
		port = '2222'
	else:
		port = '22'

	return port

def get_type(hostname):

	### THIS WILL EVALUATE BASED ON HOSTNAME STANDARDS

	if('fw' in hostname):
		device_type = 'firewall'
	elif('rt' in hostname):
		device_type = 'router'
	elif('sw' in hostname):
		device_type = 'switch'

	return device_type


def get_template_directory(platform,os,device_type):

	### THIS WILL RETURN THE CORRESPONDING DIRECTORY FOR THE APPLICATION TO OPEN THE FILE

    if(platform == 'cisco' and os == 'ios' and device_type == 'firewall'):
        directory = '/templates/cisco/ios/firewall/'
    elif(platform == 'cisco' and os == 'ios'and device_type == 'router'):
        directory = '/templates/cisco/ios/router/'
    elif(platform == 'cisco' and os == 'ios'and device_type == 'switch'):
        directory = '/templates/cisco/ios/switch/'
    elif(platform == 'juniper' and os == 'junos' and device_type == 'vfirewall'):
        directory = '/templates/juniper/junos/vfirewall/'

    return directory

def get_policy_directory(platform,os,device_type):

	### THIS WILL RETURN THE CORRESPONDING DIRECTORY FOR THE APPLICATION TO OPEN THE FILE

    if(platform == 'cisco' and os == 'ios' and device_type == 'firewall'):
        directory = '/policy/cisco/ios/firewall/'
    elif(platform == 'juniper' and os == 'junos' and device_type == 'vfirewall'):
        directory = '/policy/juniper/junos/firewall/'

    return directory

def get_updated_list(list_copy):

	### THIS WILL GET THE CURRENT TEMPLATE LIST FROM THE LIST. EXAMPLE: [['base.jinja'],['snmp.jinja','tacacs.jinja']]. 
	### IT WILL CONTINUE TO POP OFF THE 1ST ELEMENT UNTIL THERE ARE ONLY ONE ELEMENT LEFT

	updated_list = []

	if(len(list_copy) != 1):
		list_copy.pop(0)
		updated_list = list_copy[0]

	return updated_list

def get_syntax(node_object,index):

	### THIS WILL RETURN THE CORRECT SYNTAX USED FOR CISCOCONFPARSE BASED ON DEVICE PLATFORM

	if(node_object[index]['platform'] == 'cisco' and node_object[index]['type'] == 'firewall'):
		syntax = 'asa'
	elif(node_object[index]['platform'] == 'cisco' and node_object[index]['type'] == 'switch'):
		syntax = 'ios'
	elif(node_object[index]['platform'] == 'juniper' and node_object[index]['type'] == 'switch'):
		syntax = 'junos'

	return syntax
