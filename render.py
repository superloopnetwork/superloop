### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
### AND PACKAGES THEM INTO A LIST OF LISTS. THIS IS STORED IN THE 
### GLOBAL VARIABLE CALL INITIALIZE.CONFIGURATION.

from jinja2 import Environment, FileSystemLoader
import initialize
import re

def render(template,node_object,flag):

	for device_type in initialize.type:

		if(device_type == 'firewall'):
			directory = '/templates/cisco/ios/firewall/'

		if(device_type == 'router'):
			directory = '/templates/cisco/ios/router/'

		if(device_type == 'switch'):
			directory = '/templates/cisco/ios/switch/'

		print initialize.type
		print directory + template
		env = Environment(loader=FileSystemLoader("{}".format(directory)))
		baseline = env.get_template(template)
		print("! [THE FOLLOWING CODE WILL BE PUSHED:]")
		print("")
	
		for index in initialize.element:
			f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "w") 
			config_list = []
			config = baseline.render(nodes = node_object[index])
			print ("+ [{}".format(node_object[index]['hostname']) + "#]")
			f.write(config) 
			f.close 
			print("{}".format(config))
			print("")
			if(flag):
				f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "r") 
				init_config = f.readlines()
			
				for config_line in init_config:
					strip_config = config_line.strip('\n')
					config_list.append(strip_config)		
			
				initialize.configuration.append(config_list)
	
		return None

def audit_filter(template):

	AUDIT_FILTER_RE = r"\[.*\]"

	f = open("/template/{}".format(template), "r")

	auditfilter = f.read()
	audit_list = eval(re.findall(AUDIT_FILTER_RE, auditfilter)[0])	

	return audit_list
