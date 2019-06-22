#!/usr/bin/python

# # > A list for each type of technology the script might encounter
# # > HCTS = High Capacity Transport Services
coax_cable = []
dsl = []
fibre_to_home = []
fixed_wireless = []
HCTS = []
mobile_wireless = []
satellite = []
file_columns = "Municipality,Province,Coaxial Cable,DSL,Fibre to the Home,Fixed Wireless,High capacity transport services,Mobile Wireless,Satellite\n"
i = 0

# # > the start of the xpath to the area on the screen with the info. 
xpath_area_info_tab = "//*[@id='test']"

def remove_EOLs(s):
	return s.replace('\r', '').replace('\n', ' ')

def get_div_values (category, horizontal_placement):
	horizontal = "/div[" + str(horizontal_placement) + "]"
	
	if(len(driver.find_elements_by_xpath(category + horizontal + "/h4")) != 0):
		technology = remove_EOLs(driver.find_element_by_xpath(category + horizontal + "/h4").text)
		companies = driver.find_elements_by_xpath(category + horizontal + "/ul/*")
	
		for j in range(len(companies)):
			company = remove_EOLs(driver.find_element_by_xpath(category + horizontal + "/ul/*[" + str(j+1) + "]").text)
			print("\nAdding company:" + company + " to the list " + technology)
			if(technology == "Coaxial Cable"):
				coax_cable.append(company)
			elif(technology == "DSL"):
				dsl.append(company)
			elif(technology == "Fibre to the home"):
				fibre_to_home.append(company)
			elif(technology == "Fixed Wireless"):
				fixed_wireless.append(company)
			elif(technology == "High capacity transport services"):
				HCTS.append(company)
			elif(technology == "Mobile Wireless"):
				mobile_wireless.append(company)
			elif(technology == "Satellite"):
				satellite.append(company)
			else:
				raise Exception("Error: encountered a technology that you and Kent do not know about!\n" + 
					"It does not appear to be a Coax Cable, DSL, Fibre To Home, Fixed Wireless\n" +
					"High Transport Services, Mobile Wireless, or Satellite technology.\n" + 
					"Kent programmed this error to occur if the script encountered a column to add\n" +
					"in to the database, so let him know that this happened, the fix should be really easy!" + 
					"The unexpected technology had this name: \"" + technology + "\"\n")

def make_checkpoint(checkpoint, number_of_places_checked):
	checkpoint.seek(0)
	if(i > 0):
		checkpoint.write("%d\n" % number_of_places_checked)
	else:
		checkpoint.write("0\n")

def record_progress(checked, checkpoint, place, number_of_places_checked):
	make_checkpoint(checkpoint, number_of_places_checked)
	checked.write("%s,%s,%s,%s,%s,%s,%s,%s\n" % 
		(place, 
		';'.join([str(x) for x in coax_cable]),
		';'.join([str(x) for x in dsl]),
		';'.join([str(x) for x in fibre_to_home]), 
		';'.join([str(x) for x in fixed_wireless]), 
		';'.join([str(x) for x in HCTS]),
		';'.join([str(x) for x in mobile_wireless]),
		';'.join([str(x) for x in satellite])     
		) 
	)

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

checked = open("checked.txt", "a+")
with open("checked.txt", "r") as rd_only:
	first_line = rd_only.readline()
	
if("Municipality,Province" not in first_line):
	checked.write(file_columns)

checkpoint = open("checkpoint.txt", "a+")
checkpoint.seek(0)

starting_point = checkpoint.read(1)
if(starting_point == None or starting_point == ''):
	starting_point = 0
else:
	starting_point = int(starting_point)

checkpoint.close()
checkpoint = open("checkpoint.txt", "w")

try:
	driver = webdriver.Firefox()
	driver.get("https://www.ic.gc.ca/app/sitt/bbmap/hm.html?lang=eng")
	inputElement = driver.find_element_by_id("gaddress")

	with open(sys.argv[1], "r") as file:
		places = file.readlines()
	number_of_places = len(places)
	for i in range(starting_point, number_of_places):
		place = remove_EOLs(places[i])
		print("ABOUT TO CHECK::: %s" % place)
		print("%d out of %d\n\n" % (i + 1, number_of_places + 1))
		inputElement.send_keys(place)
		driver.find_element_by_xpath("//input[@value='Search']").click()
		driver.find_element_by_id("details-panel1-lnk").click()
		
		# # > wait for elements to appear
		time.sleep(5)

		# # > check for error messages
		headers = driver.find_elements_by_xpath(xpath_area_info_tab + "/h3")
		number_to_skip = 2 + len(headers)
		categories = driver.find_elements_by_xpath(xpath_area_info_tab + "/div")

		# # > skip the empty div at the end 
		numberOfCategories = len(categories) - 1

		# # > "number_to_Skip" is used so that we skip over estimated population and households, which are the first 4 values
		# # > These values also have a different div structure, and the xpath that I'm using will break on them
		for i in range(number_to_skip, numberOfCategories):
			category = xpath_area_info_tab + "/div[" + str(i) + "]"
			technologies = driver.find_elements_by_xpath(category)
	
			for column in (1,2):
				get_div_values(category, column)
		inputElement.clear()
		print(place)
		print("\nFinished checking, Recording progress...\n")
		record_progress(checked, checkpoint, place, i)
		
		coax_cable = []
		dsl = []
		fibre_to_home = []
		fixed_wireless = []
		HCTS = []
		mobile_wireless = []
		satellite = []
		
		# # > delay, so that the script behaves more like a regular user (taking a break between entries)
		time.sleep(30)
	cleanup(driver, checked, checkpoint)
	
except KeyboardInterrupt as k:
	make_checkpoint(checkpoint, i - 1)
	cleanup(driver, checked, checkpoint)

except Exception as e:	
	make_checkpoint(checkpoint, i - 1)
	print("the script has encountered an unexpected error and has stopped running. Please refer to the error message(s) above and/or below.")
	print(traceback.format_exc())
	cleanup(driver, checked, checkpoint)
