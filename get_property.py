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
	directory = ''

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

def get_sorted_juniper_template_list(template_list):

	### THIS WILL SORT THE JUNIPER TEMPLATE LIST FROM TOP CONFIGURATION IN THE ORDER THEY APPEAR IN A 'SHOW CONFIGURATION' JUNIPER OUTPUT
	### FOR EXAMPLE. GROUPS, SYSTEMS, CHASSIS, SECURITY, SNMP ETC....
	
	sorted_juniper_template_list = []
	sorted_juniper_template_list_index = []
	
	config_order = {
					'groups.jinja2': 0 ,
					'system.jinja2': 1 ,
					'interfaces.jinja2': 2,
					'chassis.jinja2': 3 ,
					'snmp.jinja2': 4 ,
					'routing-options.jinja2': 5 ,
					'policy-options.jinja2': 6 ,
					'security.jinja2': 7 ,
					'routing-instances.jinja2': 8
		}			 

	for template in template_list:         
		if(template in config_order.keys()):   
			sorted_juniper_template_list_index.append(config_order[template]) 

	### SORTING THE ORDER OF HOW THE TEMPLATES SHOULD BE IN COMPARISON WITH THE JUNIPER 'SHOW CONFIGURATION' OUTPUT
	sorted_juniper_template_list_index.sort()
#	print("SORTED_JUNIPER_TEMPLATE_LIST: {}".format(sorted_juniper_template_list_index))

	### BUILDING THE SORTED TEMPLATE LIST AND RETURNING IT
	for element in sorted_juniper_template_list_index:

		template = list(config_order.keys())[list(config_order.values()).index(element)]
		sorted_juniper_template_list.append(template)

#	print("SORTED_JUNIPER_TEMPLATE_LIST: {}".format(sorted_juniper_template_list))

	return sorted_juniper_template_list
