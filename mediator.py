### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
### AND PACKAGES THEM INTO A LIST OF LISTS. IT ONLY LOOKS AT THE 
### SELECTED INDEXES (INIITIALIZE.ELEMENT) OF THE NODE_OBJECT. 
### THE CONFIGURATIONS ARE STORED IN THE GLOBAL VARIABLE CALL 
### INITIALIZE.CONFIGURATION.
from jinja2 import Environment, FileSystemLoader
from ciscoconfparse import CiscoConfParse
from multithread import multithread_engine
from lib.mediators.generic import generic_audit_diff
from lib.mediators.juniper import juniper_mediator
from lib.mediators.juniper import juniper_audit_diff
from get_property import get_template_directory
from get_property import get_location_directory
from get_property import get_updated_list
from get_property import get_syntax
from get_property import get_sorted_juniper_template_list 
import re
import initialize
import os

home_directory = os.environ.get('HOME')

def mediator(template_list,node_object,auditcreeper,output,remediation):
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
			get_platform_template_directory = get_template_directory(node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'])
			get_location_template_directory = get_location_directory(node_object[index]['hostname'],node_object[index]['platform'],node_object[index]['type'])
			env = Environment(loader=FileSystemLoader([get_platform_template_directory,get_location_template_directory]))
			baseline = env.get_template(template)
			f = open("{}/rendered-configs/{}.{}".format(home_directory,node_object[index]['hostname'],template.split('.')[0]) + ".conf", "w") 
			### GENERATING TEMPLATE BASED ON NODE OBJECT
			config = baseline.render(nodes = node_object[index])
			f.write(config) 
			f.close 
			if(node_object[index]['platform'] == 'cisco' or node_object[index]['platform'] == 'f5'):
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
		if(node_object[index]['platform'] == 'cisco' or node_object[index]['platform'] == 'f5'):
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

		if(not remediation):
			print("Only in the device: -")
			print("Only in the generated config: +")
			print ("{}".format(node_object[index]['hostname']))

#		print('template_list: {}'.format(template_list))
		### THIS WILL LOOP THROUGH ALL THE TEMPLATES SPECIFIED FOR THE PARTICULAR HOST IN TEMPLATES.YAML

		### THIS SECTION IS FOR CISCO SYSTEMS PLATFORM ###
		if node_object[index]['platform'] == 'cisco' or node_object[index]['platform'] == 'f5':
			generic_audit_diff(node_object,index,template,template_list,AUDIT_FILTER_RE,output,remediation)

		### THIS SECTION IS FOR JUNIPER NETWORKS PLATFORM ###
		elif node_object[index]['platform'] == 'juniper':
			template_list = get_sorted_juniper_template_list(template_list)
			directory = get_template_directory(node_object[index]['platform'],node_object[index]['opersys'],node_object[index]['type'])
			f = open("{}/diff-configs/{}".format(home_directory,node_object[index]['hostname']) + ".conf", "r")
			init_config = f.readlines()
			### DIFF_CONFIG ARE THE DIFFERENTIAL CONFIGS GENERATED BY THE /DIFF-CONFIGS/*.CONF FILE 
			diff_config = []

			for config_line in init_config:
				strip_config = config_line.strip('\n')
				diff_config.append(strip_config)

			juniper_mediator(node_object,template_list,diff_config,edit_list,index)
			juniper_audit_diff(directory,template_list,diff_config,edit_list)

		if(auditcreeper):
			initialize.configuration.append(node_configs)
			if(ntw_device_pop == True):
				initialize.ntw_device.pop(node_index)
				initialize.configuration.pop(node_index)
			template_list = get_updated_list(template_list_original)

	return None
