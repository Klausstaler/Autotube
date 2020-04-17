from selenium import webdriver
import time

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)
driver = webdriver.Chrome("chromedriver.exe", chrome_options=chrome_options)
driver.get('https://www.reddit.com/r/cscareerquestionsEU/comments/7l7q7z/what_are_intern_salaries_for_software_engineering/')
elem = driver.find_elements_by_class_name("header-user-dropdown")
elem[0].click()
time.sleep(0.5)
elem = driver.find_elements_by_class_name("_3m4MQxMy4WfgIkMhHh-UAg")
elem[0].click()
#image = driver.find_element_by_id("t1_drk7wyw").screenshot("test.png")
#print(image)
time.sleep(10)
driver.quit()