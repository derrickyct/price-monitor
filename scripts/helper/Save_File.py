import os

# to save text into .txt file
# folder inputs in the order of parent folder to children folder
def save_text(text, product_name, *folders):
	current_directory = os.getcwd()
	folder_path = current_directory
	
	for folder in folders:
		folder_path = os.path.join(folder_path, folder)
	
	if not os.path.exists(folder_path):
		os.mkdir(folder_path)
		
	fname = f'{product_name}.txt'.replace(' ', '_')
	directory_path = os.path.join(folder_path, fname)
	
	with open(directory_path, 'a') as writer:
		writer.write(text)
