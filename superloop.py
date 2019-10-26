#!/usr/bin/env python
# VARIABLES LIKE "--node" OR "--file" ARE HOW IT'S BEING READ WHEN PASSED IN.
# args.node OR args.file IS HOW YOU REFER TO THE USER INPUT

#from ssh import ssh
from auditdiff import auditdiff
from push_cfgs import push_cfgs
from push_local import push_local
from render_config import render_config
from exec_command import exec_command 
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
	audit_subparser = audit_cmd.add_subparsers(dest='parser_audit')
	audit_diff_cmd = audit_subparser.add_parser('diff')
	audit_diff_cmd.set_defaults(func=auditdiff)
	audit_diff_cmd.add_argument('-n','--node', dest='node')
	audit_diff_cmd.add_argument('-f','--file', dest='file')
	audit_remediate_cmd = audit_subparser.add_parser('remediate')
	audit_remediate_cmd.set_defaults(func=auditdiff)
	audit_remediate_cmd.add_argument('-n','--node', dest='node')
	audit_remediate_cmd.add_argument('-f','--file', dest='file')

	push_cmd = subparsers.add_parser('push')
	push_subparsers = push_cmd.add_subparsers(dest='parser_push')
	push_render_cmd = push_subparsers.add_parser('render')
	push_render_cmd.set_defaults(func=render_config)
	push_render_cmd.add_argument('-n','--node', dest='node')
	push_render_cmd.add_argument('-f','--file', dest='file')
	push_cfgs_cmd = push_subparsers.add_parser('cfgs')
	push_cfgs_cmd.set_defaults(func=push_cfgs)
	push_cfgs_cmd.add_argument('-n','--node', dest='node')
	push_cfgs_cmd.add_argument('-f','--file', dest='file')
	push_local_cmd = push_subparsers.add_parser('local')
	push_local_cmd.set_defaults(func=push_local)
	push_local_cmd.add_argument('filename')
	push_local_cmd.add_argument('-n','--node', dest='node')
	
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
	host_exec_cmd = host_subparsers.add_parser('exec')
	host_exec_cmd.set_defaults(func=exec_command)
	host_exec_cmd.add_argument('argument')
	host_exec_cmd.add_argument('-n','--node', dest='node')

	node_cmd= subparsers.add_parser('node')
	node_subparsers = node_cmd.add_subparsers(dest='parser_node')
	node_list_cmd = node_subparsers.add_parser('list')
	node_list_cmd.set_defaults(func=node_list)
	node_list_cmd.add_argument('hostname')

	args = parser.parse_args()
	args.func(args)

if __name__ == '__main__':
    main()
