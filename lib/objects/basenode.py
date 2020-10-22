######################### BASE NODE ###########################
from netmiko import ConnectHandler, SCPConn
import re
import os

class BaseNode(object):

	def __init__(self,ip,hostname,platform,opersys,type):

		self.ip = ip
		self.hostname = hostname
		self.username = os.environ.get('USERNAME') 
		self.password = os.environ.get('PASSWORD')
		self.platform = platform
		self.opersys = opersys
		self.type = type

	def connect(self):

		self.net_connect = ConnectHandler(self.ip,self.hostname,self.username,self.password,self.password,device_type=self.get_device_type())
			
	def scpconnect(self):
		self.connect()
		self.scp_connect = SCPConn(self.net_connect)
		
	def location(self):

		datacenter_location = ''
		if (self.type == 'firewall'):
			location_list = self.hostname.split('-')	
			datacenter_location = location_list[3]

		elif (self.type == 'switch' or self.type == 'router'):
			location_list = self.hostname.split('.')	
			datacenter_location = location_list[3]

		return datacenter_location

	def get_device_type(self):

		device_type = {
				"asa" : "cisco_asa",
				"ios" : "cisco_ios",
				"nxos" : "cisco_nxos",
				"f5linux" : "f5_linux",
				"ltm" : "f5_ltm",
				"tmsh" : "f5_tmsh",
				"juniper" : "juniper",
				"junos" : "juniper_junos",
				"vyattavyos" : "vyatta_vyos",
				"vyos" : "vyos"
		}
	
		return device_type['{}'.format(self.opersys)]

	def push_cfgs(self,commands):

		self.connect()
		output = self.net_connect.enable()

		if self.platform == 'cisco' and self.opersys == 'ios':
			output = self.net_connect.send_config_set(commands, exit_config_mode=True)
			save = self.net_connect.send_command('write memory')
			print(output)
			print(save)

		elif self.platform == 'cisco' and self.opersys == 'nxos':
			output = self.net_connect.send_config_set(commands, exit_config_mode=True)
			save = self.net_connect.send_command('copy running-config startup-config')
			print(output)
			print(save)

		elif self.platform == 'juniper':
			output = self.net_connect.send_config_set(commands, exit_config_mode=False)
			self.net_connect.commit(and_quit=True)
			print(output)

		elif self.platform == 'vyatta':
			output = self.net_connect.send_config_set(commands, exit_config_mode=False)
			self.net_connect.commit()
			print(output)

		elif self.platform == 'f5':
			output = self.net_connect.send_config_set(commands,enter_config_mode=False,exit_config_mode=False)
			save = self.net_connect.send_command('save sys config')
			print(output)
			print(save)

		self.net_connect.disconnect()

	def pull_cfgs(self,command):

		if self.platform == 'cisco':
			command = 'show running-config'

		elif self.platform == 'cisco' and self.opersys == 'nxos':
			command = 'show running-config | exclude Time'

		elif self.platform == 'juniper':
			command = 'show configuration'

		elif(self.platform == 'vyatta'):
			command = 'show configuration commands'

		elif self.platform == 'f5':
			command = 'list ltm one-line'
			self.scpconnect()
			self.write_to_file(command)
			self.scp_connect.scp_get_file('/var/local/ucs/config.ucs', '{}/backup-configs/{}'.format(self.get_home_directory(),self.hostname))
			self.scp_connect.close()
			self.net_connect.disconnect()

		if self.platform != 'f5':
			self.connect()
			self.write_to_file(command)
			self.net_connect.disconnect()

	def exec_cmd(self,command):

		self.connect()
		output = self.net_connect.send_command(command)
		output = output.replace('\n','\n{}: '.format(self.hostname))
		output = re.sub(r'^','{}: '.format(self.hostname),output)
		print ("{}".format(output))
		print("")
		self.net_connect.disconnect()

	def get_home_directory(self):
		home_directory = os.environ.get('HOME')

		return home_directory

	def get_config(self,command):

		command = 'show running-config'
		f = open("{}/backup-configs/{}".format(self.get_home_directory(),self.hostname) + ".conf", "w")
		self.connect()
		output = self.net_connect.send_command_expect(command)
		f.write(output)
		f.close()
		self.net_connect.disconnect()

	def get_diff(self,commands):

		f = open("{}/diff-configs/{}".format(self.get_home_directory(),self.hostname) + ".conf", "w")
		self.connect()
		output = self.net_connect.send_config_set(commands)
#		print(output)
		f.write(output)
		f.close()
		self.net_connect.disconnect()

	def write_to_file(self,command):

		if(not os.path.isdir('{}/backup-configs/'.format(self.get_home_directory()))):
			os.makedirs('{}/backup-configs/'.format(self.get_home_directory()))
		with open("{}/backup-configs/{}".format(self.get_home_directory(),self.hostname) + ".conf", "w") as file:
			output = self.net_connect.send_command_expect(command)
			file.write(output)
			file.close()
