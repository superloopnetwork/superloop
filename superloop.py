#!/usr/bin/env python

from push_config import push_config
from render_config import render_config
import argparse
import os
import initialize

def main():


	os.system('clear')
	initialize.variables()

	parser = argparse.ArgumentParser('superloop')
	subparsers = parser.add_subparsers()
	
	push_cmd = subparsers.add_parser('push')
	push_cmd.set_defaults(func=push_config)
	push_cmd.add_argument('-n','--node', dest='node')
	push_cmd.add_argument('-f','--file', dest='file')
	
	render_cmd = subparsers.add_parser('render')
	render_cmd.set_defaults(func=render_config)
	render_cmd.add_argument('-n','--node', dest='node')
	render_cmd.add_argument('-f','--file', dest='file')
	
	args = parser.parse_args()
	args.func(args)

if __name__ == '__main__':
    main()
