import os
import requests
import re
import sys
import time

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver

from helper.sendEmail import send_mail
from helper.getCredential import get_password


PATH = "original_price.csv"
HEADERS = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}
TARGET_NAME = "Gmail App PW"

# email configuration
SENDER_EMAIL = "derrickyiuct@gmail.com"
RECEIVER_EMAIL = "derrickyiuct@gmail.com"
SUBJECT = "{product_name} price went down."
MESSAGE = "Product {product_name} price change from {original_price} to {new_price}, {percent_change}\% change. Here is the link: {url}"

WEBSITE_ATTRS_LIST = {
	'tuxmat': {'class': 'price'},
	'amazon': {'id': 'corePrice_feature_div'}
}
TAG_LIST = ['span', 'div', 'p']

def get_soup(url):
    try:
		# use selenium for js page scrapping
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        time.sleep(3)

        page = driver.page_source
        driver.quit()

        soup = BeautifulSoup(page, 'html.parser')
        
        return soup
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Error:", err)
    return None


# function to remove all the html tags and replace some with specific strings
def clean(text):
    rep = {"<br>": "\n", "<br/>": "\n", "<li>":  "\n"}
    rep = dict((re.escape(k), v) for k, v in rep.items()) 
    pattern = re.compile("|".join(rep.keys()))
    text = pattern.sub(lambda m: rep[re.escape(m.group(0))], text)
    text = re.sub('\<(.*?)\>', '', text)
    return text


def collect_text(soup, tag, attrs=None):
	text = ""

	# if attrs == None:
	# 	container = soup.find_all(tag)
	# else:
	container = soup.find_all(tag, attrs=attrs)
	
	for para_text in container:
		text += f"{para_text.text}\n\n"
	return text


def save_file(text, product_name):
	print(os.getcwd())
	if not os.path.exists('./product_price'):
		os.mkdir('./product_price')
	
	fname = f'product_price/{product_name}.txt'.replace(' ', '_')
	
	with open(fname, 'a') as writer:
		writer.write(text)


def read_csv():
	product_list = []
	
	df = pd.read_csv(PATH)
	df = df.reset_index()  # make sure indexes pair with number of rows

	for i, j in df.iterrows():
		product_list.append(list(j)[1:])
	return product_list


def check_discount(soup, attrs):
	for tag in TAG_LIST:
		text = collect_text(soup, tag, attrs)

		if text:
			return True
	return False


def price_compare(url, product_name, original_price):
	print(product_name)

	website = url.lower().split('.com')[0].split('.')[1]
	if not website in WEBSITE_ATTRS_LIST:
		# do something..
		pass
	
	soup = get_soup(url)
	
	attrs = WEBSITE_ATTRS_LIST[website]
	
	for tag in TAG_LIST:
		text = collect_text(soup, tag, attrs)
		
		if text:
			break

	if not text:
		print("Empty scrapped content...")
		sys.exit(1)
	
	matches = [float(match) for match in re.findall(r'\d+\.?\d+', text)]

	for match in matches:
		if original_price > match:
			save_file(match, product_name)
			print("Price went down!!!")
			return True, match
	print("Price not change...")
	return False, None


# TODO: machine learning engine to determine category of product, then search related website	


if __name__ == '__main__':
	flag = False
	product_dict = {}
	product_list = read_csv()
	
	for product in product_list:
		product_name, url, original_price = product
		
		price_drop, new_price = price_compare(url, product_name, original_price)

		# TODO: send one email including all price dropped items instead of one for each
		if price_drop:
			flag = True
			product_dict[product_name] = new_price
			percent_change = "{:.2f}".format((new_price - original_price) / original_price * 100)
		
	if not flag:
		password = get_password(TARGET_NAME)

		send_mail(
			SENDER_EMAIL,
			RECEIVER_EMAIL,
			SUBJECT.format(product_name=product_name), 
			MESSAGE.format(product_name=product_name, url=url, new_price=new_price, percent_change=percent_change),
			password=password
		)
		
	time.sleep(2) # delay 2 seconds between each requests
		