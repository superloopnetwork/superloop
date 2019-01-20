### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
### AND PACKAGES THEM INTO A LIST OF LISTS. IT ONLY LOOKS AT THE 
### SELECTED INDEXES (INIITIALIZE.ELEMENT) OF THE NODE_OBJECT. 
### THE CONFIGURATIONS ARE STORED IN THE GLOBAL VARIABLE CALL 
### INITIALIZE.CONFIGURATION.

from jinja2 import Environment, FileSystemLoader
from collections import Counter
from multithread import multithread_engine
from directory import get_directory
import re
import initialize

def auditdiff_engine(template_list,node_object,auditcreeper):

	controller = 'get_config'
	command = ''

	template_index = 0

	### INDEX_POSITION IS THE INDEX OF ALL THE MATCHED FILTER_CONFIG AGAINST THE BACKUP_CONFIGS. THE INDEX IS COMING FROM THE BACKUP_CONFIG
	index_position = 0

	### NODE_INDEX KEEPS TRACK OF THE INDEX IN INITIALIZE.NTW_DEVICE. IF REMEDIATION IS NOT REQUIRED (CONFIGS MATCHES TEMPLATE), THEN THE NODE IS POPPED OFF
	### INITIALIZE.NTW_DEVICE AND NOTHING IS CHANGED ON THAT DEVICE
	node_index = 0 
	index_template = 0

	### AUDIT_FILTER_RE IS THE REGULAR EXPRESSION TO FILTER OUT THE AUDIT FILTER IN EVERY TEMPLATE
	AUDIT_FILTER_RE = r"\[.*\]"

	template_list_copy = template_list

	if(auditcreeper):
		template_list = template_list_copy[0]
#		print("TEMPLATE_LIST : {} ; TEMPLATE_LIST_COPY : {}".format(template_list,template_list_copy))

	print("[+] [GATHERING RUNNING-CONFIG. STANDBY...]")
	multithread_engine(initialize.ntw_device,controller,command)
	print("[!] [DONE]")

	### THIS FOR LOOP WILL LOOP THROUGH ALL THE MATCHED ELEMENTS FROM THE USER SEARCH AND AUDIT ON THE GIVEN TEMPLATE
	for index in initialize.element:

		node_configs = []
		ntw_device_pop = True 
		diff = True
		print("")
		print ("[{}".format(node_object[index]['hostname']) + "#]")

		for template in template_list:

#			print("HOST: {} ; TEMPLATE: {}".format(node_object[index]['hostname'],template))
#			print("THIS IS FOR TEMPLATE: {}".format(template))

			### INDEX_LIST IS A LIST OF ALL THE POSITIONS COLLECTED FROM INDEX_POSITION VARIABLE
			index_list = []

			### FILTER_CONFIG IS A LIST OF COLLECTION OF ALL THE AUDIT FILTERS THAT MATCHED THE LINES IN BACKUP_CONFIG. THESE ENTRIES DO NOT CONTAIN DEPTHS/DEEP CONFIGS
			filtered_config = []

			### FILTERED_BACKUP_CONFIG IS THE FINAL LIST OF ALL THE AUDIT FILTERS THAT MATCHES THE LINES IN BACKUP_CONFIG. THESE ENTRIES INCLUDE DEPTHS/DEEP CONFIGS
			filtered_backup_config = []

			directory = get_directory(node_object[index]['platform'],node_object[index]['os'],node_object[index]['type'])
			env = Environment(loader=FileSystemLoader("{}".format(directory)))
			baseline = env.get_template(template)
			f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "w") 

			### GENERATING TEMPLATE BASED ON NODE OBJECT
			config = baseline.render(nodes = node_object[index])

			f.write(config) 
			f.close 
#			print("{}".format(config))

			### OPEN RENDERED CONFIG FILE AND STORE IN RENDERED_CONFIG AS A LIST
			f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "r")
			init_config = f.readlines()
			rendered_config = []

			for config_line in init_config:
				strip_config = config_line.strip('\n')
				### THIS WILL REMOVE ANY LINES THAT ARE EMPTY OR HAS A '!' MARK
				if(strip_config == '' or strip_config == "!"):
					continue	
				else:
					rendered_config.append(strip_config)	

#			print ("RENDERED CONFIG: {}".format(rendered_config))
			
			### OPEN BACKUP CONFIG FILE AND STORE IN BACKUP_CONFIG AS A LIST
			f = open("/backup-configs/{}".format(node_object[index]['hostname']) + ".conf", "r")
			init_config = f.readlines()
			backup_config = []

			for config_line in init_config:
				strip_config = config_line.strip('\n')
				backup_config.append(strip_config)	

