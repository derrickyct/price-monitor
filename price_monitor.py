import os
import re
import sys

from scripts.helper.Email import send_mail
from scripts.helper.Get_Credential import get_password
from scripts.helper.Save_File import save_text
from scripts.helper.Read_File import read_csv
from scripts.helper.Decorator import time_count

import scripts.Api_Call as api_func
import scripts.Soup_Call as soup_func

from dotenv import load_dotenv

load_dotenv()

# .env variables
CSV_PATH = os.getenv('CSV_PATH')
TARGET_NAME = os.getenv('TARGET_NAME')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
SUBJECT = os.getenv('SUBJECT')
MESSAGE = os.getenv('MESSAGE')
DOCS_FOLDER=os.getenv('DOCS_FOLDER')
TEXT_FOLDER=os.getenv('TEXT_FOLDER')

WEBSITE_ATTRS_LIST = {
	'tuxmat': {'class': 'price'},
	'amazon': {'id': 'corePrice_feature_div'}
}
TAG_LIST = ['span', 'div', 'p']


def get_domain(url):
	"""
	Get the domain name.
	"""
	website_attrs_list = WEBSITE_ATTRS_LIST

	website = url.lower().split('.com')[0].split('.')[1]
	if not website in website_attrs_list:
		# do something..
		print(f"Url - ${url} not on the list!")
		sys.exit(1)
	
	return website


# TODO: make price compare function more reusable
@time_count
def price_compare(url, product_name, original_price):
	"""
	Get updated product price using get_soup function and compare the scrapped price with original price.

	:Args:
	 - url - URL address of the product page 
	 - product_name - Name of the product
	 - original_price - Original price of the product
	"""
	tag_list = TAG_LIST
	docs_folder = DOCS_FOLDER
	text_folder = TEXT_FOLDER

	print(product_name)
	domain_name = get_domain(url)

	# TODO: call api or soup according to the domain name
		
	soup = get_soup(url)
	

	attrs = website_attrs_list[domain_name]
	print(f"attrs: ${attrs}")
	for tag in tag_list:
		print(f"tag: ${tag}")
		text = collect_text(soup, tag, attrs)
		
		if text:
			break

	if not text:
		print("Empty scrapped content...")
		save_text(str(soup), "new", docs_folder, text_folder)
		sys.exit(1)
	
	matches = [float(match) for match in re.findall(r'\d+\.?\d+', text)]

	for match in matches:
		if original_price > match:
			save_text(str(match), product_name, docs_folder, text_folder)
			print("Price went down!!!")
			return True, match
		elif original_price < match:
			print("Price went up!!!")
		
	print("Price not change...")
	return False, None


# TODO: machine learning engine to determine category of product, then search related website	

# TODO: move soup function to a new file

# TODO: create bestbuy api functions 

if __name__ == '__main__':
	csv_path = CSV_PATH
	sender_email = SENDER_EMAIL
	receiver_email = RECEIVER_EMAIL
	subject = SUBJECT
	message = MESSAGE
	target_name = TARGET_NAME

	flag = False
	product_dict = {}
	product_list = read_csv(csv_path)
	
	for product in product_list:
		product_name, url, original_price = product
		
		price_drop, new_price = price_compare(url, product_name, original_price)

		if price_drop:
			flag = True
			percent_change = "{:.2f}".format((new_price - float(original_price)) / float(original_price) * 100)
			product_dict[product_name] = [url, original_price, new_price, percent_change]
		
	if flag:
		message_list = []
		for name, info in product_dict.items():
			message_list.append(
				message.format(product_name=name, url=info[0], original_price=info[1], new_price=str(info[2]), percent_change=str(info[3]))
			)

		email_message = ' '.join(message_list)
		password = get_password(target_name)

		send_mail(
			sender_email,
			receiver_email,
			subject.format(product_name=product_name), 
			email_message,
			password=password
		)
		