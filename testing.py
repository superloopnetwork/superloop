#!/usr/bin/env python

from jinja2 import Environment, FileSystemLoader
import yaml
import argparse

def load_yaml(args):

	env = Environment(loader=FileSystemLoader('.'))
	
	baseline = env.get_template("access.jinja2")
	
	with open("nodes.yaml") as yaml_file:
		node_object = yaml.load(yaml_file)
		f = open('config.conf', 'w')
		config = baseline.render(nodes = node_object)
		f.write(config)
		f.close
	print config
#	print node_object


def push_config(args):
    print("pushing config to host: %s" % args.node)

def render_config(args):
    print("rendering config to host: %s" % args.file)

def diff():
	ls = subprocess.Popen('ls /mnt/syslog/**/*.log | wc -l', shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	list = ls.stdout.readline()
	list = list.strip('\n')
	diffcount = int(list)
	ls.kill()

	return devcount

def main():

	parser = argparse.ArgumentParser('superloop')
	subparsers = parser.add_subparsers()
	
	push_cmd = subparsers.add_parser('push')
	push_cmd.set_defaults(func=load_yaml)
	push_cmd.add_argument('-n','--node', dest='node')
	
	render_cmd = subparsers.add_parser('render')
	render_cmd.set_defaults(func=render_config)
	render_cmd.add_argument('-f','--file', dest='file')
	
	args = parser.parse_args()
	args.func(args)

if __name__ == '__main__':
    main()
