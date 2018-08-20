from processdb import process_nodes
from processdb import process_templates
from search import search_node
from search import search_template
from auditdiff_engine import auditdiff_engine
from node_create import node_create
import threading
import initialize

def auditcreeper():

	initialize.variables()
	controller = 'audit_diff'
	commands = initialize.configuration
	auditcreeper = True
	argument_node = '.+'
	template_list = []
	
	### NODE_OBJECT IS A LIST OF ALL THE NODES IN THE DATABASE WITH ALL ATTRIBUTES
	node_object = process_nodes()
	
	### NODE_TEMPLATE IS A LIST OF ALL THE TEMPLATES BASED ON PLATFORMS AND DEVICE TYPE
	node_template = process_templates()
	
	### MATCH_NODE IS A LIST OF NODES THAT MATCHES THE ARGUEMENTS PASSED IN BY USER
	match_node = search_node(argument_node,node_object)
	
	### MATCH_TEMPLATE IS A LIST OF 'MATCH' AND/OR 'NO MATCH' IT WILL USE THE MATCH_NODE
	### RESULT, RUN IT AGAINST THE NODE_OBJECT AND COMPARES IT WITH NODE_TEMPLATE DATABASE
	### TO SEE IF THERE IS A TEMPLATE FOR THE SPECIFIC PLATFORM AND TYPE.
	match_template = search_template(template_list,match_node,node_template,node_object,auditcreeper)
	node_create(match_node,node_object)
	auditdiff_engine(template_list,node_object,auditcreeper)

#	threading.Timer(60.0, audit_creeper).start()
#	print "Hello, World!"

if __name__ == "__main__":
	auditcreeper()
