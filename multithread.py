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
		if(redirect[zero] == 'exec_command'):
			### ARGUMENT(S)/COMMAND(S) ARE BEING BLACKHOLED
			arguments = commands
			element = 0
		elif(redirect[index] == 'push_cfgs' or redirect[index] == 'get_config' or redirect[index] == 'get_diff'):
			arguments = commands[index]
			element = index
		my_thread = threading.Thread(target=getattr(ntw_object[index],redirect[element]) , args=(arguments,))
		my_thread.start()

		index = index + 1

	main_thread = threading.currentThread()
	for some_thread in threading.enumerate():
		if some_thread != main_thread:
#			print(some_thread)
			some_thread.join()

	print('[!] [SUCCESS] [{}]\n'.format(datetime.datetime.now() - start_time))

