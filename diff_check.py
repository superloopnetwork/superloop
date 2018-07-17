
def diff(): 
	ls = subprocess.Popen('ls /mnt/syslog/**/*.log | wc -l', shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) 
	list = ls.stdout.readline() 
	list = list.strip('\n') 
	diffcount = int(list) 
	ls.kill() 
	
	return devcount 
