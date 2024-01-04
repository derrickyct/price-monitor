import pandas as pd

def read_csv(path):
	path = path
	product_list = []
	
	df = pd.read_csv(path)
	df = df.reset_index()  # make sure indexes pair with number of rows

	for i, j in df.iterrows():
		product_list.append(list(j)[1:])
	return product_list