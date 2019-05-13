##!/usr/bin/python

def insertIntoDictionary(key, value, dictionary):
	if key not in dictionary:
		dictionary[key] = [value]
	else:
		dictionary[key].append(value)
	return dictionary 

def get_div_values (category, horizontal_placement, dictionary):
	horizontal = "/div[" + str(horizontal_placement) + "]"
	
	if(len(driver.find_elements_by_xpath(category + horizontal + "/h4")) != 0):
		technology = driver.find_element_by_xpath(category + horizontal + "/h4")
		companies = driver.find_elements_by_xpath(category + horizontal + "/ul/*")
	
		for j in range(len(companies)):
			company = driver.find_element_by_xpath(category + horizontal + "/ul/*[" + str(j+1) + "]")
			dictionary = insertIntoDictionary(technology.text.replace('\r', '').replace('\n', ''), 
				company.text.replace('\r', '').replace('\n', ''), dictionary)
	return dictionary

def record_progress(checked, checkpoint, record, position_in_file):
	checkpoint.seek(0)
	checkpoint.write("%d\n" % position_in_file)
	checked.write(record + "\r\n")

def cleanup(driver, checkpoint, checked):
	driver.quit()
	checkpoint.close()
	checked.close()

import selenium
import time
import traceback
import sys
import os
from selenium import webdriver

with open(sys.argv[1], "r") as file:
	lines = file.readlines()

checked = open("checked.txt", "a")

header = checked.readline()
if(header == None):
	checked.write("Municipality,Province,Coaxial Cable,DSL,Fixed Wireless,High capacity transport services,

checkpoint = open("checkpoint.txt", "r")

for line in checkpoint:
	starting_point = line
	if(starting_point == None):
		starting_point = 0
	else:
		starting_point = int(starting_point)

checkpoint.close()
checkpoint = open("checkpoint.txt", "w")

max_technologies = 7
xpath_area_info_tab = "//*[@id='test']"

try:
	driver = webdriver.Firefox()
	driver.get("https://www.ic.gc.ca/app/sitt/bbmap/hm.html?lang=eng")\

	inputElement = driver.find_element_by_id("gaddress")
	number_of_places = len(lines)

	for i in range(starting_point, number_of_places):
		ISP_data = {}
		line = lines[i]
		print("CHECKING::: %s" % line)
		print("%d out of %d\n\n" % (i, number_of_places))
		inputElement.send_keys(line)

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
	
			for column in (1,2):
				ISP_data = get_div_values(category, column, ISP_data)

		for technology in sorted(ISP_data):
			line = line + ","
			for company in ISP_data[technology]:
				line = line + company + ":"
			line = line[:-1]
		line = line[:-1]

		for i in range(max_technologies - len(ISP_data.keys())):
			line += ","
		line = line[:-1]
		line = line.replace('\r', '').replace('\n', '')
		inputElement.clear()
		print(line)
		print("\nRecording progress...\n")
		record_progress(checked, checkpoint, line, i)
	cleanup(driver, checked, checkpoint)
	
except KeyboardInterrupt as k:
	record_progress(checked, checkpoint, line, i)
	cleanup(driver, checked, checkpoint)

except Exception as e:
	record_progress(checked, checkpoint, line, i)
	print("the script has encountered an unexpected error and has stopped running. Please refer to the error message below.")
	print(traceback.format_exc())
	cleanup(driver, checked, checkpoint)