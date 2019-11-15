### THIS MODULE CONSIST OF ALL THE PROPERTIES THAT SUPERLOOP IS REQUIRED TO RETRIEVE

def get_port(node_object,element,ssh_id):

	### THIS FUNCTION GETS THE CORRECT PORTS BASED ON DEVICE TYPE.
	### THIS IS SOLELY FOR MY OWN NETWORK. USERS MAY MODIFY THE PORTS OR COMPLETELY REMOVE THE STATMENTS BELOW
	if(node_object[element[ssh_id]]['type'] == 'switch'):
		port = '65500'
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


def get_directory(platform,os,device_type):

	### THIS WILL RETURN THE CORRESPONDING DIRECTORY FOR THE APPLICATION TO OPEN THE FILE

    if(platform == 'cisco' and os == 'ios' and device_type == 'firewall'):
        directory = '/templates/cisco/ios/firewall/'
    elif(platform == 'cisco' and os == 'ios'and device_type == 'router'):
        directory = '/templates/cisco/ios/router/'
    elif(platform == 'cisco' and os == 'ios'and device_type == 'switch'):
        directory = '/templates/cisco/ios/switch/'

    return directory

def get_template(template_list_copy):

	### THIS WILL GET THE CURRENT TEMPLATE LIST FROM THE LIST. EXAMPLE: [['base.jinja'],['snmp.jinja','tacacs.jinja']]. 
	### IT WILL CONTINUE TO POP OFF THE 1ST ELEMENT UNTIL THERE ARE ONLY ONE ELEMENT LEFT

	template_list = []

	if(len(template_list_copy) != 1):
		template_list_copy.pop(0)
		template_list = template_list_copy[0]

	return template_list

def get_syntax(node_object,index):

	### THIS WILL RETURN THE CORRECT SYNTAX USED FOR CISCOCONFPARSE BASED ON DEVICE PLATFORM

	if(node_object[index]['platform'] == 'cisco' and node_object[index]['type'] == 'firewall'):
		syntax = 'asa'
	elif(node_object[index]['platform'] == 'cisco' and node_object[index]['type'] == 'switch'):
		syntax = 'ios'

	return syntax
