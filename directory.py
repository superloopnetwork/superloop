### THIS MODULE WILL RETURN THE CORRESPONDING DIRECTORY FOR THE APPLICATION TO OPEN THE FILE

def get_directory(platform,os,device_type):

	if(platform == 'cisco' and os == 'ios' and device_type == 'firewall'):
		directory = '/templates/cisco/ios/firewall/'
	elif(platform == 'cisco' and os == 'ios'and device_type == 'router'):
		directory = '/templates/cisco/ios/router/'
	elif(platform == 'cisco' and os == 'ios'and device_type == 'switch'):
		directory = '/templates/cisco/ios/switch/'

	return directory
