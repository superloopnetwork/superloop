"""
	This module define the global variables.
"""
def variables():
	### NTW_DEVICE IS A LIST OF THE MATCHED NODES
	global ntw_device

	### ELEMENT IS A LIST OF THE INDEXES OF ALL THE MATCHED NODES
	global element

	### ELEMENT_POLICY IS A LIST OF THE INDEXES OF ALL THE MATCHED POLICIES
	global element_policy

	### CONFIGURATION IS A LIST OF THE CONFIGS TO BE PUSHED TO DEVICE
	global configuration

	### RENDERED_CONFIG IS A LIST OF THE CONFIGS RENDERED FROM THE TEMPLATE
	global rendered_config

	### BACKUP_CONFIG IS A LIST OF CONFIGS CAPTURED FROM THE DEVICE AT THE TIME OF AUDIT DIFF
	global backup_config

	ntw_device = []
	templates = []
	element = []
	element_policy = []
	configuration = []
	rendered_config = []
	backup_config = []

	"""
		:param ntw_device: All matched nodes.
		:type ntw_device: list
		
		:param element: All indexes of matched nodes.
		:type element: int
		
		:param element_policy: All 
		:type element_policy: int

		:param commands: Referenced to global variable commands which keeps track of all commands per node.
		:type commands: list
		
		:param ext: File extention
		:type ext: str 
		
		:param output: Flag to output to stdout.  
		:type ext: bool 
		
		:param redirect: A list of which method superloop will access. This variable is sent to the multithread_engine. Each element is a redirect per node.
		:type alt_key_file: list
		
		:param with_remediation: Current function to remediate or not remediate.  
		:type ext: bool 
	"""
