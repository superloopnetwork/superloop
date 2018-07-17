### THIS MODULE RENDERS THE TEMPLATES FROM THE JINJA2 FILES

from jinja2 import Environment, FileSystemLoader

def render(node_object):

	env = Environment(loader=FileSystemLoader('.'))

	baseline = env.get_template("access.jinja2")

	f = open('config.conf', 'w') 

	config = baseline.render(nodes = node_object) 

	f.write(config) 

	f.close 

	print config
