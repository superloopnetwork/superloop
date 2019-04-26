#!/usr/bin/env python


#from ssh import ssh
from auditdiff import auditdiff
from push_config import push_config
from render_config import render_config
from onscreen import onscreen 
from ssh_connect import ssh_connect
from hostadd import hostadd
import argparse
import os
import initialize

def main():


	os.system('clear')
	initialize.variables()

	parser = argparse.ArgumentParser('superloop')
	subparsers = parser.add_subparsers()

	push_cmd = subparsers.add_parser('auditdiff')
	push_cmd.set_defaults(func=auditdiff)
	push_cmd.add_argument('-n','--node', dest='node')
	push_cmd.add_argument('-f','--file', dest='file')

	push_cmd = subparsers.add_parser('push')
	push_cmd.set_defaults(func=push_config)
	push_cmd.add_argument('-n','--node', dest='node')
	push_cmd.add_argument('-f','--file', dest='file')
	
	render_cmd = subparsers.add_parser('render')
	render_cmd.set_defaults(func=render_config)
	render_cmd.add_argument('-n','--node', dest='node')
	render_cmd.add_argument('-f','--file', dest='file')
	
	onscreen_cmd = subparsers.add_parser('onscreen')
	onscreen_cmd.set_defaults(func=onscreen)
	onscreen_cmd.add_argument('-n','--node', dest='node')
	onscreen_cmd.add_argument('-c','--command', dest='command')

	ssh_cmd = subparsers.add_parser('ssh')
	ssh_cmd.set_defaults(func=ssh_connect)
	ssh_cmd.add_argument('-n','--node', dest='node')

#	hostadd_cmd = subparsers.add_parser('hostadd')
#	hostadd_cmd.set_defaults(func=hostadd)
#	hostadd.add_argument('-ip','--ip', dest='ip')

	args = parser.parse_args()
	args.func(args)

if __name__ == '__main__':
    main()
