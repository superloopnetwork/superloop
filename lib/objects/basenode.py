######################### BASE NODE ###########################
from netmiko import ConnectHandler
from f5.bigip import ManagementRoot
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
			
	def connect_to_f5(self):

		self.f5_connect = ManagementRoot(self.ip, self.username,self.password)
		
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
		if(self.platform == 'cisco'):
			output = self.net_connect.send_config_set(commands)
			print(output)
		elif(self.platform == 'juniper'):
			output = self.net_connect.send_config_set(commands,exit_config_mode=False)
			self.net_connect.commit(and_quit=True)
			print(output)
		self.net_connect.disconnect()

	def pull_cfgs(self,command):

		if(self.platform == 'cisco'):
			command = 'show running-config'
			self.connect()
			self.write_to_file(command)
			self.net_connect.disconnect()

		elif(self.platform == 'juniper'):
			command = 'show configuration'
			self.connect()
			self.write_to_file(command)
			self.net_connect.disconnect()

		elif(self.platform == 'f5'):
			self.connect_to_f5()
			self.f5_connect.shared.file_transfer.ucs_downloads.download_file('config.ucs', '{}/backup-configs/{}.ucs'.format(self.get_home_directory(),self.hostname))
			print('')

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
