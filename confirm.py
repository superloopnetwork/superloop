"""
    This module controls the confirmation of pushing and pulling function
    from the user.
"""
import initialize 
from multithread import multithread_engine

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

	return None
