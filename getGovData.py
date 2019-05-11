##!/usr/bin/python

def insertIntoDictionary(key, value, dictionary):
	if key not in dictionary:
		dictionary[key] = [value]
	else:
		dictionary[key].append(value)
	return dictionary 

def get_div_values (category, horizontal_placement, dictionary):
	horizontal = "/div[" + str(horizontal_placement) + "]"
	technology = driver.find_element_by_xpath(category + horizontal + "/h4")
	companies = driver.find_elements_by_xpath(category + horizontal + "/ul/*")
	
	for j in range(len(companies)):
		company = driver.find_element_by_xpath(category + horizontal + "/ul/*[" + str(j+1) + "]")
		dictionary = insertIntoDictionary(company.text, technology.text.rstrip(), dictionary)
	return dictionary

import selenium
import time
from selenium import webdriver

ISP_data = {}
xpath_area_info_tab = "//*[@id='test']"
driver = webdriver.Firefox()
driver.get("https://www.ic.gc.ca/app/sitt/bbmap/hm.html?lang=eng")\

inputElement = driver.find_element_by_id("gaddress")
inputElement.send_keys("Arnold's Cove")

driver.find_element_by_xpath("//input[@value='Search']").click()
#print(searchButton)

driver.find_element_by_id("details-panel1-lnk").click()
time.sleep(30)

#check for error messages
headers = driver.find_elements_by_xpath(xpath_area_info_tab + "/h3")
number_to_skip = 2 + len(headers)

categories = driver.find_elements_by_xpath(xpath_area_info_tab + "/div")

#skip the empty div at the end 
numberOfCategories = len(categories) - 1

for i in range(number_to_skip, numberOfCategories):
	#So that we skip over estimated population and households, which are the first 4 values
	#These values also have a different div structure, and the xpath that I'm using will break on them
	category = xpath_area_info_tab + "/div[" + str(i) + "]"
	
	technologies = driver.find_elements_by_xpath(category)
	
	ISP_data = get_div_values(category, 1, ISP_data)
	ISP_data = get_div_values(category, 2, ISP_data)

for company in ISP_data:
	line = company + ":"
	for technology in ISP_data[company]:
		line = line + technology + ","
	line = line[:-1]
	print(line)
driver.quit()