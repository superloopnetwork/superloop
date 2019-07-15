### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
### AND PACKAGES THEM INTO A LIST OF LISTS. IT ONLY LOOKS AT THE 
### SELECTED INDEXES (INIITIALIZE.ELEMENT) OF THE NODE_OBJECT. 
### THE CONFIGURATIONS ARE STORED IN THE GLOBAL VARIABLE CALL 
### INITIALIZE.CONFIGURATION.

from jinja2 import Environment, FileSystemLoader
from ciscoconfparse import CiscoConfParse
from collections import Counter
from multithread import multithread_engine
from get_property import get_directory
from get_property import get_template
import re
import difflib
import initialize

def auditdiff_engine(template_list,node_object,auditcreeper):

	controller = 'get_config'
	command = ''
	push_configs = []


	### INDEX_POSITION IS THE INDEX OF ALL THE MATCHED FILTER_CONFIG AGAINST THE BACKUP_CONFIGS. THE INDEX IS COMING FROM THE BACKUP_CONFIG
	index_position = 0

	### NODE_INDEX KEEPS TRACK OF THE INDEX IN INITIALIZE.NTW_DEVICE. IF REMEDIATION IS NOT REQUIRED (CONFIGS MATCHES TEMPLATE), THEN THE NODE IS POPPED OFF
	### INITIALIZE.NTW_DEVICE AND NOTHING IS CHANGED ON THAT DEVICE
	node_index = 0 

	### AUDIT_FILTER_RE IS THE REGULAR EXPRESSION TO FILTER OUT THE AUDIT FILTER IN EVERY TEMPLATE
	AUDIT_FILTER_RE = r"\[.*\]"

	### TEMPLATE_LIST_COPY TAKE A COPY OF THE CURRENT TEMPLATE_LIST
	template_list_copy = template_list

	if(auditcreeper):
		template_list = template_list_copy[0]

	print("[+] [GATHERING RUNNING-CONFIG. STANDBY...]")
	multithread_engine(initialize.ntw_device,controller,command)

	### THIS FOR LOOP WILL LOOP THROUGH ALL THE MATCHED ELEMENTS FROM THE USER SEARCH AND AUDIT ON SPECIFIC TEMPLATE OR IF NO ARGUMENT IS GIVEN, ALL TEMPLATES
	for index in initialize.element:

		### NODE_CONFIG IS THE FINALIZED CONFIG TO PUSH TO THE NODE FOR REMEDIATION
		node_configs = []
		ntw_device_pop = True 
		### TEMPLATE_NAME IS SET TO TRUE IN ORDER TO PRINT OUT THE TEMPLATE HEADING WHEN RECURSING
		template_name = True
		first_parent = True
		previous_parent = ''

		print("")
		print ("[+] [{}".format(node_object[index]['hostname']) + "#]")

		for template in template_list:

			### INDEX_LIST IS A LIST OF ALL THE POSITIONS COLLECTED FROM INDEX_POSITION VARIABLE
			index_list = []

			### FILTER_CONFIG IS A LIST OF COLLECTION OF ALL THE AUDIT FILTERS THAT MATCHED THE LINES IN BACKUP_CONFIG. THESE ENTRIES DO NOT CONTAIN DEPTHS/DEEP CONFIGS
			filtered_config = []

			### FILTERED_BACKUP_CONFIG IS THE FINAL LIST OF ALL THE AUDIT FILTERS THAT MATCHES THE LINES IN BACKUP_CONFIG. THESE ENTRIES INCLUDE DEPTHS/DEEP CONFIGS
			filtered_backup_config = []

			### THIS SECTION OF CODE WILL PROCESS THE TEMPLATE AND OUTPUT TO A *.CONF FILE
			directory = get_directory(node_object[index]['platform'],node_object[index]['os'],node_object[index]['type'])
			env = Environment(loader=FileSystemLoader("{}".format(directory)))
			baseline = env.get_template(template)
			f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "w") 

			### GENERATING TEMPLATE BASED ON NODE OBJECT
			config = baseline.render(nodes = node_object[index])

			f.write(config) 
			f.close 

			### THIS SECTION OF CODE WILL OPEN THE RENDERED-CONFIG *.CONF FILE AND STORE IN RENDERED_CONFIG AS A LIST
			f = open("/rendered-configs/{}".format(node_object[index]['hostname']) + ".conf", "r")
			init_config = f.readlines()
			### RENDERED_CONFIG IS A LIST OF ALL THE CONFIGS THAT WAS RENDERED FROM THE TEMPLATES (SOURCE OF TRUTH)
			rendered_config = []

			for config_line in init_config:
				strip_config = config_line.strip('\n')
				### THIS WILL REMOVE ANY LINES THAT ARE EMPTY OR HAS A '!' MARK
				if(strip_config == '' or strip_config == "!"):
					continue	
				else:
					rendered_config.append(strip_config)	

			###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#			print ("RENDERED CONFIG: {}".format(rendered_config))
			
			### THIS SECTION OF CODE WILL OPEN BACKUP-CONFIG *.CONF FILE AND STORE IN BACKUP_CONFIG AS A LIST
			f = open("/backup-configs/{}".format(node_object[index]['hostname']) + ".conf", "r")
			init_config = f.readlines()
			backup_config = []

			for config_line in init_config:
				strip_config = config_line.strip('\n')
				backup_config.append(strip_config)	

			###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#			print ("BACKUP CONFIG: {}".format(backup_config))
			
			### THIS WILL OPEN THE JINJA2 TEMPLATE AND PARSE OUT THE AUDIT_FILTER SECTION VIA REGULAR EXPRESSION
			directory = get_directory(node_object[index]['platform'],node_object[index]['os'],node_object[index]['type'])
			f = open("{}".format(directory) + template, "r")
			parse_audit = f.readline()
			audit_filter = eval(re.findall(AUDIT_FILTER_RE, parse_audit)[0])

			###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#			print ("{}".format(audit_filter))

			### FILTER OUT THE BACKUP_CONFIGS WITH THE AUDIT_FILTER
			### THIS WILL TAKE EACH ELEMENT FROM THE AUDIT_FILTER LIST AND SEARCH FOR THE MATCHED LINES IN BACKUP_CONFIG
			### MATCHED ENTRIES ARE THEN APPENDED TO FILTER_CONFIG VARIABLE AS A LIST
			for audit in audit_filter:

				parse_backup_configs = CiscoConfParse("/backup-configs/{}".format(node_object[index]['hostname']) + ".conf")
				current_template = parse_backup_configs.find_objects(r"{}".format(audit))
				for audit_string in current_template:       
					filtered_backup_config.append(audit_string.text)
					if(audit_string.is_parent):
						for child in audit_string.all_children:
							filtered_backup_config.append(child.text)

			###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#			print("FILTERED BACKUP CONFIG: {}".format(filtered_backup_config))		
					
			### FILTERED_SET/RENDERED_SET RETURNS A DICTIONARY OF THE NUMBER OF TIMES A CONFIG IS REPEATED IN THE LIST
			filtered_backup_set = Counter(filtered_backup_config)
			rendered_set = Counter(rendered_config)
			minus_commands_counter = filtered_backup_set - rendered_set
			plus_commands_counter = rendered_set - filtered_backup_set

			### MINUS_COMMANDS IS A LIST OF COMMANDS THAT EXIST ON THE NODE THAT SHOULDN'T BE WHEN COMPARED AGAINST THE TEMPLATE
			### PLUS_COMMAND IS A LIST OF COMMAND THAT DOESN'T EXIST ON THE NODE THAT SHOULD BE WHEN COMPARED AGAINST THE TEMPLATE
			minus_commands = list(minus_commands_counter.elements())
			plus_commands = list(plus_commands_counter.elements())

