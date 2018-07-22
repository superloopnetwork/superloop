import re

index = 0
result = []

node_object = [{'username': 'admin', 'password': 'a2l0Y2hlbmVyMTA0Mg==', 'vendor': 'cisco', 'ip': '38.21.29.135', 'hostname': 'core-fw-superloop.ktch', 'type': 'firewall'}, {'username': 'admin', 'password': 'a2l0Y2hlbmVyMTA0Mg==', 'vendor': 'cisco', 'ip': '38.21.29.135', 'hostname': 'core.sw.superloop.ktch', 'type': 'firewall'}, {'username': 'admin', 'password': 'a2l0Y2hlbmVyMTA0Mg==', 'vendor': 'cisco', 'ip': '38.110.105.6', 'hostname': 'core.rt.superloop.wdstk', 'type': 'firewall'}, {'username': 'admin', 'password': 'a2l0Y2hlbmVyMTA0Mg==', 'vendor': 'cisco', 'ip': '38.110.105.6', 'hostname': 'core.sw.superloop.wdstk', 'type': 'firewall'}]


search = 'core.*sw'

r = re.compile(search)

for i in node_object:

	newlist = list(filter(r.match,node_object[index]['hostname']))
	result.append(newlist[0])

	index = index + 1

print result
