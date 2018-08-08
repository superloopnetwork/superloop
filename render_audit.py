### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
### AND PACKAGES THEM INTO A LIST OF LISTS. IT ONLY LOOKS AT THE 
### SELECTED INDEXES (INIITIALIZE.ELEMENT) OF THE NODE_OBJECT. 
### THE CONFIGURATIONS ARE STORED IN THE GLOBAL VARIABLE CALL 
### INITIALIZE.CONFIGURATION.

from jinja2 import Environment, FileSystemLoader
from multithread import multithread_engine
import initialize

def render_audit(template,node_object):

	controller = 'get_config'
	command = ''
	element = 0
	expected_index = 0

	print("! [GATHERING RUNNING-CONFIG. STANDBY...]")
	multithread_engine(initialize.ntw_device,controller,command)
	print("! [DONE]")

	env = Environment(loader=FileSystemLoader('.'))
	baseline = env.get_template(template)

	for index in initialize.element:
		f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "w") 

		### GENERATING TEMPLATE BASED ON NODE OBJECT
		config = baseline.render(nodes = node_object[index])

		print ("+ [{}".format(node_object[index]['hostname']) + "#]")
		f.write(config) 
		f.close 
		print("{}".format(config))
		print("")

		### OPEN RENDERED CONFIG FILE AND STORE IN RENDERED_CONFIG AS A LIST
		f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "r")
		init_config = f.readlines()

		for config_line in init_config:
			strip_config = config_line.strip('\n')
			initialize.rendered_config.append(strip_config)	

		print ("RENDERED CONFIG: {}".format(initialize.rendered_config))
		
		### OPEN BACKUP CONFIG FILE AND STORE IN BACKUP_CONFIG AS A LIST
		f = open("/backup-configs/{}".format(node_object[index]['hostname']) + ".conf", "r")
		init_config = f.readlines()

		for config_line in init_config:
			strip_config = config_line.strip('\n')
			initialize.backup_config.append(strip_config)	

		print ("BACKUP CONFIG: {}".format(initialize.backup_config))

		### COMPARING EACH ELEMENT IN RENDERED_CONFIG AGAINST BACKUP_CONFIG(RUNNING CONFIG OF DEVICE)
		### KEEPING TRACK OF IT'S INDEX POINT IN BACKUP_CONFIG AND IT'S WHITESPACES

	return None
