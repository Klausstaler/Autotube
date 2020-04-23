from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
from io import BytesIO

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--start-maximized")
SCROLL_PAUSE_TIME = 0.5

class Screenshotter:
    def __init__(self, base_url, sort, id, darkmode=True, delay=60):
        self.driver = webdriver.Chrome("chromedriver.exe", chrome_options=chrome_options)
        self.driver.get(f"{base_url}")
        self.url = self.driver.current_url
        self.delay = delay
        self.driver.get(f"{base_url}+?sort={sort}")
        self.id = id
        if darkmode:
            user_drop = self._explicit_selector(By.CLASS_NAME, 'header-user-dropdown')
            user_drop.click()
            nightmode = self._explicit_selector(By.CLASS_NAME, '_3m4MQxMy4WfgIkMhHh-UAg')
            nightmode.click()
            self.driver.refresh()
        cookie_button = self._explicit_selector(By.XPATH, "//button[text()='I Agree']")
        cookie_button.send_keys("\n")
        discussion_b = self._explicit_selector(By.XPATH, "//button[starts-with(text(),'View entire discussion')]")
        discussion_b.click()

    def __del__(self):
        self.driver.quit()

    def screenshot_comment(self, id, path):
        try:
            elem = self._explicit_selector(By.ID, f"t1_{id}")
            self._screenshot(elem, path + ".png")
        except (NoSuchElementException, TimeoutException) as e:
            more_comments_path = "//div[starts-with(@id,'moreComments') and @style='padding-left: 0px;']"
            elem = self._explicit_selector(By.XPATH,  more_comments_path)
            ActionChains(self.driver).move_to_element(elem).perform()
            elem.click()
            self._scrollpage()
            elem = self._explicit_selector(By.ID, f"t1_{id}")
            self._screenshot(elem, path + ".png")
        time.sleep(0.5)

    def _screenshot(self, element, path):
        location = element.location_once_scrolled_into_view
        size = element.size
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.driver.execute_script("window.scrollBy(0,-96);")  # scroll up by 95 pxls to ignore the title banner
        png = self.driver.get_screenshot_as_png()  # saves screenshot of entire page

        im = Image.open(BytesIO(png))  # uses PIL library to open image in memory
        left = location['x']
        top = location['y'] + 96
        right = location['x'] + size['width']
        bottom = location['y'] + size['height'] + 96
        im = im.crop((left, top, right, bottom))  # defines crop points
        im.save(path)  # saves new cropped image

    def expand_comment(self, id):
        self.driver.execute_script("window.open("");")
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.get(self.url + f"{id}/")
        if len(self.driver.page_source) > 300:
            discussion_path = "//button[starts-with(text(),'View entire discussion')]"
            entire_discussion = self._explicit_selector(By.XPATH, discussion_path)
            entire_discussion.click()

    def screenshot_title(self, path):
        elem = self._explicit_selector(By.ID, f"t3_{self.id}")
        #elem = self.driver.find_element_by_id(f"t3_{self.id}")
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

    def _explicit_selector(self, method, logic):
        return WebDriverWait(self.driver, self.delay).until(EC.presence_of_element_located((method, logic)))
