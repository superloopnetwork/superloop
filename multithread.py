### MULTITHREAD_ENGINE FUNCTION ENABLES SIMULTANEOUSLY CONCURRENT TASKS TO OCCUR
### DELAYED_DETECTION FUNCTION ACCOMDDATES SLOWER ENVIRONMENTS. FOR EXAMPLE, TACACS SERVER BEING HAMMERED
### WITH AUTHENTICATION REQUESTS FROM NODES THAT IT CANNOT KEEP UP
### ADJUST THE SLEEP TIME (IN SECONDS) TO CONFORM TO YOUR NETWORK

####################### ENGINE FUNCTIONS ########################

import initialize
import threading
import time
import datetime

def multithread_engine(ntw_object,redirect,commands):
	
	start_time = datetime.datetime.now()
	index = 0
	zero = 0
	element = 0
	for i in ntw_object:
		if(redirect[zero] == 'exec_cmd' or redirect[zero] == 'pull_cfgs' ):
			### ARGUMENT(S)/COMMAND(S) ARE BEING BLACKHOLED
			arguments = commands
			element = 0
		elif(redirect[index] == 'push_cfgs' or redirect[index] == 'get_config' or redirect[index] == 'get_diff'):
			arguments = commands[index]
			element = index
		my_thread = threading.Thread(delayed_detection(), target=getattr(ntw_object[index], redirect[element]) , args=(arguments,))
		my_thread.start()

		index = index + 1

	main_thread = threading.currentThread()
	for some_thread in threading.enumerate():
		if some_thread != main_thread:
#			print(some_thread)
			some_thread.join()

	print('[\u2713] [complete] [{}]\n'.format(datetime.datetime.now() - start_time))

def delayed_detection():
#	time.sleep(0.500)
	
	return None
