####################### ENGINE FUNCTIONS ########################

import initialize
import threading
import time
import datetime

def multithread_engine(ntw_object,redirect,commands):
	
	start_time = datetime.datetime.now()
	index = 0
	for i in ntw_object:
		if(redirect == 'push_config'):
			arguments = commands[index]
		elif(redirect == 'exec_command' or redirect == 'get_config'):
			arguments = commands
		my_thread = threading.Thread(target=getattr(ntw_object[index],redirect) , args=(arguments,))
		my_thread.start()

		index = index + 1

	main_thread = threading.currentThread()
	for some_thread in threading.enumerate():
		if some_thread != main_thread:
#			print(some_thread)
			some_thread.join()

	print('[!] [DONE] [{}]\n'.format(datetime.datetime.now() - start_time))

