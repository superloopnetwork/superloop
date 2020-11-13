"""
	THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES
	AND PACKAGES THEM INTO A LIST OF LISTS. IT ONLY LOOKS AT THE 
	SELECTED INDEXES (INIITIALIZE.ELEMENT) OF THE NODE_OBJECT. 
	THE CONFIGURATIONS ARE STORED IN THE GLOBAL VARIABLE CALL 
	INITIALIZE.CONFIGURATION.
"""
from jinja2 import Environment, FileSystemLoader
from ciscoconfparse import CiscoConfParse
from render import process_jinja2_template 
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

def mediator(template_list,node_object,auditcreeper,output,with_remediation):
	redirect = [] 
	command = [] 
	template_counter = 0
	node_index = 0 
	AUDIT_FILTER_RE = r'\[.*\]'
	template_list_original = template_list[:]
	template_list_copy = template_list

	"""
	:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
	:type alt_key_file: list
	
	:param command: A list within a list where each element represents per node of commands to execute.
	:type command: list
	
	:param template_counter: Used to keep track of the number of templates it cycles through for Juniper.
	:type template_counter: int
	
	:param node_index: Keeps track of the index in initialize.ntw_device. If remediation is not required (configs matches template), then the node is popped of       initialize.ntw_device and nothing is changed on that device.
	:type node_index: int
	
	:param AUDIT_FILTER_RE: Regular expression to filter out the audit filter in every template.
	:type AUDIT_FILTER_RE: str
	
	:param template_list_original: Take a duplicate copy of template_list
	:type template_list_original: list
	
	:param template_list_copy: Memory reference to template_list
	:type template_list_copy: list
	
	"""
	"""
	The mediator is broken up into two sections. The first section of code will gather all rendered configs first as it's required for all platforms 
	(Cisco, Juniper & F5). Juniper does not require backup-configs in order to be diff'ed. The diff is server (node) side processed and the results 
	are returned back to superloop. Cisco platforms will require backup-configs (get_config) where the diffs are processed locally.
	"""
	if auditcreeper:
		template_list = template_list_copy[0]
	for index in initialize.element:
		rendered_config = []
		if node_object[index]['platform'] == 'juniper':
			"""
                Juniper's diff output are always in a certain stanza order. 
                The template_list ordered processed may very well not be in the 
                same order as Juniper's. In order to keep it consistent, we must 
                call the function get_sorted_juniper_template() and it will 
                return a sorted Juniper's stanza list.
			"""
			template_list = get_sorted_juniper_template_list(template_list)
			rendered_config.append('load replace terminal')
		for template in template_list:
			process_jinja2_template(node_object,index,template,with_remediation)
			"""
				Compiling the rendered configs from template and preparing
				for pushing to node.
			"""
			if(node_object[index]['platform'] == 'juniper'):
				template_counter = template_counter + 1
				f = open("{}/rendered-configs/{}.{}".format(home_directory,node_object[index]['hostname'],template.split('.')[0]) + ".conf", "r")
				init_config = f.readlines()
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

		if(not with_remediation):
			print("Only in the device: -")
			print("Only in the generated config: +")
			print ("{}".format(node_object[index]['hostname']))

#		print('template_list: {}'.format(template_list))
		### THIS WILL LOOP THROUGH ALL THE TEMPLATES SPECIFIED FOR THE PARTICULAR HOST IN TEMPLATES.YAML

		### THIS SECTION IS FOR CISCO SYSTEMS PLATFORM ###
		if node_object[index]['platform'] == 'cisco' or node_object[index]['platform'] == 'f5':
			generic_audit_diff(node_object,index,template,template_list,AUDIT_FILTER_RE,output,with_remediation)

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
