### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
### AND PACKAGES THEM INTO A LIST OF LISTS. THIS IS STORED IN THE 
### GLOBAL VARIABLE CALL INITIALIZE.CONFIGURATION.

from jinja2 import Environment, FileSystemLoader
from directory import get_directory
import initialize
import re

def render(template,node_object,flag):

		print("[!] [THE FOLLOWING CODE WILL BE PUSHED:]")
		print("")
	
		for index in initialize.element:

			### THIS CALLS THE DIRECTORY MODULE WHICH WILL RETURN THE CORRECT DIRECTORY PATH BASED ON DEVICE PLATFORM, OS AND TYPE
			directory = get_directory(node_object[index]['platform'],node_object[index]['os'],node_object[index]['type'])
			env = Environment(loader=FileSystemLoader("{}".format(directory)))
			baseline = env.get_template(template)
			f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "w") 
			config_list = []
			config = baseline.render(nodes = node_object[index])
			print ("[{}".format(node_object[index]['hostname']) + "#]")
			f.write(config) 
			f.close 
			print("{}".format(config))
			if(flag):
				f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "r") 
				init_config = f.readlines()
			
				for config_line in init_config:
					strip_config = config_line.strip('\n')
					config_list.append(strip_config)		
			
				initialize.configuration.append(config_list)
	
		return None
