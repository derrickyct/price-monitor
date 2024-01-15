import re
import requests
import time

from bs4 import BeautifulSoup
from selenium import webdriver

from scripts.helper.Decorator import time_count

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
	except requests.exceptions.HTTPError as errHttp:
		print("HTTP Error:", errHttp)
	except requests.exceptions.ConnectionError as errConnection:
		print("Error Connecting:", errConnection)
	except requests.exceptions.Timeout as errTimeout:
		print("Timeout Error:", errTimeout)
	except requests.exceptions.RequestException as err:
		print("Error:", err)
	return None


# 
def clean(text):
	"""
	To remove all the html tags and replace some with specific strings
	"""
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
