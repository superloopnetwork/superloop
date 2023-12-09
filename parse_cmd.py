import ipaddress
import re
from processdb import process_json
from get_property import get_policy_directory


def parse_commands(node_object,init_config,set_notation):
	"""
		This function generates the commands in a form of a list so that
		it can be passed into the method of the object.
	"""
	commands = initialize.configuration
	config_list = []
	if node_object['hardware_vendor'] == 'juniper' and set_notation!=True:
		config_list.append('load replace terminal')
	elif node_object['hardware_vendor'] == 'f5':
		config_list.append('load sys config merge from-terminal')
	for config_line in init_config:
		strip_config = config_line.strip('\n')
		config_list.append(strip_config)
	if node_object['hardware_vendor'] == 'juniper' and set_notation!=True or node_object['hardware_vendor'] == 'f5':
		config_list.append('\x04')
	commands.append(config_list)

	return commands

def cisco_parse_negation_commands(remediate_missing):
	commands = []
	if len(remediate_missing) == 0:
		pass
	else:
		for negate in remediate_missing:
			if len(negate) == 1:
				remediate_missing_config = 'no ' + negate[0]
				commands.append(remediate_missing_config)
			else:
				commands.append(negate[0])
				for no_config in negate[1:]:
					if no_config[0].isspace():
						remediate_missing_config = 'no ' + no_config.lstrip()
					else:
						remediate_missing_config = 'no ' + no_config
					commands.append(remediate_missing_config)
	return commands

def citrix_parse_negation_commands(remediate_missing):
	remediate_missing = list(itertools.chain.from_iterable(remediate_missing))
	command_split = []
	commands = []
	for line in remediate_missing:
		command_split = line.split()
		"""
			The below if statement will negate binding configurations associated with policy on the Citrix Netscaler.
		"""
		if command_split[0] == 'bind' and command_split[1] == 'policy':
			command_split[0] = 'unbind'
			command = ' '.join(command_split[0:5])
			commands.append(command)
		elif command_split[0] == 'add' and command_split[1] == 'policy':
			command_split[0] = 'rm'
			command = ' '.join(command_split[0:4])
			commands.append(command)
		elif command_split[0] == 'add' and command_split[1] == 'server':
			command_split[0] = 'rm'
			command = ' '.join(command_split[0:3])
			commands.append(command)
		elif command_split[0] == 'add' and command_split[1] == 'service':
			command_split[0] = 'rm'
			command = ' '.join(command_split[0:3])
			commands.append(command)
		elif command_split[0] == 'bind' and command_split[1] == 'service':
			command_split[0] = 'unbind'
			command = ' '.join(command_split[0:3])
			commands.append(command)
		elif command_split[0] == 'add' and command_split[1] == 'serviceGroup':
			command_split[0] = 'rm'
			command = ' '.join(command_split[0:3])
			commands.append(command)
		elif command_split[0] == 'add' and command_split[1] == 'lb' and command_split[2] == 'vserver':
			command_split[0] = 'rm'
			command = ' '.join(command_split[0:4])
			commands.append(command)
		elif command_split[0] == 'bind' and command_split[1] == 'lb' and command_split[2] == 'vserver':
			command_split[0] = 'unbind'
			command = ' '.join(command_split[0:5])
			commands.append(command)
		elif command_split[0] == 'add' and command_split[1] == 'cs' and command_split[2] == 'vserver':
			command_split[0] = 'rm'
			command = ' '.join(command_split[0:4])
			commands.append(command)
		elif command_split[0] == 'bind' and command_split[1] == 'cs' and command_split[2] == 'vserver':
			command_split[0] = 'unbind'
			command = ' '.join(command_split[0:4])
			commands.append(command)
		elif command_split[0] == 'bind' and command_split[1] == 'ssl ' and command_split[2] == 'vserver':
			command_split[0] = 'unbind'
			command = ' '.join(command_split[0:4])
			commands.append(command)
		elif command_split[0] == 'set' and command_split[1] == 'ssl ' and command_split[2] == 'vserver':
			command_split[0] = 'unset'
			command = ' '.join(command_split[0:4])
			commands.append(command)
		else:
			commands.append(line)
		
	return commands
