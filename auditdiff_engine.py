### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
### AND PACKAGES THEM INTO A LIST OF LISTS. IT ONLY LOOKS AT THE 
### SELECTED INDEXES (INIITIALIZE.ELEMENT) OF THE NODE_OBJECT. 
### THE CONFIGURATIONS ARE STORED IN THE GLOBAL VARIABLE CALL 
### INITIALIZE.CONFIGURATION.
from jinja2 import Environment, FileSystemLoader
from ciscoconfparse import CiscoConfParse
from collections import Counter
from multithread import multithread_engine
from get_property import get_template_directory
from get_property import get_updated_list
from get_property import get_syntax
from get_property import get_sorted_juniper_template_list 
import re
import initialize
import os
home_directory = os.environ.get('HOME')
def auditdiff_engine(template_list,node_object,auditcreeper,output,remediation):
	redirect = [] 
	command = [] 
	no_diff = 0
	###TEMPLATE_COUNTER IS TO KEEP TRACK OF WHEN THE LAST TEMPLATE ARRIVES IN THE LOOP
	template_counter = 0
	### PUSH_CONFIGS IS A LIST OF THE FINAL CONFIGS TO BE PUSHED
#	push_configs = []
	### INDEX_POSITION IS THE INDEX OF ALL THE MATCHED FILTER_CONFIG AGAINST THE BACKUP_CONFIGS. THE INDEX IS COMING FROM THE BACKUP_CONFIG
	index_position = 0
	### NODE_INDEX KEEPS TRACK OF THE INDEX IN INITIALIZE.NTW_DEVICE. IF REMEDIATION IS NOT REQUIRED (CONFIGS MATCHES TEMPLATE), THEN THE NODE IS POPPED OFF
	### INITIALIZE.NTW_DEVICE AND NOTHING IS CHANGED ON THAT DEVICE
	node_index = 0 
	### AUDIT_FILTER_RE IS THE REGULAR EXPRESSION TO FILTER OUT THE AUDIT FILTER IN EVERY TEMPLATE
	AUDIT_FILTER_RE = r"\[.*\]"
	### TEMPLATE_LIST_COPY TAKE A COPY OF THE CURRENT TEMPLATE_LIST
	template_list_original = template_list[:]
	template_list_copy = template_list
	if(auditcreeper):
		template_list = template_list_copy[0]
#	print "TEMPLATE_LIST: {}".format(template_list)
	### THIS SECTION OF CODE WILL GATHER ALL RENDERED CONFIGS FIRST AS IT'S REQUIRED FOR ALL PLATFORMS (CISCO & JUNIPER)
	### JUNIPER DOES NOT REQUIRE BACKUP-CONFIGS IN ORDER TO BE DIFFED SO INSTEAD IT WILL JUST PUSH (PUSH_CFGS) THE TEMPLATE AND PERFORM THE DIFF ON THE DEVICE ITSELF.
	### CISCO WILL REQUIRE BACKUP-CONFIGS (GET_CONFIG)
	for index in initialize.element:
		### INITIALIZING RENDERED_CONFIG
		rendered_config = []
		if(node_object[index]['platform'] == 'juniper'):
			### RENDERED_CONFIG IS TO ACCOMODATE JUNIPER PLATFORM BY APPENDING A 'LOAD REPLACE TERMINAL' TO GET THE DIFF OUTPUT
			rendered_config.append('load replace terminal')
			### THIS WILL RETURN A SORTED JUNIPER TEMPLATE LIST BASED ON JUNIPER'S 'SHOW CONFIGURATION' OUTPUT
			template_list = get_sorted_juniper_template_list(template_list)
