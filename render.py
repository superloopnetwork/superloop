### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES

from jinja2 import Environment, FileSystemLoader

def render(args,node_object):

	env = Environment(loader=FileSystemLoader('.'))

	baseline = env.get_template(args.file)

	f = open('config.conf', 'w') 

	config = baseline.render(nodes = node_object) 

	f.write(config) 

	f.close 

	return config
