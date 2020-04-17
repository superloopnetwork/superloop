
def variables():

	### NTW_DEVICE IS A LIST OF THE MATCHED NODES
	global ntw_device

	### TYPE IS A LIST OF THE MATCH NODE'S TYPE (FIREWALL, SWITCH OR ROUTER)
	global templates 

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