#			print ("BACKUP CONFIG: {}".format(backup_config))
			
			### THIS WILL OPEN THE JINJA2 TEMPLATE AND PARSE OUT THE AUDIT_FILTER SECTION VIA REGULAR EXPRESSION
			directory = get_directory(node_object[index]['platform'],node_object[index]['os'],node_object[index]['type'])
			f = open("{}".format(directory) + template, "r")
			parse_audit = f.readline()
			audit_filter = eval(re.findall(AUDIT_FILTER_RE, parse_audit)[0])

			### FILTER OUT THE BACKUP_CONFIGS WITH THE AUDIT_FILTER
			for audit in audit_filter:
				query = re.compile(audit)
				filters = list(filter(query.match,backup_config))

				for aud_filter in filters:
					filtered_config.append(aud_filter)

			### UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#			print("THIS IS THE FILTERED_CONFIG: {}".format(filtered_config))

			### GETTING THE INDEXES OF FILTER_CONFIG FROM BACKUP_CONFIG
			for config in filtered_config:
				if(config in backup_config):
					index_position = backup_config.index(config)
					index_list.append(index_position)
#				print("THIS IS THE INDEX_LIST: {}".format(index_list))

			### EXTRACTING ALL RELAVENT CONFIGS PERTAINING TO THE ONES THAT WERE PICKED UP THROUGH FILTERING
			for index_pos in index_list:

				next_element = index_pos + 1

				filtered_backup_config.append(backup_config[index_pos])
				### CHECKS THE NEXT LINE OF CODE FOR THE WHITESPACE COUNT
				whitespace = (len(backup_config[next_element])-len(backup_config[next_element].lstrip()))
#				print("{}".format(backup_config[index_pos]))
				while(whitespace != 0):
					filtered_backup_config.append(backup_config[next_element])
#					print("{}".format(backup_config[next_element]))
					next_element = next_element + 1
					whitespace = (len(backup_config[next_element])-len(backup_config[next_element].lstrip()))
				

#			print("THIS IS THE FILTERED BACKUP CONFIG: {}".format(filtered_backup_config))		
					
			### COMPARING EACH ELEMENT IN RENDERED_CONFIG AGAINST FILTERED_BACKUP_CONFIG(RUNNING CONFIG OF DEVICE)
#			minus_commands = list(set(filtered_backup_config) - set(rendered_config))
#			plus_commands = list(set(rendered_config) - set(filtered_backup_config))

#			filtered_set = set(filtered_backup_config)
#			rendered_set = set(rendered_config)

			### MINUS_COMMANDS IS A LIST OF COMMANDS THAT EXIST ON THE NODE THAT SHOULDN'T BE WHEN COMPARED AGAINST THE TEMPLATE
#			minus_commands = [x for x in filtered_backup_config if x not in rendered_set]

			### PLUS_COMMAND IS A LIST OF COMMAND THAT DOESN'T EXIST ON THE NODE THAT SHOULD BE WHEN COMPARED AGAINST THE TEMPLATE
#			plus_commands = [x for x in rendered_config if x not in filtered_set]
			filtered_set = Counter(filtered_backup_config)
			rendered_set = Counter(rendered_config)

			minus_commands_counter = filtered_set - rendered_set
			plus_commands_counter = rendered_set - filtered_set

			minus_commands = list(minus_commands_counter.elements())
			plus_commands = list(plus_commands_counter.elements())

			
			### NODE_CONFIG IS THE FINALIZED CONFIG TO PUSH TO THE NODE FOR REMEDIATION

#			print("minus_commands: {}".format(minus_commands))
#			print("plus_commands: {}".format(plus_commands))

