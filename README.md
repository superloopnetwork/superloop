# superloop
Inspired by a wide array of toolsets (unamed) used and developed by a leading social media tech company in the Bay Area for network automation, I have created my own version of framework.

## Prerequisites
  1. Python 3.6 or higher.
  2. netmiko - A HUGE thanks and shout out to Kirk Byers for developing the library!
  3. snmp_helper.py - module written by Kirk Byers (https://github.com/ktbyers/pynet/blob/master/snmp/snmp_helper.py).
  4. ciscoconfparse - A library to help parse out Cisco (or similiar) CLI configs (https://pypi.org/project/ciscoconfparse/).
  5. yaml - YAML is a human-readable data-serialization language (https://en.wikipedia.org/wiki/YAML).
  6. jinja2 - template engine for Python (https://jinja.palletsprojects.com/en/2.11.x/)

## Support

|__Platform__|__audit diff__|__push cfgs__|__host exec__|__ssh__ |__node list__|__host add__|__host remove__|__push acl__|__pull cfgs__|
|------------|:------------:|:-----------:|:-----------:|:------:|:-----------:|:----------:|:-------------:|:----------:|:------------|
| Cisco IOS  |       x      |      x      |       x     |    x   |      x      |      x     |       x       |      -     |      x      |
| Cisco NXOS |       x      |      x      |       x     |    x   |      x      |      x     |       x       |      -     |      x      |
| Cisco ASA  |       x      |      x      |       x     |    x   |      x      |      x     |       x       |            |      x      |
| Juniper OS |       x      |      x      |       x     |    x   |      x      |      x     |       x       |            |      x      |
|F5 BigIP LTM|       x      |      x      |       x     |    x   |      x      |            |               |      -     |      x      |

## Install

To install superloop, simply use pip:

```$ python -m pip install superloop```

This will install superloop along with all required dependencies to the directory ```/usr/local/lib/python3.x/dist-packages/superloop```. You will need to install yaml system wide via the following command ```$ python -m pip install pyyaml```

IMPORTANT: To simplify the execution of superloop application, please do the following after installation.

Create a symbolic link of 'superloop.py' and place it in '/usr/local/bin/'. Set the permission to 755. (replace python3.x with your correct python version)
```
$ ln -s /usr/local/lib/python3.x/dist-packages/superloop/superloop.py /usr/local/bin/superloop
$ chmod 755 /usr/local/bin/superloop
```
Now uncomment the following code within ```/usr/local/bin/superloop``` near the top:
```
#import sys
#sys.path.append('/usr/local/lib/python3.x/dist-packages/superloop')
```
So it looks like this . . . . 
```
#!/usr/bin/python3
import sys
sys.path.append('/usr/local/lib/python3.x/dist-packages/superloop')
from auditdiff import auditdiff
from push_cfgs import push_cfgs
...
..
.
<output truncated>
```
This will set the system path of superloop to '/usr/local/lib/python3.x/dist-packages/superloop'. If you have superloop installed in another directory, change the path accordingly (replace python3.x with appropriate version).

In Netmiko version 3.x by default is going to expect the configuration command to be echoed to the screen. This ensures Netmiko doesn't get out of sync with the underlying device (ex. keep sending configuration commands even though the remote device might be too slow and buffering them).

We will need to turn off command verification in netmiko base_connection.py file:
```
vi /usr/local/lib/python3.7/dist-packages/netmiko/base_connection.py
```
Search for the function 'send_config_set' and change 'cmd_verify=True' to 'cmd_verify=False' like this:
```
    def send_config_set(
        self,
        config_commands=None,
        exit_config_mode=True,
        delay_factor=1,
        max_loops=150,
        strip_prompt=False,
        strip_command=False,
        config_mode_command=None,
        cmd_verify=False,
        enter_config_mode=True,
    ):
```
Before we begin, I've constructed this application for easy database management by utilizing the power of YAML files. There are a combination of two YAML files that require management (default path is ~/database/):

  1. nodes.yaml
  2. templates.yaml

nodes.yaml acts as the inventory for all network devices. It must follow the format defined below as the application reads it in a specific method.
```
root@devvm:~/database# cat nodes.yaml 
---
- name: core-fw-superloop-toron
  ip: 10.10.10.10
  platform_name: cisco
  opersys: ios
  type: firewall
- name: core.sw.superloop.sfran
  ip: 20.20.20.20  
  platform_name: cisco
  opersys: ios
  type: switch 
- name: core.rt.superloop.sjose 
  ip: 30.30.30.30 
  platform_name: cisco
  opersys: ios
  type: router
```  
Credentials used to connect to nodes are via OS environment varilables. This eliminates any files associated to the application 'superloop' hardcoded with the username and password and thus, reduces the risk of being leaked/hacked. To setup the OS environment variables, the easiest way is to create a hidden file like ```.secret``` placed in your home directory. This file absolutely needs to be locked down to the service account owner. Set permission so only the service account owner where superloop is executed can read/write ```chmod 600 .secret```.

Your file should look like this:
```
root@devvm:~# cat .secret
export USERNAME="username"
export PASSWORD="password"
export SNMP_COMMUNITY_STRING="snmp_k3y"
```
* Please replace the fields with the appropriate values

Now open up your ```.bashrc``` file from your home directory ```vi ~/.bashrc``` and place the below code at the end of the file:
```
source /{home_directory}/.secret
```
Disconnect from your ssh session and reconnect again for changes to take effect. The environment variables have now been loaded.

templates.yaml is a database file that consist of all the jinja2 templates. You will need to include the full path. Here is a sample of how it should look like below. Do not change the format as the application reads it in a specific method. Only change the properties.
```
root@devvm:~/database# cat templates.yaml 
---
- platform_name: cisco
  type: firewall
  opersys: ios
  templates:
  - ~/templates/cisco/ios/firewall/snmp.jinja2
  - ~/templates/cisco/ios/firewall/base.jinja2
- platform_name: cisco
  type: router 
  opersys: ios
  templates:
  - ~/templates/cisco/ios/router/base.jinja2
- platform_name: cisco
  type: switch 
  opersys: ios
  templates:
  - ~/templates/cisco/ios/switch/access.jinja2
  - ~/templates/cisco/ios/switch/services.jinja2
  - ~/templates/cisco/ios/switch/snmp.jinja2
  - ~/templates/cisco/ios/switch/hostname.jinja2
  - ~/templates/cisco/ios/switch/dhcp.jinja2
```
I've structured the hierarchy based on vendor, os and the type. You should do the same in order to keep your templates orderly. Whatever hierarchy you choose, you will need to update/modify in the directory.py file to reflect (default path /templates/). Below is an example of how it can be organized.
```
root@devvm:~# tree ~/templates/
/root/templates/
|-- cisco
|   |-- ios
|   |   |-- router
|   |   |   |-- logging.jinja2
|   |   |   |-- service.jinja2
|   |   |   `-- snmp.jinja2
|   |   `-- switch
|   |       |-- base.jinja2
|   |       |-- logging.jinja2
|   |       |-- service.jinja2
|   |       `-- snmp.jinja2
|   `-- nxos
|       |-- router
|       |   |-- logging.jinja2
|       |   |-- service.jinja2
|       |   `-- snmp.jinja2
|       `-- switch
|           |-- base.jinja2
|           |-- logging.jinja2
|           |-- service.jinja2
|           `-- snmp.jinja2
|-- juniper
|   `-- junos
|       |-- router
|       |   |-- interfaces.jinja2
|       |   |-- policy-options.jinja2
|       |   |-- protocols.jinja2
|       |   |-- routing-options.jinja2
|       |   |-- security.jinja2
|       |   |-- snmp.jinja2
|       |   `-- system.jinja2
|       `-- vfirewall
|           |-- interfaces.jinja2
|           |-- policy-options.jinja2
|           |-- routing-instances.jinja2
|           |-- routing-options.jinja2
|           |-- security.jinja2
|           `-- system.jinja2

```
Let's look at a simple Cisco platform_name jinja2 template as an example.
```
root@devvm:~/superloop# cat ~/templates/cisco/ios/switch/base.jinja2 
{# audit_filter = ['name.*'] #}
{% if with_remediation %}
no name
{% endif %}
name {{ nodes.name }}
```
Notice there is a section called 'audit_filter' at the top of file. This audit filter should be included in all templates of Cisco and F5 platform_name. This tells superloop which lines to look for and compare against when rendering the configs. In other words, superloop will look for only lines that begin with 'name'. If you have additional lines that you want superloop to look at, simply append strings seperated by a comma like so... 
```
['name.*','service.*','username.*']
```

You may also have a template that consist of one or several levels deep like so...
```
root@devvm:~/superloop# cat ~/templates/cisco/ios/switch/dhcp.jinja2
{# audit_filter = ['ip dhcp.*'] #}

ip dhcp excluded-address 10.50.80.1
ip dhcp ping packets 5
!
ip dhcp pool DATA
 network 10.10.20.0 255.255.255.0
 default-router 10.10.20.1 
 dns-server 8.8.8.8 
``` 
Look at 'ip dhcp pool DATA'. The next line of config has an indentation. The parent is considered 'ip dhcp pool DATA' and the child are anything below that section. superloop is inteligent enough to parse the remaining 3 lines of configs without having to include it into the audit_filter.

Let's take a look at some Juniper templates.
```
root@devvm:~# cat ~/templates/juniper/junos/router/interfaces.jinja2   
{% import 'common.jinja2' as variable%}
replace: interfaces {
{%- for port in variable.INTERFACES %} 
    {{ port }} { 
        unit 0 { 
            family inet { 
                        {% if port == 'ge-0/0/1' %}
                filter {
                        input edge_inbound_softlayer;
                        output edge_outbound_softlayer;
                    }
                    sampling {
                        input;
                    }
            {%- endif -%} 
            {% if 'er1' in nodes.name %} 
                address {{ variable.INTERFACES[port]['er1_ip'] }}; 
            {% elif 'er2' in nodes.name %} 
                address {{ variable.INTERFACES[port]['er2_ip'] }}; 
            {% endif %} 
            } 
        } 
    }{% endfor %} 
} 
```
```
root@devvm:~# cat ~/templates/juniper/junos/router/routing-options.jinja2  
{% import 'common.jinja2' as variable%}
replace: routing-options {
    static {
    {% for route in variable.ROUTING_OPTIONS %}
      {% if variable.ROUTING_OPTIONS[route]['next_hop'] == 'discard' %}
        route {{ variable.ROUTING_OPTIONS[route]['destination'] }} {{ variable.ROUTING_OPTIONS[route]['next_hop'] }};
      {% elif variable.ROUTING_OPTIONS[route]['destination'] == variable.DEFAULT_ROUTE %}
        route {{ variable.ROUTING_OPTIONS[route]['destination'] }} {
            next-hop {{ variable.ROUTING_OPTIONS[route]['next_hop'] }};
            preference {{ variable.ROUTING_OPTIONS[route]['preference'] }};
      {% else %}
        route {{ variable.ROUTING_OPTIONS[route]['destination'] }} next-hop {{ variable.ROUTING_OPTIONS[route]['next_hop'] }};
     {% endif %}
    {% endfor %}
        }
    }
{%- if 'er1' in nodes.name %}  
    router-id {{ variable.SUPERLOOP_BGP_PEER1 }};
{% elif 'er2' in nodes.name %}
    router-id {{ variable.SUPERLOOP_BGP_PEER2 }};
{% endif %}
    autonomous-system {{ variable.AUTONOMOUS_SYSTEM }};
}
```
In these examples, you can see I imported a 'common.jinja2' file with the namespace as 'variable'. common.jinja2 is treated as a master variable file for a paricular region/data center. With this method, management is made simple and clean. Should you ever need to make a change on an existing value, you will only need to touch the common.jina2 file and the rest is taken care of.
```
{% set PRIVATE_NETWORK = '10.0.0.0' %}
{% set PRIVATE_PREFIX = '10.136' %}
{% set PUBLIC_PREFIX = '200.10.10' %}
{% set PUBLIC_MASK = '23' %}
{% set DEFAULT_ROUTE = '0.0.0.0/0' %}
{% set SUPERLOOP_BGP_PEER_PREFIX = '182.94.24' %}
{% set SUPERLOOP_BGP_PEER1 = '172.50.60.4' %}
{% set SUPERLOOP_BGP_PEER1 = '182.94.24.58' %}
{% set SUPERLOOP_BGP_PEER2 = '182.94.24.59' %}
{% set SUPERLOOP_NETWORK_1 = '172.50.60.0' %}
{% set SUPERLOOP_NETWORK_1_MASK = '28' %}
{% set SUPERLOOP_NETWORK_1_NEXTHOP = '172.50.60.1' %}
{% set AUTONOMOUS_SYSTEM = '65565' %}
 
{% set INTERFACES = {
  'ge-0/0/0': { 
        'er1_ip': PUBLIC_PREFIX ~ '.17/28',
        'er2_ip': PUBLIC_PREFIX ~ '.18/28'
  },
  'ge-0/0/1': { 
        'er1_ip': SUPERLOOP_BGP_PEER_PREFIX ~ '.4/' ~ SUPERLOOP_NETWORK_1_MASK,
        'er2_ip': SUPERLOOP_BGP_PEER_PREFIX ~ '.2/' ~ SUPERLOOP_NETWORK_1_MASK
  },
  'ge-0/0/2': { 
        'er1_ip': PUBLIC_PREFIX ~ '.33/30',
        'er2_ip': PUBLIC_PREFIX ~ '.34/30'
  },
  'fxp0': { 
        'er1_ip': PRIVATE_PREFIX ~ '.33/30',
        'er2_ip': PRIVATE_PREFIX ~ '.34/30'
  }
}
%}

{% set ROUTING_OPTIONS= {
  'static_route_1': { 
        'destination': PUBLIC_PREFIX ~ '.0/' ~ PUBLIC_MASK,
        'next_hop': 'discard'
  },
  'static_route_2': { 
        'destination': SUPERLOOP_BGP_PEER1 ~ '/32',
        'next_hop': SUPERLOOP_NETWORK_1_NEXTHOP
  },
  'static_route_3': { 
        'destination': SUPERLOOP_BGP_PEER2 ~ '/32',
        'next_hop': SUPERLOOP_NETWORK_1_NEXTHOP
  },
  'static_route_4': { 
        'destination': PRIVATE_NETWORK ~ '/8',
        'next_hop': PRIVATE_PREFIX ~ '.0.1'
  },
  'static_route_5': { 
        'destination': DEFAULT_ROUTE,
        'next_hop': SUPERLOOP_NETWORK_1_NEXTHOP,
                'preference': '175'
  }
}
%}
```

Now that I have explained the basic operations, onto the fun stuff!

## superloop audit diff

First and foremost, I would like to introduce to you the 'audit diff' function. This function was designed to compare against the jinja2 templates with your running-configurations/candidate-configurations to see if they are according to standards. You could imagine if you had hundreds, if not thousands of devices to maintain, standardization would be a nightmare without some form of auditing/automation tool. To paint you an example, say one day, little 'Amit' decides to make an unauthorized manual configuration change on a switch. No one knows about it or what he did. 'superloop' would be able to dive into the device and see if there were any discrepencies againist the template as that is considered the trusted source. 'superloop' is then able to determine what was exactly modified or changed. Whatever little Amit decided to configure would essentially be removed without hassel. This works the other way around as well. If configuration(s) on a device(s) does not have the standard rendered configs from the template (configs removed), superloop will determine they are missing and you may proceed to remediate by pushing the rendered configs. 'audit diff' will audit againist ONE or ALL templates belonging to the matched device(s) from the query. If you want to audit against ONE template, simply include the option '-f <template_name>' (exclude extension .jinja2). If you want to audit against ALL templates belonging to the matched device(s) query, do not include the '-f' option. 

![superloop audit_diff demo](https://github.com/superloopnetwork/superloop/blob/master/gifs/superloop_audit_diff_demo.gif)

'-' indicating a config(s) should be removed
'+' indicating a config(s) should be added
* (none) indicating NO discrepancies.

## superloop auditcreeper

By leveraging the power of the auditdiff engine, I'm able to extend it's functionality by creating a creeper. The 'auditcreeper' would essentially audit ALL devices in the nodes.yaml file against ALL templates specified in templates.yaml file at a set interval. For example, I may set the 'auditcreeper' to check every 4 hours to ensure standardization. You may modify the timining in second in the auditcreeper.py file. Look for:

```threading.Timer(14400, auditcreeper).start()```

* 14400 seconds = 4 hours

For the sake of this example, I've narrowed down to 5 second to speed things up so you'll have an idea of how it works.

![superloop auditcreeper demo](https://github.com/superloopnetwork/superloop/blob/master/gifs/superloop_auditcreeper_demo.gif)

In this demo, only one device gets remediated. A config was removed from the device. superloop detected the discrepancies and proceeded to remediate. Upon remediation, the second time 'audicreeper' runs, you can see that all templates are then matched (shown by '(none)', as in NO discrepancies):

```
+ ip dhcp excluded-address 10.50.30.3
```
'-' indicating a config(s) was removed
'+' indicating a config(s) was added
  
If there are no discrepancies for a specific template, you should see something like this:

```
/templates/cisco/ios/switch/service.jinja2 (none)
/templates/cisco/ios/switch/name.jinja2 (none)
/templates/cisco/ios/switch/dhcp.jinja2 (none)
/templates/cisco/ios/switch/snmp.jinja2 (none)
```
* (none) indicating NO discrepancies.

If there are multiple devices that require remediation, superloop handles remediation concurrently - meaning, superloop connects to all devices in parallel via multithreading.

## superloop push cfgs

The next set of features I developed was 'push cfgs'. 'push cfgs' is simplying pushing a template to a device(s). You may use regular expression in your query to match multiple nodes. This has proven to be very powerful and useful in an organized environment. 

In the below demo, I have made a change to the 'system.jinja2' template for a Juniper device. I've added the DNS entry of '4.4.4.4;' Using 'superloop push cfgs' to push the template, I then veryify the changes using 'superloop host exec' (to be discussed further in this documentation) to view the changes.

![superloop push_cfgs demo](https://github.com/superloopnetwork/superloop/blob/master/gifs/superloop_push_cfgs_demo.gif)

Verifying changes have been pushed:

![superloop host_exec_after_push_cfgs demo](https://github.com/superloopnetwork/superloop/blob/master/gifs/superloop_host_exec_after_push_cfgs_demo.gif)

You can see the '4.4.4.4;' entry now exist.

## superloop push local

The 'push local' command allows you to push configs that are stored in a text file to one more multiple nodes. I found this feature to be very useful when performing migrations. For example, if we wanted to drain/undrain traffic from one node, we could pre-configure the set of commands in the text file. At the time of migration, we can push the configs to the selected nodes. This method would eliminate any human error in the process.

![superloop push_local demo](https://github.com/superloopnetwork/superloop/blob/master/gifs/superloop_push_local_demo.gif)

## superloop pull cfgs

The 'pull cfgs' feature allows you to pull configs from one or multiple nodes. It's a function used to backup your configs manually when the command is invoked. To use it, simply type 'superloop pull cfgs -n core.*'. This will backup all node configurations that matches the regex. For F5 platform_names, this will download the *.ucs file from the appliance.

## superloop host exec

The 'host exec' (formerly known as 'onscreen') features allow you to execute a command on the device(s) without requiring you to log in. In the example below, the screen on the right is using 'push' and the screen on the left is using 'host exec' to check the changes after.

Here is an example of how you would use it:
```
root@devvm:~/superloop# superloop host exec "show ip int brief" -n core.*sw                
core.sw.superloop.sfran: Interface              IP-Address      OK? Method Status                Protocol
core.sw.superloop.sfran: Vlan1                  unassigned      YES NVRAM  administratively down down    
core.sw.superloop.sfran: Vlan120                 10.120.20.1      YES NVRAM  up                    up      
core.sw.superloop.sfran: Vlan130                 10.130.30.1      YES NVRAM  up                    up      
core.sw.superloop.sfran: Vlan140                 10.140.40.1      YES NVRAM  up                    up      
core.sw.superloop.sfran: Vlan150                 10.150.50.1      YES NVRAM  up                    up      
```
In this demo, I'm doing a 'show version' for all the devices I have in my database (3 - a mix of Cisco and Juniper platform_name) and it's displaying all the information in 9.6 seconds. You can imagine how powerful this feature would be if you have hundreds, if not thousands of devices that you need to pull information from without the need of logging in, one by one and capturing the output.

![superloop host_exec_demo](https://github.com/superloopnetwork/superloop/blob/master/gifs/superloop_host_exec_demo.gif)

## superloop ssh

Users are now able to take advantage of the 'ssh' menu screen. This feature allows users to quickly search up a device via name (doesn't have to be a complete or exactly matched string) and establish a SSH session. It's a very powerful tool in the sense that it support regular expression to filter out certain desired hosts from a lare scale network.

Here is an example of how you would use it:
```
root@devvm:~/superloop# superloop ssh core.*
ID      name                    address         platform_name
1       core-fw-superloop-toron 10.10.10.10     cisco
2       core.sw.superloop.sfran 20.20.20.20     cisco
3       core.rt.superloop.sjose 30.30.30.30     cisco
Enter ID to SSH to: 
```
```
root@devvm:~/superloop# python superloop ssh core.*(fw|rt)
ID      name                    address         platform_name
1       core-fw-superloop-toron 10.10.10.10     cisco
2       core.rt.superloop.sjose 30.30.30.30     cisco
Enter ID to SSH to: 
```
```
root@devvm:~/superloop# superloop ssh .*sfran
ID      name                    address         platform_name
1       core.sw.superloop.sfran 20.20.20.20     cisco
Password: 
```
* Notice after 'ssh' it expects a positional argument(name).

If the search result returns one host, superloop automatically establishes a SSH session.

## superloop host add/remove

When I first built this application, the expectation was to manually populate the nodes.yaml file in order for superloop to execute. That is no longer a requirement. Introducing 'host add'. This function will allow you add hosts to the database file via cli (one line) without the need to manually update the nodes.yaml file. It works like this; when 'superloop host add <management ip address>' command is invoked, superloop will connect to the device via snmp. It will pull the neccessary information such as it's name and platform_name to populate it into nodes.yaml.

Let's now look at 'host remove' feature. Just like 'add', 'remove' allows you to remove a node from the database without having to manually edit the nodes.yaml file. Here is how you use it:
```
root@devvm:~/superloop# cat nodes.yaml
---
- name: core-fw-superloop-toron
  ip: 10.10.10.10
  platform_name: cisco
  opersys: ios
  type: firewall
- name: core.sw.superloop.sfran
  ip: 20.20.20.20  
  platform_name: cisco
  opersys: ios
  type: switch 
- name: core.rt.superloop.sjose 
  ip: 30.30.30.30 
  platform_name: cisco
  opersys: ios
  type: router
  ```
Say we wanted to blow out the node 'core.sw.superloop.sfran'. Simply use the following command 'superloop host remove core.sw.superloop.sfran' or 'superloop host remove 20.20.20.20'. It supports both name and IP address.
```
root@devvm:~/superloop# superloop host remove core.sw.superloop.sfran
[-] NODE SUCCESSFULLY REMOVED FROM DATABASE
```
```
root@devvm:~/superloop# cat nodes.yaml
---
- name: core-fw-superloop-toron
  ip: 10.10.10.10
  opersys: ios
  platform_name: cisco
  type: firewall
- name: core.rt.superloop.sjose
  ip: 30.30.30.30
  opersys: ios
  platform_name: cisco
  type: router
```
* Noticed how the node 'core.sw.superloop.sfran' has been removed from the database.

## superloop node list

We can now leverage the power of 'superloop host add' by having snmp poll more attributes on the node(s) such as the software version, location, serial number etc. Once we have these details in our database file, we are then able list them in cli. This will give us all the details about a particular node. To use this, simply type 'superloop node list <name>'. Regular expressions is supported for this feature so if you have multiple hosts you would like to view, you can match it via regex.
```  
root@devvm:~/superloop# superloop node list core.*
[
    {
        "name": "core-fw-superloop-toron"
        "os": "ios"
        "platform_name": "cisco"
        "type": "firewall"
        "data": {
            "managed_configs": {
                   base.jinja2
                   snmp.jinja2
             }
         }
    },
    {
        "name": "core.sw.superloop.sfran"
        "os": "ios"
        "platform_name": "cisco"
        "type": "switch"
        "data": {
            "managed_configs": {
                   base.jinja2
                   service.jinja2
                   dhcp.jinja2
                   snmp.jinja2
             }
         }
    },
    {
        "name": "core.rt.superloop.sjose"
        "os": "ios"
        "platform_name": "cisco"
        "type": "router"
        "data": {
            "managed_configs": {
                   base.jinja2
             }
         }
    }
]
```
Or a particular node...
```
root@devvm:~/superloop# superloop node list .*sfran  
[
    {
        "name": "core.sw.superloop.sfran"
        "os": "ios"
        "platform_name": "cisco"
        "type": "switch"
        "data": {
            "managed_configs": {
                   base.jinja2
                   service.jinja2
                   dhcp.jinja2
                   snmp.jinja2
             }
         }
    }
]
```
