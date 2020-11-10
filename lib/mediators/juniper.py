import re
import initialize
import os
from get_property import get_sorted_juniper_template_list 

home_directory = os.environ.get('HOME')

def juniper_mediator(node_object,template_list,diff_config,edit_list,index):

	for template in template_list:
		### THIS SECTION IS FOR JUNIPER NETWORKS PLATFORM ###
	
		###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
	#	print ("DIFF CONFIG: {}".format(diff_config))
	
		### THIS FIRST SECTION WILL FIND ALL THE INDEXES WITH THE '[edit <TEMPLATE>]' AND APPEND IT TO THE EDIT_LIST
		### EDIT_LIST MAINTAINS A LIST OF ALL THE INDEXES THAT PERTAIN TO THE TEMPLATES
		for line in diff_config:
			if re.search('\[edit\s{}'.format(template.split('.')[0]),line):
				element = diff_config.index(line) 
				edit_list.append(element)
				break
			elif re.search('\+\s\s{}\s'.format(template.split('.')[0]),line):
				element = diff_config.index(line) 
				edit_list.append(element)
				break
			else:
				continue
				###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
				print('ELEMENT: {}'.format(element))
				print("{}".format(line))
		###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#		print('EDIT_LIST 1st: {}'.format(edit_list))
#		print("index_of_template_list: {}".format(index_of_template_list))
#		print("length_template_list: {}".format(length_template_list))
#		edit_list.sort()
	
				
	return edit_list 

def juniper_audit_diff(directory,template_list,diff_config,edit_list):

	template_list = get_sorted_juniper_template_list(template_list)

#	for element in edit_list:
#		if element not in no_duplicate_edit_list:
#			no_duplicate_edit_list.append(element)
#
#	edit_list = no_duplicate_edit_list[:]

	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print('DIFF_CONFIG: {}'.format(diff_config))
#	print("EDIT_LIST: {}".format(edit_list))
	### THIS WILL CHECK IF IT'S ON THE LAST TEMPLATE. IF IT IS, IT WILL LOCATE THE LAST INDEX FOR EDIT_LIST AND APPEND IT TO THE LIST
#	if(index_of_template_list == length_template_list):
	for line in diff_config:
		if(re.search('exit configuration-mode',line)):
			element = diff_config.index(line) 
			###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#			print('ELEMENT: {}'.format(element))
#			print("{}".format(line))
			### THE BELOW STATEMENT IS TO CHECK IF THE PIVOT POINT (INDEX)IS LESS THEN OR EQUAL TO THE INDEX OF THE LAST ELEMENT OF THE EDIT_LIST. IF IT'S LESS THAN
			### OR EQUAL TO, IT KNOWS THAT IT HAS NOT REACHED PASSED THE LAST INDEX OF EDIT_LIST (LAST ELEMENT). THEREFORE PIVOT POINT MUST BE GREATER TO KNOW IT'S THE
			### END
#			if(element<=edit_list[len(edit_list) - 1]):
#				continue
#			else:
				### THE COUNTER 6 IS TO DECREMENT THE INDEX '6' TIMES FROM THE 'exit configuration-mode'. THIS WILL LAND THE PIVOT POINT AT THE END OF THE DIFF.
				### THE LAST ELEMENT OF THE 'DIFF' IS NOW APPENDED TO THE EDIT_LIST, (ALL UNNECCESSARY INFO EX. SHOW | COMPARE, ROLLBACK 0 ETC... HAVE BEEN LEFT OUT
				### AND THEREFORE WE ARE ABLE TO FILTER OUT THE DIFF OUTPUT.
			element = element - 6 
			edit_list.append(element)
			break
	###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#	print('EDIT_LIST FINAL: {}'.format(edit_list))
	start = 0
	end = 1
	### THE LAST SECTION WILL PRINT THE APPROPREIATE DIFF BASED ON THE TEMPLATES FROM THE EDIT_LIST INFORMATION
#	print('TEMPLATE_LIST: {}'.format(template_list))
#	print('DIFF_config: {}'.format(diff_config))


	for template in template_list: 
#		if(len(search) >= 1):
#			print("TEMPLATE: {}".format(template))
#			print("LENGTH OF SEARCH: {}.".format(search))
		for line in diff_config:
			### SATISFY CONDITION WHEN THERE IS A DIFF AND CONFIGURATION STANZA EXIST ON DEVICE AND IN TEMPLATE
			if(re.search('\[edit\s{}'.format(template.split('.')[0]),line)):
				juniper_diff_output(diff_config,directory,template,edit_list,start,end)
				start = start + 1
				end = end + 1
				break
				###UN-COMMENT THE BELOW PRINT STATEMENT FOR DEBUGING PURPOSES
#				print('DIFF_TEMPLATE: {}'.format(diff_template))
			### SATISFY CONDITION WHEN CONFIGURATION DOESN'T CURRENTLY EXIST ON DEVICE BUT ONLY IN TEMPLATE
			elif re.search('\+\s\s{}\s'.format(template.split('.')[0]),line):
				juniper_diff_output(diff_config,directory,template,edit_list,start,end)
				start = start + 1
				end = end + 1
				break
			### SATISFY CONDITION WHEN THERE ARE NO DIFFS FOUND. LENGTH OF EDIT_LIST IS EQUAL TO 1 AS '' (BLANK) [MINUS 6 INDEX FROM 'exit configuration-mode' 
			### WILL BE THE ONLY ELEMENT IN THE LIST.
			elif len(edit_list) == 1:
				print("{}{} (none)".format(directory,template))
				break
			### SATISFY CONDITION WHEN THERE ARE NO DIFFS FOUND AND THE LINE BEING EVALUATED REACHES THE END OF THE DIFF_CONFIG. IT THEN KNOWS THERE 
			### ARE NO MATCHES. 
			else:
				if diff_config.index(line) == len(diff_config):
					print("{}{} (none)".format(directory,template))
				pass

#			start = start + 1
#			end = end + 1

def juniper_diff_output(diff_config,directory,template,edit_list,start,end):

	diff_template = diff_config[edit_list[start]:edit_list[end]]  
	print("{}{}".format(directory,template))
	for line in diff_template:
		## THE BELOW IF STATEMENT IS TO CORRECT THE OUTPUT. AT RANDOM TIMES, THE DIFF-CONFIG MAY INCLUDE 'ROLLBACK 0' IN OUTPUT. IT WILL OMIT PRINTING THAT.
		if line == '[edit]':
			pass
		else:
			print("{}".format(line))
	print()
