# superloop
Inspired by the world's leading social media tech company (Facebook) for network automation, I have created my own version of the framework.

## Prerequisites
  1. Python 3.6 or higher.
  2. netmiko - A HUGE thanks and shout out to Kirk Byers for developing the library!
  3. snmp_helper.py - module written by Kirk Byers (https://github.com/ktbyers/pynet/blob/master/snmp/snmp_helper.py).
  4. ciscoconfparse - A library to help parse out Cisco (or similiar) CLI configs (https://pypi.org/project/ciscoconfparse/).
  5. yaml - YAML is a human-readable data-serialization language (https://en.wikipedia.org/wiki/YAML).
  6. libyaml-cpp-dev - C parser for yaml (xargs apt-get install < requirements.apt)
  7. jinja2 - template engine for Python (https://jinja.palletsprojects.com/en/2.11.x/)
  8. hvac - Python client for hashicorp vault (https://pypi.org/project/hvac/).

## Support

|__Platform__|__audit diff__|__push cfgs__|__host exec__|__ssh__ |__node list__|__host add__|__host remove__|__host discover__|__push acl__|__pull cfgs__|
|------------|:------------:|:-----------:|:-----------:|:------:|:-----------:|:----------:|:-------------:|:---------------:|:----------:|:------------|
| Cisco IOS  |       x      |      x      |       x     |    x   |      x      |      x     |       x       |        x        |      -     |      x      |
| Cisco NXOS |       x      |      x      |       x     |    x   |      x      |      x     |       x       |        x        |      -     |      x      |
| Cisco ASA  |       x      |      x      |       x     |    x   |      x      |      x     |       x       |        x        |            |      x      |
| Juniper OS |       x      |      x      |       x     |    x   |      x      |      x     |       x       |        x        |            |      x      |
|F5 BigIP LTM|       x      |      x      |       x     |    x   |      x      |      x     |       x       |        x        |      -     |      x      |
|  Netscaler |       x      |      x      |       x     |    x   |      x      |      x     |       x       |        x        |      -     |      x      |

## Overview

![superloop gitops_operational_framework](https://github.com/superloopnetwork/superloop/blob/master/gifs/superloop_gitops_operational_framework.png)


## Install

There are a few methods to install superloop but the easiest is the following:

An appropriate install location would be in ```/usr/local/```

```
   $ cd /usr/local/
   $ git clone https://github.com/superloopnetwork/superloop
   $ cd superloop/
   $ pip3 install -r requirements.txt
   $ xargs apt-get install < requirements.apt
```

This will install superloop along with all required dependencies to the directory. 

IMPORTANT: To simplify the execution of superloop application, please do the following after installation.

Create a symbolic link of 'superloop.py' and place it in '/usr/local/bin/'. Set the permission to 755. (replace python3.x with your correct python version)
```
$ ln -s /usr/local/superloop/superloop.py /usr/local/bin/superloop
$ chmod 755 /usr/local/bin/superloop
```
Now uncomment the following code within ```/usr/local/bin/superloop``` near the top:
```
#import sys
#sys.path.append('/usr/local/superloop')
```
So it looks like this . . . . 
```
#!/usr/bin/python3
import sys
sys.path.append('/usr/local/superloop')
from auditdiff import auditdiff
from push_cfgs import push_cfgs
...
..
.
<output truncated>
```
This will set the system path of superloop to '/usr/local/superloop'. If you have superloop installed in another directory, change the path accordingly (replace python3.x with appropriate version).

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
  
## Credentials

Credentials used to connect to nodes are via the OS environment varilable, $USER. It will prompt you for your password
```
export USERNAME=username
```

## Hierarchy

You'll noticed the superloo_code/ and superloop/ source code are completely segregated by different repositories. superloop_code/ repo can be found here and should be cloned to the home directory of the user as that is where superloop references to. Hourly backups should be stored in the superloop_code/backup-configs directory via CI/CD. superloop_code/database are where the inventory of the devices, templates (reference) files are stored. superloop_code/templates are where all the templates are stored. The hierarchy is structured based on vendor, OS and device type when it comes to templates. That's because different vendors and OS have different syntaxes. ex. Cisco IOS have different syntaxes than Cisco NXOS.
```
root@devvm:~# tree superloop_code/
superloop_code/
├── database
│   ├── nodes.yaml
│   ├── policies.yaml
│   ├── templates.yaml
│   └── templates.yaml.bak
├── policy
│   ├── APPLICATIONS.net
│   ├── cisco
│   │   └── ios
│   │       └── firewall
│   │           └── base_policy.json
│   ├── juniper
│   │   └── junos
│   │       └── vfirewall
│   │           └── policy.json
│   ├── NETWORKS.net
│   ├── SERVICES.net
│   ├── SOURCE_DEVICE.net
│   ├── SOURCE_USER.net
│   ├── :w
│   └── ZONES.net
└── templates
    ├── hardware_vendors
    │   ├── cisco
    │   │   ├── asa
    │   │   │   └── firewall
    │   │   │       ├── base.jinja2
    │   │   │       ├── logging.jinja2
    │   │   │       ├── object-groups.jinja2
    │   │   │       └── snmp.jinja2
    │   │   ├── ios
    │   │   │   ├── router
    │   │   │   │   └── base.jinja2
    │   │   │   └── switch
    │   │   │       ├── aaa.jinja2
    │   │   │       ├── base.jinja2
    │   │   │       ├── base.jinja2.bak
    │   │   │       ├── crypto.jinja2
    │   │   │       ├── cs_vserver.jinja2
    │   │   │       ├── dhcp.jinja2
    │   │   │       ├── interfaces.jinja2
    │   │   │       ├── logging.jinja2
    │   │   │       ├── service.jinja2
    │   │   │       └── snmp.jinja2
    │   │   └── nxos
    │   ├── f5
    │   │   └── bigip
    │   └── juniper
    │       └── junos
    │           └── vfirewall
    │               ├── interfaces.jinja2
    │               ├── protocols.jinja2
    │               ├── routing-instances.jinja2
    │               ├── routing-options.jinja2
    │               └── system.jinja2
    └── standards
        └── common.jinja2

```
Let's look at a simple Cisco platform_name jinja2 template as an example.

```
{# audit_filter = ['snmp-server (?!user).*'] #}
{%- import 'global.jinja2' as global -%}
{%- import 'datacenter.jinja2' as dc -%}
{%- import 'environment.jinja2' as env -%}
{# %- import node.name ~ '.jinja2' as device -% #}
snmp-server community {{ secrets['community_1'] }} group network-operator
snmp-server community {{ secrets['community_2'] }} group network-operator
snmp-server community {{ secrets['community_3'] }} group network-operator
snmp-server location {{ dc.snmp.location }}
```
Notice there is a section called 'audit_filter' at the top of file. This audit filter should be included in all templates of Cisco and Citrix Netscaler. It accepts a regular expression. This tells superloop which lines to look for and compare against when rendering the configs. In other words, superloop will look for only lines that begin with 'snmp-server' and anything else trailing but exclude 'user' as the second piece of string. If you have additional lines that you want superloop to look at, simply append strings seperated by a comma like so...
```
['snmp-server (?!user).*','hello','world']
```
There are a few import statements that you may need to include depending on the variables you need to use. The files are organized based on the logic and reference to their geographic location.

global.jinja2 maps to ~/superloop_code/templates/standards/global.jinja2 # all global variables will stored in this file.

datacenter.jinja2 maps to ~/superloop_code/templates/datacenter/<site_name>/datacenter.jinja2 # all variables pertaining to datacenter/region specific will be stored in this file.

environment.jinja2 maps to ~/superloop_code/templates/datacenter/<site_name>/prod/environment.jinja2 # all variables pertaining to the different region and environment will be stored in this file.

NEVER include any secrets (static) within any templates as they will be exposed in clear text and visible in version control. Instead we want to mask our secrets by storing them in hashicorp and calling them in this fashion:
```
{{ secrets['community_1'] }}
```
Mappings can be found here: Networking > prod > secrets in vault. Every time when a template is being rendered for output, superloop will authenticate with vault. If successful, it then queries the requested secret. The secret is returned to superloop and is then pushed to jinja for output. With this method, no secrets are exposed in any files.

You may also have a template that consist of one or several levels deep like so...
```
{# audit_filter = ['ip dhcp .*'] #}
ip dhcp excluded-address 10.50.80.1
ip dhcp ping packets 5
!
ip dhcp pool DATA
network 10.10.20.0 255.255.255.0
default-router 10.10.20.1
dns-server 8.8.8.8
```
Look at 'ip dhcp pool DATA'. The next line of config has an indentation. The parent is considered 'ip dhcp pool DATA' and the child are anything below that section. superloop is intelligent enough to parse the remaining 3 lines of configs without having to include it into the audit_filter.

Now that I have explained the basic operations, onto the fun stuff!

## superloop host add
When you add a device, every attribute of the node will be discovered automatically so there is no need to populate it manually.
```
root@devvm:~# superloop host add 10.202.1.7
+ SNMP discovery successful.
+ New node appended to database.
```

## superloop host remove
To remove a node, simply execute a 'superloop host remove <IPv4/hostname>':
```
wailit.loi@pc-netauto-001:~$ superloop host remove 10.202.1.7
- Node successfully removed from database.
```

## superloop node list
To verify the device attributes:

```
root@devvm:~# superloop node list pt-switch-001
[
    {
        "created_at": "2022-09-12 14:02:10"
        "created_by": "wailit.loi"
        "data": {
            "managed_configs": {
                   "logging.jinja2"
                   "ntp.jinja2"
                   "snmp.jinja2"
             }
         }
        "domain_name": "null"
        "environment": "prod"
        "hardware_vendor": "cisco"
        "lifecycle_status": "null"
        "location_name": "toronto"
        "mgmt_con_ip4": "null"
        "mgmt_ip4": "10.202.1.7"
        "mgmt_oob_ip4": "null"
        "mgmt_snmp_community4": "null"
        "name": "pt-switch-001.shortcovers.local"
        "opersys": "ios"
        "platform_name": "WS-C3750X-48"
        "role_name": "datacenter-switch"
        "serial_num": "FDO1629R0JL"
        "software_image": "null"
        "software_version": "null"
        "status": "online"
        "type": "switch"
        "updated_at": "null"
        "updated_by": "null"
    }
]
```

## superloop host update

Notice the 'name' or hostname of the device has the domain appended because the 'ip domain-name domain.name' is configured. If the domain name is not required, superloop has the ability to modify the database attribute from cli:
```
root@devvm:~#  superloop host update core1.leaf.demo.domain.name --help
usage: superloop host update [-h] [-a ATTRIBUTE] [-am AMEND] node
positional arguments:
  node
optional arguments:
  -h, --help            show this help message and exit
  -a ATTRIBUTE, --attribute ATTRIBUTE
                        Specify the attribute that requires updating
  -am AMEND, --amend AMEND
                        The value that is being amended
 
root@devvm:~# superloop host update core1.leaf.demo.domain.name -a name -am core1.leaf.demo
Please confirm you would like to change the value from core1.leaf.demo.domain.name : name : core1.leaf.demo.domain.name to core1.leaf.demo.domain.name : name : core1.leaf.demo. [y/N]: y
+ Amendment to database was successful.
```
We can take a look at the 'node list' feature to verify the 'name' attribute has changed:
```
root@devvm:~# superloop node list core1.leaf.demo
[
    {
        "created_at": "2022-09-12 14:02:10"
        "created_by": "wailit.loi"
        "data": {
            "managed_configs": {
                   "logging.jinja2"
                   "ntp.jinja2"
                   "snmp.jinja2"
             }
         }
        "domain_name": "null"
        "environment": "prod"
        "hardware_vendor": "cisco"
        "lifecycle_status": "null"
        "location_name": "telecity"
        "mgmt_con_ip4": "null"
        "mgmt_ip4": "10.202.1.7"
        "mgmt_oob_ip4": "null"
        "mgmt_snmp_community4": "null"
        "name": "core1.leaf.demo"
        "opersys": "ios"
        "platform_name": "WS-C3750X-48"
        "role_name": "datacenter-switch"
        "serial_num": "FDO1629R0JL"
        "software_image": "null"
        "software_version": "null"
        "status": "online"
        "type": "switch"
        "updated_at": "2022-09-12 14:13:36"
        "updated_by": "wailit.loi"
    }
]
```
When it comes to templating, we are able to call these attributes directly and make logical decisions based on the value. We'll discuss more later on in this article...

## superloop push render
The 'push render' function, simply renders a template created in jinja2. Ensure the template is provisioned in the ~/superloop_code/database/templates.yaml file so superloop understands which template(s) is/are loaded. If we want to render a template, we simply execute 'superloop push render --node <regex> --file <name_of_template>'. --node accepts a regular expression to match (multiple) node(s) and it can be as granular as you wish. Ex. matching an entire datacenter and/or device type. If there is no '–file' flag supplied, ALL templates for the device specific type will be rendered.
```
root@devvm:~# superloop push render --node core.*sw.*demo --file logging
core1.sw.yyz.demo
/root/superloop_code/templates/hardware_vendors/cisco/nxos/switch/logging.jinja2
logging message interface type ethernet description
logging logfile messages 6 size 32768
logging server 10.100.10.53
logging server 10.100.2.40
logging timestamp milliseconds
logging monitor 3
no logging rate-limit
 
core2.sw.yyz.demo
/root/superloop_code/templates/hardware_vendors/cisco/nxos/switch/logging.jinja2
logging message interface type ethernet description
logging logfile messages 6 size 32768
logging server 10.100.10.53
logging server 10.100.2.40
logging timestamp milliseconds
logging monitor 3
no logging rate-limit
```

## superloop audit diff
This function was designed to compare against the jinja2 templates with your running-configurations/candidate-configurations to see if they are according to standards. You could imagine if you had hundreds, if not thousands of devices to maintain, standardization would be a nightmare without some form of auditing/automation tool. To paint you an example, say one day, an employee decides to make an unauthorized manual configuration change on a switch. No one knows about it or what they did. 'superloop' is able to dive into all devices and see if there were any discrepancies against the template as that is considered the trusted source. 'superloop' is then able to determine what was exactly modified or changed. Whatever was configured would essentially be negated automatically. This works the other way around as well. If configuration(s) on a device(s) does not have the standard rendered configs from the template (configs removed), superloop will determine they are missing and you may proceed to remediate by pushing the rendered configs. 'audit diff' will audit against ONE or ALL templates belonging to the matched device(s) from the query. If you want to audit against ONE template, simply include the option '--file <template_name>' (exclude extension .jinja2). If you want to audit against ALL templates belonging to the matched device(s) query, do not include the '--file' option.

```
root@devvm:~# superloop audit diff -n pc.*test -f snmp                                   
Password:
[>] complete [0:00:10.911552]
 
Only in the device: -
Only in the generated config: +
pc-n9ktest-001
/root/superloop_code/templates/hardware_vendors/cisco/nxos/switch/snmp.jinja2
- snmp-server community helloworld group network-operator
+ snmp-server location coresite
```

## superloop push cfgs
The 'push cfgs' function simply pushes the template(s) to the specified node(s). For Cisco, Citrix, F5 and Palo Alto devices, a debug output will be shown with a list of commands (if any) of what will be sent first before user commits to push. From the below example, you can see which templates are enabled for pushing, represented by [>] vs. which templates are disabled, represented by [x]. The state of the template can be controlled in the ~/superloop_code/database/templates.yaml file. As a safety, we disable any templates that we are not confident in pushing. If enabled, superloop will auto remediate those template(s). Please use with caution as it can cause severe impact. Two phases happens when pushing templates of Cisco, Citrix, F5 and Palo Alto devices. First, superloop performs an audit diff. It will check to see what configs are missing or removed. Second, it will encapsulate the necessary configs and prepare it for pushing. If the device has no diffs, then no configs will be pushed to the device. The output of session when pushing will be displayed so users can see what happens behind the scenes.

```
root@devvm:~# superloop push cfgs --node p.*nxs
[x] core1.sw.yyz.demo ; base.jinja2
[x] core1.sw.yyz.demo-iad4 ; base.jinja2
[x] core2.sw.yyz.demo ; base.jinja2
[x] core2.sw.yyz.demo-iad4 ; base.jinja2
[x] core1.leaf.yyz.demo ; base.jinja2
[x] core2.leaf.yyz.demo ; base.jinja2
[x] core3.leaf.yyz.demo ; base.jinja2
[>] core1.sw.yyz.demo ; logging.jinja2
[>] core1.sw.yyz.demo ; ntp.jinja2
[>] core1.sw.yyz.demo ; snmp.jinja2
[>] core1.sw.yyz.demo-iad4 ; logging.jinja2
[>] core1.sw.yyz.demo-iad4 ; ntp.jinja2
[>] core1.sw.yyz.demo-iad4 ; snmp.jinja2
[>] core2.sw.yyz.demo ; logging.jinja2
[>] core2.sw.yyz.demo ; ntp.jinja2
[>] core2.sw.yyz.demo ; snmp.jinja2
[>] core2.sw.yyz.demo-iad4 ; logging.jinja2
[>] core2.sw.yyz.demo-iad4 ; ntp.jinja2
[>] core2.sw.yyz.demo-iad4 ; snmp.jinja2
[>] core1.leaf.yyz.demo ; logging.jinja2
[>] core1.leaf.yyz.demo ; ntp.jinja2
[>] core1.leaf.yyz.demo ; snmp.jinja2
[>] core2.leaf.yyz.demo ; logging.jinja2
[>] core2.leaf.yyz.demo ; ntp.jinja2
[>] core2.leaf.yyz.demo ; snmp.jinja2
[>] core3.leaf.yyz.demo ; logging.jinja2
[>] core3.leaf.yyz.demo ; ntp.jinja2
[>] core3.leaf.yyz.demo ; snmp.jinja2
+ complete [0:00:11.403772]
 
[DEBUG]
{
    "core2.leaf.yyz.demo": [
        [
            "ntp logging"
        ]
    ],
    "core3.leaf.yyz.demo": [
        [
            "ntp logging"
        ]
    ]
}
config term
Enter configuration commands, one per line. End with CNTL/Z.
 
core2.leaf.yyz.demo(config)# ntp logging
 
core2.leaf.yyz.demo(config)# end
 
core2.leaf.yyz.demo#
config term
Enter configuration commands, one per line. End with CNTL/Z.
 
core3.leaf.yyz.demo(config)# ntp logging
 
core3.leaf.yyz.demo(config)# end
 
core3.leaf.yyz.demo#
+ complete [0:00:14.664805]
```

## superloop push local

The 'push local' command allows you to push configs that are stored in a text file (home directory). This feature is useful when performing migrations. For example, if we wanted to drain/undrain traffic from one node, we could pre-configure the set of commands in the text file. At the time of migration, we can push the configs to the selected nodes. This method would eliminate any human error in the process.

## superloop ssh
SSH feature allows us to quickly search up node(s) via regular expression and establish a SSH session with the device. This is useful when you have thousands of nodes in the network and memorizing IP addresses is simply not an option.
```
root@devvm:~# superloop ssh p.*lb.*act
id                        name                           address                   platform
1                         core1.lb.yyz.demo.active       10.10.10.1               citrix                  
2                         core1.lb.sfo.demo.active       10.10.10.2               citrix                  
3                         core1.lb.sin.demo.active       10.10.10.3               citrix
```
## superloop host exec
The 'host exec' features allow you to execute a command on the device(s) without requiring you to log in manually one by one. This feature is extremely useful at times when you want to check status across multi devices.
```
root@devvm:~# superloop host exec "show ip interface brief" --node core.*sw.*yyz.*demo       
Password:
core1.sw.yyz.demo: IP Interface Status for VRF "default"(1)
core1.sw.yyz.demo: Interface            IP Address      Interface Status
core1.sw.yyz.demo: Vlan201              10.201.1.22     protocol-up/link-up/admin-up      
core1.sw.yyz.demo:
 
core2.sw.yyz.demo: IP Interface Status for VRF "default"(1)
core2.sw.yyz.demo: Interface            IP Address      Interface Status
core2.sw.yyz.demo: Vlan201              10.201.1.23     protocol-up/link-up/admin-up      
core2.sw.yyz.demo:
 
[>] Complete [0:00:08.375958]
```