#			print("MINUS_COMMANDS: {}".format(minus_commands))
#			print("PLUS_COMMANDS:: {}".format(plus_commands))
			### THIS SECTION OF CODE CHECKS TO SEE IF THE LENGTH OF THE TWO LIST IS EQUAL TO ZERO, THEN NOTHING HAS TO BE REMEDIATED
			if(len(minus_commands) == 0 and len(plus_commands) == 0 and auditcreeper == False):
				print("{}{} (none)".format(directory,template))
				print
				initialize.ntw_device.pop(node_index)

			if(len(minus_commands) == 0 and len(plus_commands) == 0 and auditcreeper == True):
				print("{}{} (none)".format(directory,template))
				print

			elif(len(minus_commands) >= 1 or len(plus_commands) >= 1):

				### THIS WILL JUST PRINT THE HEADING OF THE TEMPLATE NAME SO YOU KNOW WHAT IS BEING CHANGED UNDER WHICH TEMPLATE
				print("{}{}".format(directory,template))

				### THIS SECTION OF CODE WILL PRINT THE DIFF OF WHAT CONFIG(S) WILL BE CHANGING
				for line in difflib.unified_diff(filtered_backup_config, rendered_config,n=10):
					if(line.startswith("---") or line.startswith("+++") or line.startswith("@") or line.startswith("  ")):
						continue
					else:
						print line
						if(line.startswith("-")):
							config_line = line.strip()
							if(re.match("-",config_line)):
								config_line = line.replace("-","no ")
								push_configs.append(config_line)
							elif(re.match("-\s\w",line)):
								config_line = line.replace("-","no")
								push_configs.append(config_line)
						elif(line.startswith("+")):
							config_line = line.strip()
							config_line = line.strip("+")
							push_configs.append(config_line)
						else:
							config_line = line.strip()
							push_configs.append(config_line)
				print("")	
				print("PUSH_COMMANDS: {}".format(push_configs))
#				if(len(minus_commands) >= 1):
#					for minus in plus_commands:
#						print("+ {}".format(minus))
#				if(len(plus_commands) >= 1):
#					for plus in plus_commands:
#						print("+ {}".format(plus))
					
				### IF ENVIRONMENT HAVE MULTI VENDORS, INSERT CONDITIONAL STATEMENTS TO ACCOMODATE:
				### if(node_object[index]['platform'] == 'cisco' and node_object[index]['os'] == 'ios'):
				### THIS STEP WILL NEGATE ALL ALL ANCHORED COMMANDS
#				if(node_object[index]['platform'] == 'cisco' and node_object[index]['os'] == 'ios'):
#
#					### THIS WILL NEGATE ALL THE ANCHORED CONFIGS
#					for anchor in filtered_config:
#						node_configs.append("no {}".format(anchor))

					### THIS STEP WILL APPEND REMEDIATION CONFIGS FROM TEMPLATE
				for config in push_configs:
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
			template_list = get_template(template_list_copy)
#			if(len(template_list_copy) != 1):
#				template_list_copy.pop(0)
#				template_list = template_list_copy[0]
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
