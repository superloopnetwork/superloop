### PARSE_AUDIT_FILTER FUNCTION FILTERS OUT THE BACKUP_CONFIGS WITH THE AUDIT_FILTER
### THIS WILL TAKE EACH ELEMENT FROM THE AUDIT_FILTER LIST AND SEARCH FOR THE MATCHED LINES IN BACKUP_CONFIG
### MATCHED ENTRIES ARE THEN APPENDED TO FILTER_BACKUP_CONFIG VARIABLE AS A LIST AND RETURNED

import re
import initialize
import os
from ciscoconfparse import CiscoConfParse
from get_property import get_template_directory
from get_property import get_syntax
from get_property import get_sorted_juniper_template_list 

home_directory = os.environ.get('HOME')

def cisco_audit_diff(node_object,index,template,template_list,AUDIT_FILTER_RE,output,remediation):

	for template in template_list:
		### INDEX_LIST IS A LIST OF ALL THE POSITIONS COLLECTED FROM INDEX_POSITION VARIABLE
		index_list = []
		
		### FILTER_CONFIG IS A LIST OF COLLECTION OF ALL THE AUDIT FILTERS THAT MATCHED THE LINES IN BACKUP_CONFIG. THESE ENTRIES DO NOT CONTAIN DEPTHS/DEEP CONFIGS
		filtered_config = []
		
		### FILTERED_BACKUP_CONFIG IS THE FINAL LIST OF ALL THE AUDIT FILTERS THAT MATCHES THE LINES IN BACKUP_CONFIG. THESE ENTRIES INCLUDE DEPTHS/DEEP CONFIGS
		filtered_backup_config = []
		
		### THIS SECTION OF CODE WILL OPEN THE RENDERED-CONFIG *.CONF FILE AND STORE IN RENDERED_CONFIG AS A LIST
		f = open("{}/rendered-configs/{}.{}".format(home_directory,node_object[index]['hostname'],template.split('.')[0]) + ".conf", "r")
		init_config = f.readlines()
	#	print"INIT_CONFIG: {}".format(init_config)
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
	#	print ("RENDERED CONFIG: {}".format(rendered_config))
		
		### THIS SECTION OF CODE WILL OPEN BACKUP-CONFIG *.CONF FILE AND STORE IN BACKUP_CONFIG AS A LIST
		f = open("{}/backup-configs/{}".format(home_directory,node_object[index]['hostname']) + ".conf", "r")
		init_config = f.readlines()
		backup_config = []
		
		for config_line in init_config:
			strip_config = config_line.strip('\n')
			backup_config.append(strip_config)	
		
		###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
	#	print ("BACKUP CONFIG: {}".format(backup_config))
		
		### THIS WILL OPEN THE JINJA2 TEMPLATE AND PARSE OUT THE AUDIT_FILTER SECTION VIA REGULAR EXPRESSION
		directory = get_template_directory(node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'])
		f = open("{}".format(directory) + template, "r")
		parse_audit = f.readline()
		audit_filter = eval(re.findall(AUDIT_FILTER_RE, parse_audit)[0])
		
		###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
	#	print ("AUDIT_FILTER: {}".format(audit_filter))
		
		### FILTER OUT THE BACKUP_CONFIGS WITH THE AUDIT_FILTER
		### THIS WILL TAKE EACH ELEMENT FROM THE AUDIT_FILTER LIST AND SEARCH FOR THE MATCHED LINES IN BACKUP_CONFIG
		### PARSING THE BACKUP CONFIGS
		parse_backup_configs = CiscoConfParse("{}/backup-configs/{}".format(home_directory,node_object[index]['hostname']) + ".conf", syntax=get_syntax(node_object,index))
	#	print "SYNTAX: {}".format(get_syntax(node_object,index))
		
		### MATCHED ENTRIES ARE THEN APPENDED TO FILTER_BACKUP_CONFIG VARIABLE AS A LIST
		### FUNCTION CALL TO PARSE_AUDIT_FILTER() TO FIND ALL THE PARENT/CHILD
		filtered_backup_config = parse_audit_filter(
				node_object,
				index,
				parse_backup_configs,
				audit_filter
		)
		
		### UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
	#	print("FILTERED BACKUP CONFIG: {}".format(filtered_backup_config))		
		
		### SYNC_DIFF WILL DIFF OUT THE FILTERED_BACKUP_COFNIG FROM THE RENDERED CONFIG AND STORE WHATEVER COMMANDS THAT
		### COMMANDS THAT NEED TO BE ADDED/REMOVE IN PUSH_CONFIGS VARIABLE
		parse = CiscoConfParse(filtered_backup_config)
		push_configs = parse.sync_diff(
				rendered_config,
				"",
				ignore_order=True, 
				remove_lines=True, 
				debug=False
		)
		if(len(push_configs) == 0):
			if(output):
				print("{}{} (none)".format(directory,template))
				print('')
		else:
		
			### THIS WILL JUST PRINT THE HEADING OF THE TEMPLATE NAME SO YOU KNOW WHAT IS BEING CHANGED UNDER WHICH TEMPLATE
			if(output):
				print("{}{}".format(directory,template))
		
			for line in push_configs:
				search = parse_backup_configs.find_objects(r"^{}".format(line))
				if('no' in line):
					line = re.sub("no","",line)
					if(not remediation):
						print("-{}".format(line))
				elif(len(search) == 0):
					if(not remediation):
						print("+ {}".format(line))
				elif(len(search) > 1):
					if(not remediation):
						print("+ {}".format(line))
				else:
					if(not remediation):
						print("  {}".format(line))
				
			print("")
			###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
	#		print("PUSH_CONFIGS: {}".format(push_configs))
			if(remediation):
		
				### THIS STEP WILL APPEND REMEDIATION CONFIGS FROM TEMPLATE (EXPECTED RESULTS)
				for config in push_configs:
					node_configs.append(config)
					ntw_device_pop = False
				### INITIALIZE.COFIGURATION APPENDS ALL THE REMEDIATED CONFIGS AND PREPARES IT FOR PUSH
				if(auditcreeper == False):
					initialize.configuration.append(node_configs)
				node_index = node_index + 1

	return None

def parse_audit_filter(node_object,index,parse_backup_configs,audit_filter):
	filtered_backup_config = []
	for audit in audit_filter:
		current_template = parse_backup_configs.find_objects(r"^{}".format(audit))
		for audit_string in current_template:
			filtered_backup_config.append(audit_string.text)
			if(audit_string.is_parent):
				for child in audit_string.all_children:
					filtered_backup_config.append(child.text)
			### THE BELOW IF STATEMENT WILL ACCOMODATE JUNIPER PLATFORM SYNTAX AS IT'S MISSING A CLOSING CURLY BRACE AT THE END 
			if(node_object[index]['platform'] == 'juniper'):
				filtered_backup_config.append('}')

	return filtered_backup_config
