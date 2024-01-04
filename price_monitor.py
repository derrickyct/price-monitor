import os
import requests
import re
import sys
import time

from bs4 import BeautifulSoup
from selenium import webdriver

from scripts.helper.Email import send_mail
from scripts.helper.Get_Credential import get_password
from scripts.helper.Save_File import save_text
from scripts.helper.Read_File import read_csv

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


def time_count(func):
	def wrapper(*args, **kwargs):
		t1 = time.time()
		res = func(*args, **kwargs)
		t2 = time.time()-t1
		print(f'Took {t2} seconds to run {func.__name__}')
		return res
	
	return wrapper


@time_count
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


def collect_text(soup, tag, attrs):
	text = ""

	container = soup.find_all(tag, attrs=attrs)
	
	for para_text in container:
		text += f"{para_text.text}\n\n"
	return text


def check_discount(soup, attrs):
	tag_list = TAG_LIST
	for tag in tag_list:
		text = collect_text(soup, tag, attrs)

		if text:
			return True
	return False


@time_count
def price_compare(url, product_name, original_price):
	website_attrs_list = WEBSITE_ATTRS_LIST
	tag_list = TAG_LIST
	docs_folder = DOCS_FOLDER
	text_folder = TEXT_FOLDER

	print(product_name)

	website = url.lower().split('.com')[0].split('.')[1]
	if not website in website_attrs_list:
		# do something..
		pass
	
	soup = get_soup(url)
	
	attrs = website_attrs_list[website]
	
	for tag in tag_list:
		text = collect_text(soup, tag, attrs)
		
		if text:
			break

	if not text:
		print("Empty scrapped content...")
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
		