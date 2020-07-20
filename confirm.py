### THIS MODULE CONTROLS THE CONFIRMATION OF PUSHING FROM THE USER.
### BOTH PUSH_CFGS AND PUSH_LOCAL UTILIZES THIS MODULE.

from multithread import multithread_engine
import initialize 

def confirm(redirect,commands):

	index = 0

	if(redirect[index] == 'push_cfgs'):
		check = str(input("Push configs? [y/N]: ")).strip()
	else:
		check = str(input("Pull configs? [y/N]: ")).strip()
	try:
		if check[0] == 'y':
			multithread_engine(initialize.ntw_device,redirect,commands)
		elif check[0] == 'N':
			return False
		else:
			print("RuntimeError: aborted at user request")

	except Exception as error:
		print("ExceptionError: an exception occured")
		print(error)
