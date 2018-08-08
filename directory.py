### THIS MODULE WILL RETURN THE CORRESPONDING DIRECTORY FOR THE APPLICATION TO OPEN THE FILE

def get_directory(device_type):

	if(device_type == 'firewall'):
		directory = '/templates/cisco/ios/firewall/'
	elif(device_type == 'router'):
		directory = '/templates/cisco/ios/router/'
	elif(device_type == 'switch'):
		directory = '/templates/cisco/ios/switch/'

	return directory
