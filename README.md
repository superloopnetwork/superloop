# superloop
Insprired by a wide array of toolsets used and developed by Facebook for network automation, I have attempted to create my own version.

Before we begin, I've constructed this application for easy database management by utilizing the power of YAML files. There consist of two YAML files that require management:

  1. nodes.yaml
  2. templates.yaml

nodes.yaml acts as the inventory for all network devices. It must follow the format defined below as the application reads it in a specific method.

root@jumpbox:~/superloop# cat nodes.yaml 
---
- hostname: core-fw-superloop-toron
  ip: 10.10.10.10
  username: admin
  password: cGFzc3dvcmQ=
  platform: cisco
  os: ios
  type: firewall
- hostname: core.sw.superloop.sfran
  ip: 20.20.20.20  
  username: admin
  password: cGFzc3dvcmQ=
  platform: cisco
  os: ios
  type: switch 
- hostname: core.rt.superloop.sjose 
  ip: 30.30.30.30 
  username: admin
  password: cGFzc3dvcmQ=
  platform: cisco
  os: ios
  type: router
  
  Most fields are self explainatory except the password. The password is encrypted in base64 format so it's not visible in clear text. The easiest way to generate this hash is via the python interpreter. Assume your password is 'password':
  
  root@jumpbox:~/superloop# python
Python 2.7.6 (default, Nov 23 2017, 15:49:48) 
[GCC 4.8.4] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import base64
>>> password = 'password'
>>> encode = base64.b64encode(password)
>>> encode
'cGFzc3dvcmQ='
>>> 

The password is only decrypted during the time the application connects to your device(s). For now, I've only built support for Cisco IOS as those are the only equipment I have for testing. I'll integrate more vendors over time.

templates.yaml is a database file that consist of all the jinja2 templates. You will need to include the full path. Here is a sample of how it should look like below. Do not change the format as the application reads it in a specific method. Only change the properties.

root@jumpbox:~/superloop# cat templates.yaml 
---
- platform: cisco
  type: firewall
  os: ios
  templates:
  - /templates/cisco/ios/firewall/snmp.jinja2
  - /templates/cisco/ios/firewall/hostname.jinja2
- platform: cisco
  type: router 
  os: ios
  templates:
  - /templates/cisco/ios/router/hostname.jinja2
- platform: cisco
  type: switch 
  os: ios
  templates:
  - /templates/cisco/ios/switch/access.jinja2
  - /templates/cisco/ios/switch/services.jinja2
  - /templates/cisco/ios/switch/snmp.jinja2
  - /templates/cisco/ios/switch/hostname.jinja2
  - /templates/cisco/ios/switch/dhcp.jinja2

I've structured the hierarchy based on vendor, os and the type. You should do the same in order to keep your templates orderly.

Let's look at a simple jinja2 template as an example.

root@jumpbox:~/superloop# cat /templates/cisco/ios/switch/hostname.jinja2 
{# audit_filter = ['hostname.*'] #}
hostname {{ nodes.hostname }}

