from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from PIL import Image
import time
from io import BytesIO

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--start-maximized")
SCROLL_PAUSE_TIME = 0.5


class Screenshotter:
    def __init__(self, base_url, sort, id, darkmode=True):
        self.driver = webdriver.Chrome("chromedriver.exe", chrome_options=chrome_options)
        self.driver.get(f"{base_url}")
        self.url = self.driver.current_url
        self.driver.get(f"{base_url}+?sort={sort}/")
        self.id = id
        if darkmode:
            self.driver.find_elements_by_class_name("header-user-dropdown")[0].click()
            time.sleep(0.5)
            self.driver.find_elements_by_class_name("_3m4MQxMy4WfgIkMhHh-UAg")[0].click()
            self.driver.refresh()
            time.sleep(0.5)
        time.sleep(1)
        self.driver.find_element_by_xpath("//button[text()='I Agree']").send_keys("\n")
        time.sleep(1)
        self.driver.find_element_by_xpath("//button[starts-with(text(),'View entire discussion')]").click()
        time.sleep(1.5)

    def __del__(self):
        self.driver.quit()

    def screenshot_comment(self, id, path):
        # self.driver.find_element_by_id(f"t1_{id}").screenshot(path + ".png")
        # """
        try:
            elem = self.driver.find_element_by_id(f"t1_{id}")
            self._screenshot(elem, path + ".png")
        except NoSuchElementException as e:
            elem = self.driver.find_element_by_xpath(
                "//div[starts-with(@id,'moreComments') and @style='padding-left: 0px;']")
            ActionChains(self.driver).move_to_element(elem).perform()
            time.sleep(0.5)
            elem.click()
            time.sleep(3.5)
            self._scrollpage()
            elem = self.driver.find_element_by_id(f"t1_{id}")
            self._screenshot(elem, path + ".png")
        # """
        time.sleep(0.5)

    def _screenshot(self, element, path):
        location = element.location_once_scrolled_into_view
        size = element.size
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.driver.execute_script("window.scrollBy(0,-96);")  # scroll up by 95 pxls to ignore the title banner
        time.sleep(1)
        png = self.driver.get_screenshot_as_png()  # saves screenshot of entire page

        im = Image.open(BytesIO(png))  # uses PIL library to open image in memory
        left = location['x']
        top = location['y'] + 96
        right = location['x'] + size['width']
        bottom = location['y'] + size['height'] + 96
        im = im.crop((left, top, right, bottom))  # defines crop points
        im.save(path)  # saves new cropped image

    def expand_comment(self, id):
        self.driver.get(self.url + f"{id}/")
        """
        self.driver.find_element_by_xpath(
            "//div[starts-with(@id,'moreComments') and @style='padding-left: 21px;']").click()
        """
        if len(self.driver.page_source) > 300:
            time.sleep(2)
            self.driver.find_element_by_xpath("//button[starts-with(text(),'View entire discussion')]").click()
            time.sleep(2.5)

    def screenshot_title(self, path):
        elem = self.driver.find_element_by_id(f"t3_{self.id}")
        self._screenshot(elem, path + ".png")

    def _scrollpage(self):

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
