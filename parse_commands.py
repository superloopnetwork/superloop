### THIS MODULE WILL GENERATE THE COMMANDS IN A FORM A LIST SO IT CAN BE
### FED INTO THE METHOD OF THE OBJECT CREATED.
import initialize


def parse_commands(init_config):

	commands = initialize.configuration

	config_list = []

	for config_line in init_config:
		strip_config = config_line.strip('\n')
		config_list.append(strip_config)

	commands.append(config_list)

	return commands
