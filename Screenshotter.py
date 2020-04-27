from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
import time

chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications": 2}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--start-maximized")
#chrome_options.headless = True
SCROLL_PAUSE_TIME = 0.5

def _stitch_img(img1, img2):
    (width1, height1) = img1.size
    (width2, height2) = img2.size
    result_width = max(width1, width2)
    result_height = height1 + height2
    res = Image.new("RGB", (result_width, result_height))
    res.paste(im=img1, box=(0, 0))
    res.paste(im=img2, box=(0, height1))  # create new img with the old img and new comment piece
    return res

class Screenshotter:
    def __init__(self, base_url, sort, id, darkmode=True, delay=10):
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

    def screenshot_comment(self, ID, path):
        try:
            elem = self._explicit_selector(By.ID, f"t1_{ID}")
            self._screenshot(elem, path + ".png")
        except (NoSuchElementException, TimeoutException) as e:
            more_comments_path = "//div[starts-with(@id,'moreComments') and @style='padding-left: 0px;']"
            elem = self._explicit_selector(By.XPATH, more_comments_path)
            ActionChains(self.driver).move_to_element(elem).perform()
            self.driver.execute_script("arguments[0].click();", elem)
            self._scrollpage()
            self._screenshot_comment(ID, path, 0)
        time.sleep(0.5)

    def _screenshot_comment(self, ID, path, d):
        if d > 10:
            raise NoSuchElementException
        try:
            elem = self._explicit_selector(By.ID, f"t1_{ID}")
            self._screenshot(elem, path + ".png")
        except (NoSuchElementException, TimeoutException) as e:
            more_comments_path = "//div[starts-with(@id,'moreComments') and @style='padding-left: 0px;']"
            elem = self._explicit_selector(By.XPATH, more_comments_path)
            ActionChains(self.driver).move_to_element(elem).perform()
            elem.click()
            self._scrollpage()
            self._screenshot_comment(ID, path, d + 1)

    def _screenshot(self, element, path):
        location = element.location_once_scrolled_into_view
        if location['y'] > 3:
            time.sleep(5)
            location = element.location_once_scrolled_into_view
        size = element.size
        im = Image.new("RGB", (0, 0))
        HEADER_HEIGHT = 96
        TAB_HEIGHT = 925
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        self.driver.execute_script(
            f"window.scrollBy(0,{(-1)*HEADER_HEIGHT + location['y']});")  # scroll up by this amount to avoid header
        print((-1)*HEADER_HEIGHT + location['y'])
        while size["height"] > 0:  # stitch comment pieces together until we screenshotted whole comment
            png = self.driver.get_screenshot_as_png()  # saves screenshot of entire page
            new_img = Image.open(BytesIO(png))  # uses PIL library to open image in memory
            left = location['x']
            top = HEADER_HEIGHT
            right = location['x'] + size['width']
            sc_height = size['height'] + HEADER_HEIGHT
            max_sc_height = min(sc_height, TAB_HEIGHT)  # the maximum height of the comment is limited by the tab
            bottom = max_sc_height  # size and the comment size
            new_img = new_img.crop((left, top, right, bottom))  # defines crop points
            im = _stitch_img(im, new_img)
            height_decrease = min(sc_height, TAB_HEIGHT - HEADER_HEIGHT)
            size["height"] -= height_decrease
            self.driver.execute_script(f"window.scrollBy(0,{height_decrease});")
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
        # elem = self.driver.find_element_by_id(f"t3_{self.id}")
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