#			print("THIS IS MINUS_COMMANDS: {}".format(minus_commands))
#			print("")
#			print("THIS IS PLUS_COMMANDS: {}".format(plus_commands))

			if(len(minus_commands) == 0 and len(plus_commands) == 0 and auditcreeper == False):
				print("{}{} (none)".format(directory,template))
				print
				initialize.ntw_device.pop(node_index)

			if(len(minus_commands) == 0 and len(plus_commands) == 0 and auditcreeper == True):
				print("{}{} (none)".format(directory,template))
				print

			elif(len(minus_commands) >= 1 or len(plus_commands) >= 1):

				### THIS WILL JUST PRINT THE HEADING OF THE TEMPLATE NAME SO YOU KNOW WHAT IS BEING CHANGED UNDER WHICH TEMPLATE
				if(diff):	
					print("{}{}".format(directory,template))
					print
					diff = False

				if(len(minus_commands) >= 1):
					for minus in minus_commands:
 						print("- {}".format(minus))

				if(len(plus_commands) >= 1):
					for plus in plus_commands:
						print("+ {}".format(plus))
					
				### IF ENVIRONMENT HAVE MULTI VENDORS, INSERT CONDITIONAL STATEMENTS TO ACCOMODATE:
				### if(node_object[index]['platform'] == 'cisco' and node_object[index]['os'] == 'ios'):
				### THIS STEP WILL NEGATE ALL ALL ANCHORED COMMANDS
				if(node_object[index]['platform'] == 'cisco' and node_object[index]['os'] == 'ios'):

					### THIS WILL NEGATE ALL THE ANCHORED CONFIGS
					for anchor in filtered_config:
						node_configs.append("no {}".format(anchor))

					### THIS STEP WILL APPEND REMEDIATION CONFIGS FROM TEMPLATE
					for config in rendered_config:
						node_configs.append(config)
						ntw_device_pop = False

					### INITIALIZE.COFIGURATION APPENDS ALL THE REMEDIATED CONFIGS AND PREPARES IT FOR PUSH
					if(auditcreeper == False):
						initialize.configuration.append(node_configs)
					node_index = node_index + 1

				

#			elif(len(minus_commands) >= 1):
#			
#				### THIS WILL JUST PRINT THE HEADING OF THE TEMPLATE NAME SO YOU KNOW WHAT IS BEING CHANGED UNDER WHICH TEMPLATE
#				if(diff):	
#					print("{}{}".format(directory,template))
#					diff = False
#
#				for minus in minus_commands:
#					print("- {}".format(minus))
#
#				### IF ENVIRONMENT HAVE MULTI VENDORS, INSERT CONDITIONAL STATEMENTS TO ACCOMODATE:
#				### if(node_object[index]['platform'] == 'cisco' and node_object[index]['os'] == 'ios'):
#				### THIS STEP WILL NEGATE ALL ALL ANCHORED COMMANDS
#				if(node_object[index]['platform'] == 'cisco' and node_object[index]['os'] == 'ios'):
#
#					### THIS WILL NEGATE ALL THE ANCHORED CONFIGS
#					for anchor in filtered_config:
#						node_configs.append("no {}".format(anchor))
#
#					### THIS STEP WILL APPEND REMEDIATION CONFIGS FROM TEMPLATE
#					for config in rendered_config:
#						node_configs.append(config)
#						ntw_device_pop = False
#
#					### INITIALIZE.COFIGURATION APPENDS ALL THE REMEDIATED CONFIGS AND PREPARES IT FOR PUSH
#					if(auditcreeper == False):
#						initialize.configuration.append(node_configs)
#					node_index = node_index + 1
#
#			elif(len(plus_commands) >= 1):
#
#				### THIS WILL JUST PRINT THE HEADING OF THE TEMPLATE NAME SO YOU KNOW WHAT IS BEING CHANGED UNDER WHICH TEMPLATE
#				if(diff):	
#					print("{}{}".format(directory,template))
#					diff = False
#
#				for plus in plus_commands:
#					print("+ {}".format(plus))
#
#				if(node_object[index]['platform'] == 'cisco' and node_object[index]['os'] == 'ios'):
#			
#					### THIS STEP WILL APPEND REMEDIATION CONFIGS FROM TEMPLATE
#					for config in rendered_config:
#						node_configs.append(config)
#						ntw_device_pop = False
#
#					### INITIALIZE.COFIGURATION APPENDS ALL THE REMEDIATED CONFIGS AND PREPARES IT FOR PUSH
#					if(auditcreeper == False):
#						initialize.configuration.append(node_configs)
#					node_index = node_index + 1


		if(auditcreeper):
#			print("LENGTH OF LIST IS : {}".format(len(template_list_copy)))
			initialize.configuration.append(node_configs)
			if(ntw_device_pop == True):
				initialize.ntw_device.pop(node_index)
				initialize.configuration.pop(node_index)
			if(len(template_list_copy) != 1):
				template_list_copy.pop(0)
				template_list = template_list_copy[0]
#			print("TEMPLATE_LIST : {} ; TEMPLATE_LIST_COPY : {}".format(template_list,template_list_copy))
#				print("FINAL REMEDIATION CONFIGS: {}".format(initialize.configuration))
#			del rendered_config[:]		
#		 	del backup_config[:]
#			del index_list[:]
#			del filtered_config[:]
#			del filtered_backup_config[:]


#	print("INITIALIZE.NTW_DEVICE: {}".format(initialize.ntw_device))
#	print("INITIALIZE.CONFIGURATION : {}".format(initialize.configuration))

	return None
