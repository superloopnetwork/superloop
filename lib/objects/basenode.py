######################### BASE NODE ###########################
from netmiko import ConnectHandler, SCPConn
import re
import os

class BaseNode(object):

	def __init__(self,created_at,created_by,domain_name,hardware_vendor,lifecycle_status,location_name,mgmt_ip4,mgmt_con_ip4,mgmt_oob_ip4,mgmt_snmp_community4,name,platform_name,oncall_team,opersys,software_image,software_version,type,role_name,serial_num,status,updated_at,updated_by):

		self.created_at = created_at
		self.created_by = created_by
		self.domain_name = domain_name
		self.hardware_vendor = hardware_vendor 
		self.lifecycle_status = lifecycle_status
		self.location_name = location_name
		self.mgmt_con_ip4 = mgmt_con_ip4
		self.mgmt_ip4 = mgmt_ip4
		self.mgmt_oob_ip4 = mgmt_oob_ip4
		self.mgmt_snmp_community4 = mgmt_snmp_community4
		self.name = name
		self.oncall_team = oncall_team
		self.password = os.environ.get('PASSWORD')
		self.platform_name = platform_name
		self.oncall_team = oncall_team
		self.opersys = opersys
		self.role_name = role_name 
		self.serial_num = serial_num
		self.software_image = software_image
		self.software_version = software_version
		self.status = status
		self.type = type
		self.updated_at = updated_at
		self.updated_by = updated_by
		self.username = os.environ.get('USERNAME') 

	def connect(self):
		self.net_connect = ConnectHandler(self.mgmt_ip4,self.name,self.username,self.password,self.password,device_type=self.get_device_type())
			
	def scpconnect(self):
		self.connect()
		self.scp_connect = SCPConn(self.net_connect)
		
	def location(self):
		datacenter_location = ''
		if (self.type == 'firewall'):
			location_list = self.name.split('-')	
			datacenter_location = location_list[3]

		elif (self.type == 'switch' or self.type == 'router'):
			location_list = self.name.split('.')	
			datacenter_location = location_list[3]

		return datacenter_location

	def get_device_type(self):


		device_type = {
				'ASA5510' : 'cisco_asa',
				'WS-C3750G-24TS-1U' : 'cisco_ios',
				'f5linux' : 'f5_linux',
				'ltm' : 'f5_ltm',
				'tmsh' : 'f5_tmsh',
				'firefly-perimeter' : 'juniper',
				'junos' : 'juniper_junos',
				'vyattavyos' : 'vyatta_vyos',
				'vyos' : 'vyos'
		}
	
		return device_type['{}'.format(self.platform_name)]

	def push_cfgs(self,commands):
		self.connect()
		output = self.net_connect.enable()
		if self.hardware_vendor == 'cisco' and self.opersys == 'ios':
			output = self.net_connect.send_config_set(commands, exit_config_mode=True)
			save = self.net_connect.send_command('write memory')
			print(output)
			print(save)
		elif self.hardware_vendor == 'cisco' and self.opersys == 'nxos':
			output = self.net_connect.send_config_set(commands, exit_config_mode=True)
			save = self.net_connect.send_command('copy running-config startup-config')
			print(output)
			print(save)
		elif self.hardware_vendor == 'juniper':
			output = self.net_connect.send_config_set(commands, exit_config_mode=False)
			self.net_connect.commit(and_quit=True)
			print(output)
		elif self.hardware_vendor == 'vyatta':
			output = self.net_connect.send_config_set(commands, exit_config_mode=False)
			self.net_connect.commit()
			print(output)
		elif self.hardware_vendor == 'f5':
			output = self.net_connect.send_config_set(commands,enter_config_mode=False,exit_config_mode=False)
			save = self.net_connect.send_command('save sys config')
			print(output)
			print(save)
		self.net_connect.disconnect()

	def pull_cfgs(self,command):
		scp_flag = False
		method = 'pull_cfgs'
		if self.hardware_vendor == 'cisco' and self.opersys == 'ios':
			command = 'show running-config | exclude ntp clock-period'
		elif self.hardware_vendor == 'cisco' and self.opersys == 'nxos':
			command = 'show running-config | exclude Time'
		elif self.hardware_vendor == 'cisco' and self.opersys == 'asa':
			command = 'show running-config'
		elif self.hardware_vendor == 'juniper':
			command = 'show configuration'
		elif(self.hardware_vendor == 'vyatta'):
			command = 'show configuration commands'
		elif self.hardware_vendor == 'f5':
			command = 'list ltm one-line'
			self.scpconnect()
			self.write_to_file(command)
			scp_flag = True
			self.scp_connect.scp_get_file('/var/local/ucs/config.ucs', '{}/backup-configs/{}'.format(self.get_pwd(),self.name))
			self.scp_connect.close()
			self.net_connect.disconnect()
		if self.hardware_vendor != 'juniper' or self.hardware_vendor != 'f5':
			self.connect()
			self.write_to_file(command,scp_flag,method)
			self.net_connect.disconnect()

	def exec_cmd(self,command):
		self.connect()
		output = self.net_connect.send_command(command)
		output = output.replace('\n','\n{}: '.format(self.name))
		output = re.sub(r'^','{}: '.format(self.name),output)
		print ('{}'.format(output))
		print('')
		self.net_connect.disconnect()

	def get_pwd(self):
		pwd = os.getcwd()

		return pwd

	def get_config(self,command):
		scp_flag = False
		method = 'get_config'
		if self.hardware_vendor == 'cisco':
			command = 'show running-config'
		elif self.hardware_vendor == 'f5':
			command = 'list one-line'
		self.connect()
		self.write_to_file(command,scp_flag,method)
		self.net_connect.disconnect()

	def get_diff(self,commands):
		scp_flag = False
		method = 'get_diff'
		self.connect()
		self.write_to_file(commands,scp_flag,method)
		self.net_connect.disconnect()

	def get_subdir(self,scp_flag):
		if self.hardware_vendor == 'f5' and scp_flag:
			sub_dir = 'ucs'
		else:
			sub_dir = 'configs'
		return sub_dir

	def write_to_file(self,command,scp_flag,method):
		if method == 'pull_cfgs':
			extention = ''
			if self.hardware_vendor == 'juniper' and 'display set' in command:
				extention = '.set'
			else:
				extention = '.conf'
			self.check_and_mkdir(scp_flag,method)
			with open('{}/backup-configs/{}/{}{}'.format(self.get_pwd(),self.get_subdir(scp_flag),self.name,extention), "w") as file:
				output = self.net_connect.send_command(command)
				file.write(output)
				file.close()
		elif method == 'get_config':
			self.check_and_mkdir(scp_flag,method)
			with open('{}/backup-configs/{}'.format(self.get_pwd(),self.name) + ".conf", "w") as file:
				output = self.net_connect.send_command(command)
				file.write(output)
				file.close()
		elif method == 'get_diff':
			self.check_and_mkdir(scp_flag,method)
			with open('{}/diff-configs/{}'.format(self.get_pwd(),self.name) + ".conf", "w") as file:
				output = self.net_connect.send_config_set(command)
				file.write(output)
				file.close()

	def check_and_mkdir(self,scp_flag,method):
		if method == 'pull_cfgs':
			os.makedirs('{}/backup-configs/{}/'.format(self.get_pwd(),self.get_subdir(scp_flag)),exist_ok=True)
		elif method == 'get_config':
			os.makedirs('{}/backup-configs/{}'.format(self.get_pwd(),self.name),exist_ok=True)	
		elif method == 'get_diff':
			os.makedirs('{}/diff-configs/{}'.format(self.get_pwd(),self.name),exist_ok=True)
