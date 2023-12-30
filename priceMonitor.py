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
SUBJECT = "{product_name} price went down"
MESSAGE = "Product {product_name} price went down, here is the link: {url}"


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


def collect_text(soup, tag, style=None):
	text = ""

	if style == None:
		container = soup.find_all(tag)
	else:
		container = soup.find_all(tag, attrs=eval(style))
	
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


def price_compare(url, product_name, original_price, tag, style):
	print(product_name)

	soup = get_soup(url)
	text = collect_text(soup, tag, style)

	if not text:
		print("Empty scrapped content...")
		sys.exit(1)
	
	matches = [float(match) for match in re.findall(r'\d+\.?\d+', text)]

	for match in matches:
		if original_price > match:
			save_file(text, product_name)
			print("Price went down!!!")
			return True
		
		print("Price not change...")
	return False

if __name__ == '__main__':
	product_list = read_csv()
	
	for product in product_list:
		product_name, url, original_price, tag, style = product
		
		price_drop = price_compare(url, product_name, original_price, tag, style)

		if price_drop:
			password = get_password(TARGET_NAME)

			send_mail(SENDER_EMAIL, RECEIVER_EMAIL, SUBJECT.format(product_name=product_name), 
							MESSAGE.format(product_name=product_name, url=url), password=password)
			
		time.sleep(2) # delay 2 seconds between each requests
		