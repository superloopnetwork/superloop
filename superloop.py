#!/usr/bin/env python
# VARIABLES LIKE "--node" OR "--file" ARE HOW IT'S BEING READ WHEN PASSED IN.
# args.node OR args.file IS HOW YOU REFER TO THE USER INPUT

#from ssh import ssh
from auditdiff import auditdiff
from push_config import push_config
from render_config import render_config
from onscreen import onscreen 
from ssh_connect import ssh_connect
from modifydb import append
from modifydb import remove 
from node_list import node_list
import argparse
import os
import initialize

def main():


	os.system('clear')
	initialize.variables()

	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()

	audit_cmd = subparsers.add_parser('audit')
	audit_subparser = audit_cmd.add_subparsers(dest='parser_host')
	audit_diff_cmd = audit_subparser.add_parser('diff')
	audit_diff_cmd.set_defaults(func=auditdiff)
	audit_diff_cmd.add_argument('-n','--node', dest='node')
	audit_diff_cmd.add_argument('-f','--file', dest='file')

	push_cmd = subparsers.add_parser('auditdiff')
	push_cmd.set_defaults(func=auditdiff)

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
	ssh_cmd.add_argument('hostname')

	host_cmd= subparsers.add_parser('host')
	host_subparsers = host_cmd.add_subparsers(dest='parser_host')
	host_add_cmd = host_subparsers.add_parser('add')
	host_add_cmd.set_defaults(func=append)
	host_add_cmd.add_argument('ip')
	host_remove_cmd = host_subparsers.add_parser('remove')
	host_remove_cmd.set_defaults(func=remove)
	host_remove_cmd.add_argument('argument')

	node_cmd= subparsers.add_parser('node')
	node_subparsers = node_cmd.add_subparsers(dest='parser_node')
	node_list_cmd = node_subparsers.add_parser('list')
	node_list_cmd.set_defaults(func=node_list)
	node_list_cmd.add_argument('hostname')

	args = parser.parse_args()
	args.func(args)

if __name__ == '__main__':
    main()
