from selenium import webdriver
from selenium.webdriver.common.by import By
import time

driver = webdriver.Chrome()

driver.get("https://www.google.com")

# print out the page title, stored in the driver object:
title = driver.title
print("Visited the page entitled: " + title)

# Wait a second to load the entire webpage... but actually let's do 5 seconds so you see it!
time.sleep(5)

print("\n\nFirst, Blase wants to print out the page's HTML source:")
rawhtml = driver.page_source
print(rawhtml)
 
print("\n\nNow Blase wants to print out the rendered contents of the page:")
contents = driver.find_element(By.XPATH, "/html/body").text
print(contents)

driver.quit()