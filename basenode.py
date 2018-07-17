######################### BASE NODE ###########################

from netmiko import ConnectHandler
import base64
import re


class BaseNode(object):

	def __init__(self,ip,hostname,username,password,vendor,type):
		self.ip = ip
   		self.hostname = hostname
   		self.username = username
   		self.password = password
   		self.vendor = vendor
   		self.type = type
		self.password_decrypt= base64.b64decode(self.password)

	def connect(self):
		if (self.type == 'switch'):
			self.net_connect = ConnectHandler(self.ip,self.hostname,self.username,self.password_decrypt,self.get_secret(),port=65500,device_type=self.get_device())
		else:
			self.net_connect = ConnectHandler(self.ip,self.hostname,self.username,self.password_decrypt,self.get_secret(),device_type=self.get_device())
			
	def get_secret(self):
		enable_get_secret = ''
		if (self.location() == 'wdstk'):
			enable_get_secret = base64.b64decode(self.password)
		elif (self.location() == 'ktch'):
			enable_get_secret = base64.b64decode(self.password)

		return enable_get_secret
		
	def location(self):
		datacenter_location = ''
		if (self.type == 'firewall'):
			location_list = self.hostname.split('-')	
			datacenter_location = location_list[3]

		elif (self.type == 'switch' or self.type == 'router'):
			location_list = self.hostname.split('.')	
			datacenter_location = location_list[3]

		return datacenter_location

	def get_device(self):
		device_attribute = ''
		if (self.type == 'router' or self.type == 'switch'):
			device_attribute = 'cisco_ios'
		
		elif (self.type == 'firewall'):
			device_attribute = 'cisco_asa'

		return device_attribute

