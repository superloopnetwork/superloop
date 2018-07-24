### THIS MODULE WILL GENERATE THE COMMANDS IN A FORM A LIST SO IT CAN BE
### FED INTO THE METHOD OF THE OBJECT CREATED.


def parse_commands():

	config_list = []

	configs = 'config.conf'

	f = open(configs)

	init_config = f.readlines()

	for config_line in init_config:
		strip_config = config_line.strip('\n')
		config_list.append(strip_config)

	return config_list
