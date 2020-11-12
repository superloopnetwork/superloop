### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
### AND PACKAGES THEM INTO A LIST OF LISTS. THIS IS STORED IN THE 
### GLOBAL VARIABLE CALL INITIALIZE.CONFIGURATION.

from jinja2 import Environment, FileSystemLoader
from get_property import get_template_directory
from get_property import get_location_directory
from get_property import get_updated_list
from parse_cmd import parse_commands
import initialize
import re

def render(template_list,node_object,auditcreeper,output,with_remediation):

### TEMPLATE_LIST_COPY TAKE A COPY OF THE CURRENT TEMPLATE_LIST
	template_list_copy = template_list

	if(auditcreeper):
	    template_list = template_list_copy[0]
#	print("[!] [THE FOLLOWING TEMPLATE(S) IS/ARE RENDERED:]")
	for index in initialize.element:
		get_platform_template_directory = get_template_directory(node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'])
		print ("{}".format(node_object[index]['hostname']))
		for template in template_list:
			config = process_jinja2_template(node_object,index,template,with_remediation)
			print("{}{}".format(get_platform_template_directory,template))
			if(output):
				print("{}".format(config))

			f = open("/rendered-configs/{}.{}".format(node_object[index]['hostname'],template.replace('jinja2','')) + "conf", "r")
			init_config = f.readlines()
			### THE BELOW PARSE_COMMANDS FUNCTION WILL ONLY GET EXECUTED IF NEEDS TO STORE COMMANDS IN THE GLOBAL VARILABLE INITIALIZE.CONFIGURATION FOR PUSH
			### PUSH_CFGS(OUTPUT = TRUE) VS RENDER_CONFIG(OUTPUT = FALSE) FUNCTIONS.
			if(output!=True):
				parse_commands(node_object[index],init_config)
			print()

		if(auditcreeper):
			template_list = get_updated_list(template_list_copy)

	return None

def process_jinja2_template(node_object,index,template,with_remediation):
	### THIS CALLS THE DIRECTORY MODULE WHICH WILL RETURN THE CORRECT DIRECTORY PATH BASED ON DEVICE PLATFORM, OS AND TYPE
	get_platform_template_directory = get_template_directory(node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'])
	get_location_template_directory = get_location_directory(node_object[index]['hostname'],node_object[index]['platform'],node_object[index]['type'])
	env = Environment(loader=FileSystemLoader([get_platform_template_directory,get_location_template_directory]),lstrip_blocks = True,trim_blocks=True)
	baseline = env.get_template(template)
	f = open("/rendered-configs/{}.{}".format(node_object[index]['hostname'],template.strip('jinja2')) + "conf", "w") 
	config = baseline.render(nodes = node_object[index],with_remediation = with_remediation)
	f.write(config) 
	f.close 

	return config

def remediate(input):
	"""Custom filter"""
	if with_remediate == True:
		return input
	else:
		return ''
