"""
	This module displays the attributes of the searched node(s) in 
	dictionary format. 
"""
import initialize
from processdb import process_nodes
from processdb import process_templates
from search import node_element
from search import search_node
from search import search_template
from node_create import node_create
from get_property import get_updated_list

def node_list(args):
	argument_node = args.name
	auditcreeper = True
	element_position = 1
	push_cfgs = False
	safe_push_list = []
	template_list = []
	template_list_copy = template_list
	"""
		:param argument_node: Argument accepted as regular expression.
		:type augument_node: str
		
		:param auditcreeper: When auditcreeper is active/non-active.
		:type auditcreeper: bool
		
		:param element_position: Keeps track of the position.
		:type element_position: int

		:param push_cfgs: This flag is to determine if a push is required for Cisco like platforms. Juniper will continue to push configs no matter if there are no diffs.
		:type ext: bool

		:param safe_push_list: A list of enable/disabled strings. This corresponds to templates that are safe to push (enable) vs. templates that are not safe to push (disabled).
		:type ext: list
		
		:param template_list: Initializing list of templates.
		:type template_list: list
		
		:param template_list_copy: Memory reference to template_list.
		:type ext: list
		
	"""
	node_object = process_nodes()
	match_node = search_node(argument_node,node_object)
	node_template = process_templates()
	match_template = search_template(template_list,safe_push_list,match_node,node_template,node_object,auditcreeper,push_cfgs)
	"""
		:param node_object: All node(s) in the database with all attributes.
		:type node_object: list

		:param node_template: All templates based on hardware_vendor and device type.
		:type node_template: list

		:param match_node: Nodes that matches the arguements passed in by user.
		:type match_node: list

		:param match_template: Return a list of 'match' and/or 'no match'.
		:type match_template: list 
	"""
	if len(match_node) == 0:
		print('+ No matching node(s) found in database.')
		print('')
	else:
		print('[')
		template_list = template_list_copy[0]
		for index in initialize.element:
			print('    {')
			if(args.attribute == 'protocols' or args.attribute == 'all'):
				print("\t\"bgp\": [")
				for peer in node_object[index]['bgp']:
					print("\t   {")
					print("\t\t\"peer\": \"{}\"\n" \
					  	  "\t\t\"remote_as\": \"{}\"" \
							.format(peer['peer'],
									peer['remote_as']
								)
					)
					print("\t   },")
					print('        ]')
			print("\t\"created_at\": \"{}\"\n" \
				  "\t\"created_by\": \"{}\"" \
					.format(node_object[index]['created_at'],node_object[index]['created_by'])
					)
			print("\t\"data\": {\n" \
				  "\t    \"managed_configs\": {" \
					)
			for template in template_list:
				print("\t\t   \"{}\"".format(template))
			print('\t     }')
			print('         }')
			print("\t\"domain_name\": \"{}\"\n" \
				  "\t\"hardware_vendor\": \"{}\"\n" \
				  "\t\"lifecycle_status\": \"{}\"\n" \
				  "\t\"location_name\": \"{}\"\n" \
				  "\t\"mgmt_con_ip4\": \"{}\"\n" \
				  "\t\"mgmt_ip4\": \"{}\"\n" \
				  "\t\"mgmt_oob_ip4\": \"{}\"\n" \
				  "\t\"mgmt_snmp_community4\": \"{}\"\n" \
				  "\t\"name\": \"{}\"\n" \
				  "\t\"opersys\": \"{}\"" \
					.format(node_object[index]['domain_name'],
							node_object[index]['hardware_vendor'],
							node_object[index]['lifecycle_status'],
							node_object[index]['location_name'],
							node_object[index]['mgmt_con_ip4'],
							node_object[index]['mgmt_ip4'],
							node_object[index]['mgmt_oob_ip4'],
							node_object[index]['mgmt_snmp_community4'],
							node_object[index]['name'],
							node_object[index]['opersys'],
					)
			)
			if(args.attribute == 'protocols' or args.attribute == 'all'):
				print("\t\"ospf\": [")
				for peer in node_object[index]['ospf']:
					print("\t   {")
					print("\t\t\"neighbor_id\": \"{}\"\n" \
					  	  "\t\t\"area\": \"{}\"\n" \
					  	  "\t\t\"priority: \"{}\"\n" \
					  	  "\t\t\"state: \"{}\"" \
							.format(peer['neighbor_id'],
									peer['area'],
									peer['priority'],
									peer['state']
								)
					)
					print("\t   },")
					print('        ]')
			print("\t\"platform_name\": \"{}\"" \
				.format(node_object[index]['platform_name']
					)
			)
			if(args.attribute == 'ports' or args.attribute == 'all'):
				print("\t\"ports\": [")
				for interface in node_object[index]['ports']:
					print("\t   {")
					print("\t\t\"access_vlan\": \"{}\"\n" \
					  	  "\t\t\"acl4_in\": \"{}\"\n" \
					  	  "\t\t\"acl4_out: \"{}\"\n" \
					  	  "\t\t\"admin_status: \"{}\"\n" \
					  	  "\t\t\"created_at: \"{}\"\n" \
					  	  "\t\t\"created_by: \"{}\"\n" \
					  	  "\t\t\"data: \"{}\"\n" \
					  	  "\t\t\"drain_status: \"{}\"\n" \
					  	  "\t\t\"farend_name: \"{}\"\n" \
					  	  "\t\t\"if_speed: \"{}\"\n" \
					  	  "\t\t\"ip4: \"{}\"\n" \
					  	  "\t\t\"management: \"{}\"\n" \
					  	  "\t\t\"mtu: \"{}\"\n" \
					  	  "\t\t\"name: \"{}\"\n" \
					  	  "\t\t\"node_name: \"{}\"\n" \
					  	  "\t\t\"portrole_name: \"{}\"\n" \
					  	  "\t\t\"type: \"{}\"\n" \
					  	  "\t\t\"updated_at: \"{}\"\n" \
					  	  "\t\t\"updated_by: \"{}\"\n" \
					  	  "\t\t\"wan_link: \"{}\"" \
							.format(interface['access_vlan'],
									interface['acl4_in'],
									interface['acl4_out'],
									interface['admin_status'],
									interface['created_at'],
									interface['created_by'],
									interface['data'],
									interface['drain_status'],
									interface['farend_name'],
									interface['if_speed'],
									interface['ip4'],
									interface['management'],
									interface['mtu'],
									interface['name'],
									interface['node_name'],
									interface['portrole_name'],
									interface['type'],
									interface['updated_at'],
									interface['updated_by'],
									interface['wan_link']
							)
				)
				print("\t   },")
				print('        ]')
			print("\t\"role_name\": \"{}\"\n" \
				  "\t\"serial_num\": \"{}\"\n" \
				  "\t\"software_image\": \"{}\"\n" \
				  "\t\"software_version\": \"{}\"\n" \
                  "\t\"status\": \"{}\"\n" \
				  "\t\"type\": \"{}\"\n" \
                  "\t\"updated_at\": \"{}\"\n" \
                  "\t\"updated_by\": \"{}\"" \
					.format(node_object[index]['role_name'],
							node_object[index]['serial_num'],
							node_object[index]['software_image'],
							node_object[index]['software_version'],
							node_object[index]['status'],
							node_object[index]['type'],
							node_object[index]['updated_at'],
							node_object[index]['updated_by']
					)
			)
			template_list = get_updated_list(template_list_copy)
			if element_position == len(initialize.element):
				print('    }')
			else:
				print('    },')
			element_position = element_position + 1
		print(']')

	return None
