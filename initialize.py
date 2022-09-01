"""
	This module define the global variables.
"""
def variables():
	global backup_config
	global compliance_percentage
	global configuration
	global debug_element 
	global element
	global element_policy
	global netscaler_ha
	global ntw_device
	global password
	global rendered_config

	backup_config = []
	compliance_percentage = 0
	configuration = []
	debug_element = []
	element = []
	element_policy = []
	netscaler_ha = []
	ntw_device = []
	password = ''
	rendered_config = []

	"""
		:param backup_config: Backup configuration from taken from devices.
		:type backup_config: list
		:param compliance_percentage: This keeps track of the percentage of code compliance from our templates with respect to our running configurations.
		:type configuration: int
		:param configuration: Referenced to global variable configuration which keeps track of all commands per node.
		:type configuration: list
		:param debug_element: Element number of device for when there are no diffs, then device gets popped off.
		:type debug_element: list
		:param element_policy: All elements of matched policies.
		:type element_policy: int
		:param netscaler_ha: All matched nodes.
		:type netscaler_ha: list
		:param element: The element number of the match device(s) from the list of nodes.
		:type element: list
		:param element_policy: The element number of the match policy from the list of polcies.
		:type element_policy: list
		:param ntw_device: All matched nodes.
		:type ntw_device: list
		:param password: Only a single time use, per session of push_cfgs.py for Cisco like devices so users do not require to authenticate twice.
		:type password: str
		:param rendered_config: Rendered configurations from templates.
		:type rendered_config: list
	"""
