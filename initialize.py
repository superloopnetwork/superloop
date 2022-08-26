"""
	This module define the global variables.
"""
def variables():
	global ntw_device
	global element
	global element_policy
	global configuration
	global rendered_config
	global backup_config
	global debug_element

	ntw_device = []
	templates = []
	element = []
	element_policy = []
	configuration = []
	rendered_config = []
	backup_config = []
	debug_element = []

	"""
		:param password: Only a single time use, per session of push_cfgs.py for Cisco like devices so users do not require to authenticate twice.
		:type password: str

		:param ntw_device: All matched nodes.
		:type ntw_device: list

		:param templates: All matched templates.
		:type templates: list

		:param element_policy: All elements of matched policies.
		:type element_policy: int

		:param configuration: Referenced to global variable configuration which keeps track of all commands per node.
		:type configuration: list

		:param rendered_config: Redered configurations from templates.
		:type rendered_config: list

		:param backup_config: Backup configuration from taken from devices.
		:type backup_config: list

		:param debug_element: Element number of device for when there are no diffs, then device gets popped off.
		:type debug_element: list
	"""
