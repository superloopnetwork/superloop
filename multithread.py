"""
	This module controls the multithreaded calls to Class BaseNode	
"""
import datetime
import initialize
import threading
import time

def multithread_engine(ntw_object,redirect,commands):
	start_time = datetime.datetime.now()
	index = 0
	zero = 0
	element = 0
	for node in ntw_object:
		if(redirect[zero] == 'exec_cmd' or redirect[zero] == 'pull_cfgs' ):
			"""
				argument(s)/command(s) are being blackholed
			"""
			arguments = commands
			element = 0
		elif(redirect[index] == 'push_cfgs' or redirect[index] == 'get_config' or redirect[index] == 'get_diff'):
			arguments = commands[index]
			element = index
		my_thread = threading.Thread(target=getattr(delayed_detection(),ntw_object[index],redirect[element]) , args=(arguments,))
		my_thread.start()
		index = index + 1
	main_thread = threading.currentThread()
	for some_thread in threading.enumerate():
		if some_thread != main_thread:
			some_thread.join()
	print('+ complete [{}]\n'.format(datetime.datetime.now() - start_time))

	return None

def delayed_detection():
	time.sleep(0)

	return None
