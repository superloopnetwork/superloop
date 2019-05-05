### THIS MODULE ALLOWS THE SSH SESSION FOR USERS.
### NODE_OBJECT IS A LIST OF DICTIONARY COMPILED BY THE 
### PROCESSDB MODULE. IT PROCESSES THE INFORMATION FROM THE
### NODES.YAML FILE AND STORES IT INTO A LIST OF DICTIONARY.
from snmp import snmp
from modifydb import append 
import yaml

def hostadd(args):

	argument_node = args.ip

	device = snmp(argument_node)
	append(device)
