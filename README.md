# superloop
Insprired by a wide array of toolsets (unamed) used and developed by a leading tech company for network automation, I have attempted to create my own version.

Prerequisite:
  1. netmiko - A HUGE thanks and shout out to Kirk Byers for developing the library!

Before we begin, I've constructed this application for easy database management by utilizing the power of YAML files. There consist of two YAML files that require management:

  1. nodes.yaml
  2. templates.yaml

nodes.yaml acts as the inventory for all network devices. It must follow the format defined below as the application reads it in a specific method.
```
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
```  
  Most fields are self explainatory except the password. The password is encrypted in base64 format so it's not visible in clear text. The easiest way to generate this hash is via the python interpreter. Assume your password is 'password':
```  
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
```
The password is only decrypted during the time the application connects to your device(s). For now, I've only built support for Cisco IOS as those are the only equipment I have for testing. I'll integrate more vendors over time.

templates.yaml is a database file that consist of all the jinja2 templates. You will need to include the full path. Here is a sample of how it should look like below. Do not change the format as the application reads it in a specific method. Only change the properties.
```
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
```
I've structured the hierarchy based on vendor, os and the type. You should do the same in order to keep your templates orderly. Whatever hierarchy you choose, you will need to update/modify in the directory.py file to reflect.

Let's look at a simple jinja2 template as an example.
```
root@jumpbox:~/superloop# cat /templates/cisco/ios/switch/hostname.jinja2 
{# audit_filter = ['hostname.*'] #}
hostname {{ nodes.hostname }}
```
Notice there is a section called 'audit_filter' at the top of file. This audit filter should be included in all templates. This tells superloop which lines to look for and compare against when rendering the configs. In other words, superloop will look for only lines that begin with 'hostname'

You may also have a template that consist of one or several levels deep like so.
```
root@jumpbox:~/superloop# cat /templates/cisco/ios/switch/dhcp.jinja2
{# audit_filter = ['ip dhcp.*'] #}

ip dhcp excluded-address 10.50.80.1
ip dhcp ping packets 5
!
ip dhcp pool DATA
 network 10.10.20.0 255.255.255.0
 default-router 10.10.20.1 
 dns-server 8.8.8.8 
``` 
Look at 'ip dhcp pool DATA'. The next line of config has an indentation. superloop is inteligent enough to render the remaining 3 lines of configs without having to include it into the audit_filter.
 
Now that I have explained the basic operations, onto the fun stuff!
 
First and foremost, I would like to introduce to you the 'auditdiff' function. This function was designed to compare against the jinja2 templates with your running-configurations to see if they are according to standards. You could imagine if you had hundreds, if not thousands of devices to maintain, standardization would be a nightmare without some form of auditing/automation tool. To paint you an example, say one day, little Amit decides to make an unauthorized manual configuration change on a switch. No one knows about it or what he did. superloop would be able to dive into the device and see if there were any discrepencies againist the template as that is considered the trusted source. If superloop senses a difference, it will provide you the option of remediating. Whatever little Amit decided to configure would essentially be removed without hassel. This works the other way around as well. If configuration(s) on a device(s) does not have the standard rendered configs from the template (configs removed), superloop will determine they are missing and you may proceed to remediate by pushing the rendered configs. 'auditdiff' will only audit againist one template at a time.
 
By leveraging the power of the auditdiff engine, I'm able to extend it's functionality by creating a creeper. The 'auditcreeper' would essentially audit all devices in the nodes.yaml file against ALL templates specified in templates.yaml file at a set interval. For example, I may set the 'auditcreeper' to check every 4 hours to ensure standardization. You may modify the timining in second in the auditcreeper.py file. Look for:

```threading.Timer(14400, auditcreeper).start()```

* 14400 seconds = 4 hours

For the sake of this example, I've narrowed down to 5 second to speed things up so you'll have an idea of how it works.

![superloop auditcreeper demo](https://github.com/superloopnetwork/superloop/blob/master/gifs/superloop_auditcreeper.gif)

In this demo, only one device gets remediated. A config was removed and a random config was added. superloop detected the discrepancies and proceeded to remediate:

```
- ip dhcp excluded-address 10.50.40.4
+ ip dhcp excluded-address 10.10.10.10
```

If there are multiple devices that require remediation, superloop handles remediation concurrently - meaning, superloop connects to all devices in parallel via multithreading.

The next features I developed was 'push' and 'onscreen'. 'push' is simplying pushing a template to a device(s). You may use regular expression in your query to match multiple nodes. This has proven to be very powerful and useful in an organized environment. The 'onscreen' features allow you to execute a command on the device(s) without requiring you to log in.

In the example below, the screen on the right is using 'push' and the screen on the left is using 'onscreen' to check the changes after.

![superloop push and onscreen demo](https://github.com/superloopnetwork/superloop/blob/master/gifs/superloop_push_onscreen_demo.gif)
