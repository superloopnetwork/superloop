####################### ENGINE FUNCTIONS ########################

import initialize
import threading
import time
import datetime

def multithread_engine(object,redirect,commands):
	
	start_time = datetime.datetime.now()
	index = 0

	for i in object:
#		print("THESE ARE THE COMMANDS FED FROM MULTITHREAD: {}".format(commands[index]))
		if(redirect == 'push_config'):
			arguments = commands[index]
		elif(redirect == 'onscreen' or redirect == 'get_config'):
			arguments = commands
		my_thread = threading.Thread(target=getattr(object[index],redirect) , args=(arguments,))
		my_thread.start()

		index = index + 1

	main_thread = threading.currentThread()
	for some_thread in threading.enumerate():
		if some_thread != main_thread:
#			print(some_thread)
			some_thread.join()

	print('TIME ELAPSED: {}\n'.format(datetime.datetime.now() - start_time))

