#!/usr/bin/env python3
""" 
	Main executable file for superloop. A symbolic link should be created as a global command for ease of use.	
"""
import sys
import argparse
import initialize
import os
from acl_config import acl_config
from auditdiff import auditdiff
from pull_cfgs import pull_cfgs
from push_cfgs import push_cfgs
from push_local import push_local
from push_acl import push_acl
from render_config import render_config
from exec_cmd import exec_cmd 
from ssh_connect import ssh_connect
from modifydb import append
from modifydb import discover 
from modifydb import remove 
from modifydb import update 
from node_list import node_list

sys.path.append('/root/superloop/')

def main():
#	try:
	initialize.variables()
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()


	acl_cmd = subparsers.add_parser('acl')
	acl_subparsers = acl_cmd.add_subparsers(dest='parser_acl')
	acl_render_cmd = acl_subparsers.add_parser('render')
	acl_render_cmd.set_defaults(func=acl_config)
	acl_render_cmd.add_argument('-n','--node', dest='node', help='Specify node(s) to match against. Accepts regular expressions.')

	audit_cmd = subparsers.add_parser('audit')
	audit_subparser = audit_cmd.add_subparsers(dest='parser_audit')
	audit_diff_cmd = audit_subparser.add_parser('diff')
	audit_diff_cmd.set_defaults(func=auditdiff)
	audit_diff_cmd.add_argument('-n','--node', dest='node', help='Specify node(s) to match against. Accepts regular expressions.' )
	audit_diff_cmd.add_argument('-f','--file', dest='file', help='Specify template file to audit against [exclude *.jinja2 extension].')

	pull_cmd = subparsers.add_parser('pull')
	pull_subparsers = pull_cmd.add_subparsers(dest='parser_pull')
	pull_cfgs_cmd = pull_subparsers.add_parser('cfgs')
	pull_cfgs_cmd.set_defaults(func=pull_cfgs)
	pull_cfgs_cmd.add_argument('-n','--node', dest='node', help='Specify node(s) to match against. Accepts regular expressions.')
	pull_cfgs_cmd.add_argument('-c','--confirm', dest='confirm', help='Skip confirmation [default is True].')

	push_cmd = subparsers.add_parser('push')
	push_subparsers = push_cmd.add_subparsers(dest='parser_push')
	push_render_cmd = push_subparsers.add_parser('render')
	push_render_cmd.set_defaults(func=render_config)
	push_render_cmd.add_argument('-n','--node', dest='node', help='Specify node(s) to match against. Accepts regular expressions.')
	push_render_cmd.add_argument('-f','--file', dest='file', help='Specify template file to audit against [exclude *.jinja2 extension].')
	push_cfgs_cmd = push_subparsers.add_parser('cfgs')
	push_cfgs_cmd.set_defaults(func=push_cfgs)
	push_cfgs_cmd.add_argument('-n','--node', dest='node', help='Specify node(s) to match against. Accepts regular expressions.')
	push_cfgs_cmd.add_argument('-f','--file', dest='file', help='Specify template file to audit against [exclude *.jinja2 extension].')
	push_cfgs_cmd.add_argument('-c','--confirm', dest='confirm', help='Skip confirmation [default is True].')
	push_local_cmd = push_subparsers.add_parser('local')
	push_local_cmd.set_defaults(func=push_local)
	push_local_cmd.add_argument('filename', help='Specify local filename to be pushed.')
	push_local_cmd.add_argument('-n','--node', dest='node', help='Specify node(s) to match against. Accepts regular expressions.')
	push_acl_cmd = push_subparsers.add_parser('acl')
	push_acl_cmd.set_defaults(func=push_acl)
	push_acl_cmd.add_argument('-n','--node', dest='node', help='Specify node(s) to match against. Accepts regular expressions.')
	push_acl_cmd.add_argument('-p','--policy', dest='policy', help='Specify the policy file to match against [exclude *.json extension].')
	
	ssh_cmd = subparsers.add_parser('ssh')
	ssh_cmd.set_defaults(func=ssh_connect)
	ssh_cmd.add_argument('name', help='Specify name(s) to match against. Accepts regular expressions.')

	host_cmd= subparsers.add_parser('host')
	host_subparsers = host_cmd.add_subparsers(dest='parser_host')
	host_add_cmd = host_subparsers.add_parser('add', help='Add node to database')
	host_add_cmd.set_defaults(func=append)
	host_add_cmd.add_argument('node', help='Specify IP address of host')
	host_discover_cmd = host_subparsers.add_parser('discover', help='Re-discover existing node from database')
	host_discover_cmd.set_defaults(func=discover)
	host_discover_cmd.add_argument('node', help='Specify FQDN or IP address of host')
	host_remove_cmd = host_subparsers.add_parser('remove', help='Remove node from database')
	host_remove_cmd.set_defaults(func=remove)
	host_remove_cmd.add_argument('node')
	host_update_cmd = host_subparsers.add_parser('update', help='Update node attribute in database')
	host_update_cmd.set_defaults(func=update)
	host_update_cmd.add_argument('node')
	host_update_cmd.add_argument('-a','--attribute', dest='attribute', help='Specify the attribute that requires updating')
	host_update_cmd.add_argument('-am','--amend', dest='amend', help='The value that is being amended')
	host_exec_cmd = host_subparsers.add_parser('exec')
	host_exec_cmd.set_defaults(func=exec_cmd)
	host_exec_cmd.add_argument('command', help='Specify command to execute on device')
	host_exec_cmd.add_argument('-n','--node', dest='node', help='Specify node(s) to match against. Accepts regular expressions.')

	node_cmd= subparsers.add_parser('node')
	node_subparsers = node_cmd.add_subparsers(dest='parser_node')
	node_list_cmd = node_subparsers.add_parser('list')
	node_list_cmd.set_defaults(func=node_list)
	node_list_cmd.add_argument('name', help='Specify name(s) to match again. Accepts regular expressions.')
	node_list_cmd.add_argument('-e','--extended', dest='attribute', help='Specify extended option for additional attributes. {ports|protocols}')

	args = parser.parse_args()
	args.func(args)
#	except AttributeError as error:
#			print('Please check help menu for further operations; superloop --help')

if __name__ == '__main__':
    main()
