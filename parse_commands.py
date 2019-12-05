### THIS MODULE WILL GENERATE THE COMMANDS IN A FORM A LIST SO IT CAN BE
### FED INTO THE METHOD OF THE OBJECT CREATED.
import initialize


def parse_commands(node_object,init_config):

	commands = initialize.configuration

	config_list = []

	if(node_object['platform'] == 'juniper'):
		config_list.append('load replace terminal')

	for config_line in init_config:
		strip_config = config_line.strip('\n')
		config_list.append(strip_config)

	if(node_object['platform'] == 'juniper'):
		config_list.append('\x04')

	commands.append(config_list)

	return commands
