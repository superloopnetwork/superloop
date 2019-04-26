### THIS MODULE PROCESS THE YAML FILE TO CREATE THE DATABASES OF BOTH
### NODES AND TEMPLATES

import yaml

def append_nodes(data):

	with open('nodes.yaml','a') as yaml_file:
		yaml_file.write(data)
	
