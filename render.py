### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
### AND PACKAGES THEM INTO A LIST OF LISTS. THIS IS STORED IN THE 
### GLOBAL VARIABLE CALL INITIALIZE.CONFIGURATION.

from jinja2 import Environment, FileSystemLoader
from get_property import get_directory
from get_property import get_template
from parse_commands import parse_commands
import initialize
import re

def render(template_list,node_object,auditcreeper,output):

### TEMPLATE_LIST_COPY TAKE A COPY OF THE CURRENT TEMPLATE_LIST
	template_list_copy = template_list

	if(auditcreeper):
	    template_list = template_list_copy[0]
#	print("[!] [THE FOLLOWING TEMPLATE(S) IS/ARE RENDERED:]")
	for index in initialize.element:

		print ("{}".format(node_object[index]['hostname']))
		for template in template_list:
		### THIS CALLS THE DIRECTORY MODULE WHICH WILL RETURN THE CORRECT DIRECTORY PATH BASED ON DEVICE PLATFORM, OS AND TYPE
			directory = get_directory(node_object[index]['platform'],node_object[index]['os'],node_object[index]['type'])
			env = Environment(loader=FileSystemLoader("{}".format(directory)))
			baseline = env.get_template(template)
			f = open("/rendered-configs/{} - {}".format(node_object[index]['hostname'],template.strip('jinja2')) + ".conf", "w") 
			config_list = []
			config = baseline.render(nodes = node_object[index])
			f.write(config) 
			f.close 
			print("{}{}".format(directory,template))
			if(output):
				print("{}".format(config))

			f = open("/rendered-configs/{} - {}".format(node_object[index]['hostname'],template.strip('jinja2')) + ".conf", "r")
			init_config = f.readlines()
			### THE BELOW PARSE_COMMANDS FUNCTION WILL ONLY GET EXECUTED IF NEEDS TO STORE COMMANDS IN THE GLOBAL VARILABLE INITIALIZE.CONFIGURATION FOR PUSH
			### PUSH_CFGS(OUTPUT = TRUE) VS RENDER_CONFIG(OUTPUT = FALSE) FUNCTIONS.
			if(output!=True):
				parse_commands(node_object[index],init_config)

		if(auditcreeper):
			template_list = get_template(template_list_copy)
		print

	return None