#			print("TEMPLATE_LIST FIRST PHASE: {}".format(template_list))
		for template in template_list:
			### THIS SECTION OF CODE WILL PROCESS THE TEMPLATE AND OUTPUT TO A *.CONF FILE
			directory = get_template_directory(node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'])
			env = Environment(loader=FileSystemLoader(['{}'.format(directory),'/root/templates/juniper/junos/common/','/root/templates/juniper/junos/router/wdc1/']))
			baseline = env.get_template(template)
			f = open("{}/rendered-configs/{}.{}".format(home_directory,node_object[index]['hostname'],template.split('.')[0]) + ".conf", "w") 
			### GENERATING TEMPLATE BASED ON NODE OBJECT
			config = baseline.render(nodes = node_object[index])
			f.write(config) 
			f.close 
			if(node_object[index]['platform'] == 'cisco'):
				### THIS SECTION OF CODE WILL OPEN THE RENDERED-CONFIG *.CONF FILE AND STORE IN RENDERED_CONFIG AS A LIST
				f = open("{}/rendered-configs/{}.{}".format(home_directory,node_object[index]['hostname'],template.split('.')[0]) + ".conf", "r")
				init_config = f.readlines()
				### RENDERED_CONFIG IS A LIST OF ALL THE CONFIGS THAT WAS RENDERED FROM THE TEMPLATES (SOURCE OF TRUTH)
			if(node_object[index]['platform'] == 'juniper'):
				template_counter = template_counter + 1
	
				### THIS SECTION OF CODE WILL OPEN THE RENDERED-CONFIG *.CONF FILE AND STORE IN RENDERED_CONFIG AS A LIST
				f = open("{}/rendered-configs/{}.{}".format(home_directory,node_object[index]['hostname'],template.split('.')[0]) + ".conf", "r")
				init_config = f.readlines()
				### RENDERED_CONFIG IS A LIST OF ALL THE CONFIGS THAT WAS RENDERED FROM THE TEMPLATES (SOURCE OF TRUTH)
	
				for config_line in init_config:
					strip_config = config_line.strip('\n')
					### THIS WILL REMOVE ANY LINES THAT ARE EMPTY OR HAS A '!' MARK
					if(strip_config == '' or strip_config == "!"):
						continue	
					else:
						rendered_config.append(strip_config)	
				### THIS BELOW STATEMENT WILL CHECK TO SEE IF IT'S THE LAST TEMPLATE FOR THE NODE. IT WILL THEN APPEND 3 COMMANDS TO THE LIST
				if template_counter == len(template_list):
					rendered_config.append('\x04')
					rendered_config.append('show | compare')
					rendered_config.append('rollback 0')
	
				###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#				print ("RENDERED CONFIG: {}".format(rendered_config))
		### THE BELOW STATEMENT WILL ONLY EXECUTE IF USER IS AUDITING AGAINST MULTIPLE TEMPLATES. IF ONLY ONE TEMPLATE IS BEING AUDITED, DO NO POP OFF ELEMENT.
		if len(template_list) != 1:
			template_list = get_updated_list(template_list_copy)
		if(node_object[index]['platform'] == 'cisco'):
			redirect.append('get_config')
			command.append([''])
		### JUNIPER DEVICES WILL RECEIVE A DIFFERENT REDIRECT THAN CISCO PLATFORM
		### THREE ADDITIONAL COMMANDS ARE APPENEDED AT THE END, ^D, SHOW | COMPARE AND ROLLBACK 0
		### ALL TEMPLATES MATCHING ARE EXECUTED AT ONCE PER DEVICE
		elif(node_object[index]['platform'] == 'juniper'):
			redirect.append('get_diff')
			command.append(rendered_config)
			template_counter = 0
	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print('REDIRECT: {}'.format(redirect))
	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print('TEMPLATE_LIST: {}'.format(template_list))
#	print('COMMAND: {}'.format(command))
#	print("[+] [COMPUTING DIFF. STANDBY...]")
	multithread_engine(initialize.ntw_device,redirect,command)
	
	### RESETING TEMPLATE_LIST TO ORIGINAL LIST
	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print("ORIGINAL_LIST: {}".format(template_list_original))
	template_list = template_list_original
	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print("TEMPLATE_LIST: {}".format(template_list))
	### REINITIALIZING TEMPLATE_LIST TO THE ORIGINAL LIST OF TEMPLATES
	if(auditcreeper):
		template_list = template_list_original[0]
	### THIS FOR LOOP WILL LOOP THROUGH ALL THE MATCHED ELEMENTS FROM THE USER SEARCH AND AUDIT ON SPECIFIC TEMPLATE OR IF NO ARGUMENT IS GIVEN, ALL TEMPLATES
	
	for index in initialize.element:
		### INITIALIZING 'edit_list' FOR EACH NEW NODE IT CYCLES THROUGH
		edit_list = []
		### NODE_CONFIG IS THE FINALIZED CONFIG TO PUSH TO THE NODE FOR REMEDIATION
		node_configs = []
		ntw_device_pop = True 
		### TEMPLATE_NAME IS SET TO TRUE IN ORDER TO PRINT OUT THE TEMPLATE HEADING WHEN RECURSING
		template_name = True
		if(not remediation):
			print("Only in the device: -")
			print("Only in the generated config: +")
			print ("{}".format(node_object[index]['hostname']))
		### THIS WILL LOOP THROUGH ALL THE TEMPLATES SPECIFIED FOR THE PARTICULAR HOST IN TEMPLATES.YAML
		for template in template_list:
			### THIS SECTION IS FOR CISCO SYSTEMS PLATFORM ###
			if(node_object[index]['platform'] == 'cisco'):
				cisco_audit_diff(node_object,index,template,AUDIT_FILTER_RE,output,remediation)
	
			### THIS SECTION IS FOR JUNIPER NETWORKS PLATFORM ###
			if(node_object[index]['platform'] == 'juniper'):
				directory = get_template_directory(node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'])
				### THIS SECTION OF CODE WILL OPEN DIFF-CONFIG *.CONF FILE AND STORE IN DIFF_CONFIG AS A LIST
				f = open("{}/diff-configs/{}".format(home_directory,node_object[index]['hostname']) + ".conf", "r")
				init_config = f.readlines()
				### DIFF_CONFIG ARE THE DIFFERENTIAL CONFIGS GENERATED BY THE /DIFF-CONFIGS/*.CONF FILE 
				diff_config = []
	
				for config_line in init_config:
					strip_config = config_line.strip('\n')
					diff_config.append(strip_config)	
	
				###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#				print ("DIFF CONFIG: {}".format(diff_config))
				RE = re.compile(r'\[edit\s({})\]'.format(template.split('.')[0]))
				search = list(filter(RE.match,diff_config))
				if(len(search) == 0):
					print("{}{} (none)".format(directory,template))
					print('')
					no_diff = no_diff + 1
					if(no_diff == len(template_list)):
						break
					if(len(template_list) > 1):	
						juniper_audit_diff(directory,template,template_list,diff_config,edit_list,search)
					else:
						continue
						
				else:
					### THIS FIRST SECTION WILL FIND ALL THE INDEXES WITH THE '[edit <TEMPLATE>]' AND APPEND IT TO THE EDIT_LIST
					### EDIT_LIST MAINTAINS A LIST OF ALL THE INDEXES THAT PERTAIN TO THE TEMPLATES
					for line in diff_config:
						if(re.search('\[edit\s{}\]'.format(template.split('.')[0]),line)):
							element = diff_config.index(line) 
							edit_list.append(element)
							###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#							print('ELEMENT: {}'.format(element))
#							print("{}".format(line))
					###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#					print('EDIT_LIST 1st: {}'.format(edit_list))
#					print("index_of_template_list: {}".format(index_of_template_list))
#					print("length_template_list: {}".format(length_template_list))
					juniper_audit_diff(directory,template,template_list,diff_config,edit_list,search)
#					print("end_of_template_list: {}".format(end_of_template_list))
					### UPON THE LAST TEMPLATE, IT WILL THEN FIND THE CLOSING CURLY BRACES INDEX NUMBER TO APPEND TO THE EDIT_LIST
			print('')
		if(auditcreeper):
			initialize.configuration.append(node_configs)
			if(ntw_device_pop == True):
				initialize.ntw_device.pop(node_index)
				initialize.configuration.pop(node_index)
			template_list = get_updated_list(template_list_original)
#	if(remediation):
#		print("[+]: PUSH ENABLED")
#		print("[!]: PUSH DISABLED")
		
			
	return None
### PARSE_AUDIT_FILTER FUNCTION FILTERS OUT THE BACKUP_CONFIGS WITH THE AUDIT_FILTER
### THIS WILL TAKE EACH ELEMENT FROM THE AUDIT_FILTER LIST AND SEARCH FOR THE MATCHED LINES IN BACKUP_CONFIG
### MATCHED ENTRIES ARE THEN APPENDED TO FILTER_BACKUP_CONFIG VARIABLE AS A LIST AND RETURNED
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
def cisco_audit_diff(node_object,index,template,AUDIT_FILTER_RE,output,remediation):
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
def juniper_audit_diff(directory,template,template_list,diff_config,edit_list,search):
	length_template_list = len(template_list)
	index_of_template_list = template_list.index(template) + 1
	element = template_list.index(template)
	index_of_template_list = template_list.index(template) + 1
	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print('DIFF_CONFIG: {}'.format(diff_config))
#	print("EDIT_LIST: {}".format(edit_list))
	### THIS WILL CHECK IF IT'S ON THE LAST TEMPLATE. IF IT IS, IT WILL LOCATE THE LAST INDEX FOR EDIT_LIST AND APPEND IT TO THE LIST
	if(index_of_template_list == length_template_list):
		for line in diff_config:
			if(re.search('exit configuration-mode',line)):
				element = diff_config.index(line) 
				###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#				print('ELEMENT: {}'.format(element))
#				print("{}".format(line))
				### THE BELOW STATEMENT IS TO CHECK IF THE INDEX OF 'exit configuration-mode' IS LESS THEN OR EQUAL TO THE INDEX OF THE LAST ELEMENT OF THE EDIT_LIST.
				### THIS IS TO ENSURE THAT IT'S TAKING 'exit configuration-mode' FROM THE VERY END OF THE DIFF_CONFIG IN CASE 'exit configuration-mode' APPEARS IN THE 
				### MIDDLE OF DIFF_CONFIG.
				if(element<=edit_list[len(edit_list) - 1]):
					continue
				else:
					### THE COUNTER 6 IS TO DECREMENT THE INDEX '6' TIMES FROM THE 'exit configuration-mode'. THIS WILL LAND THE PIVOT POINT AT THE END OF THE DIFF.
					### THE LAST ELEMENT OF THE 'DIFF' IS NOW APPENDED TO THE EDIT_LIST, (ALL UNNECCESSARY INFO EX. SHOW | COMPARE, ROLLBACK 0 ETC... HAVE BEEN LEFT OUT
					### AND THEREFORE WE ARE ABLE TO FILTER OUT THE DIFF OUTPUT.
					element = element - 6 
					edit_list.append(element)
					break
		###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#		print('EDIT_LIST 2nd: {}'.format(edit_list))
		start = 0
		end = 1
		### THE LAST SECTION WILL PRINT THE APPROPREIATE DIFF BASED ON THE TEMPLATES FROM THE EDIT_LIST INFORMATION
#		print('TEMPLATE_LIST_JUNIPER: {}'.format(template_list_juniper))
#		print('DIFF_config: {}'.format(diff_config))
		for template in template_list: 
			RE = re.compile(r'\[edit\s({})\]'.format(template.split('.')[0]))
			search = list(filter(RE.match,diff_config))
			if(len(search) >= 1):
#				print("TEMPLATE: {}".format(template))
#				print("LENGTH OF SEARCH: {}.".format(search))
				print("{}{}".format(directory,template))
			for line in diff_config:
				if(re.search('\[edit\s{}\]'.format(template.split('.')[0]),line)):
					###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#					print "edit_list[start]: {}".format(edit_list[start])
#					print "edit_list[end]: {}".format(edit_list[end])
					diff_template = diff_config[edit_list[start]:edit_list[end]]  
					###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#					print('DIFF_TEMPLATE: {}'.format(diff_template))
					for line in diff_template:
						## THE BELOW IF STATEMENT IS TO CORRECT THE OUTPUT. AT RANDOM TIMES, THE DIFF-CONFIG MAY INCLUDE 'ROLLBACK 0' IN OUTPUT. IT WILL OMIT PRINTING THAT.
						if line == 'rollback 0':
							pass
						else:
							print("{}".format(line))
					print
				else:
					continue
				start = start + 1
				end = end + 1
