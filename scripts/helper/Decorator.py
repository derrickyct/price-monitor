import time

def time_count(func):
	def wrapper(*args, **kwargs):
		t1 = time.time()
		res = func(*args, **kwargs)
		t2 = time.time()-t1
		print(f'Took {t2} seconds to run {func.__name__}')
		return res
	
	return wrapper