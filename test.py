from Screenshotter import Screenshotter
from PIL import Image
from io import BytesIO
import time

x = Screenshotter("https://www.reddit.com/r/AskReddit/comments/f08dxb/would_you_watch_a_show_where_a_billionaire_ceo/", "f08dxb")
time.sleep(7.5)
element = x.driver.find_element_by_id("t1_fgs5ld9")
location = element.location_once_scrolled_into_view
size = element.size
x.driver.execute_script("arguments[0].scrollIntoView();", element)
print("At element")
time.sleep(5)
png = x.driver.get_screenshot_as_png() # saves screenshot of entire page

im = Image.open(BytesIO(png)) # uses PIL library to open image in memory
im.save("wholepage.png")
left = location['x']
top = im.size[1] - size["height"]
right = location['x'] + size['width']
bottom = im.size[1]


im = im.crop((left, top, right, bottom)) # defines crop points
im.save('screenshot0.png') # saves new cropped image
element.screenshot("screenshot2.png")

"""
location = element.location_once_scrolled_into_view
size = element.size
x.driver.execute_script("arguments[0].scrollIntoView();", element)
x.driver.execute_script("window.scrollBy(0,-85);")#scroll up by 85 pxls to ignore the stupid banner
png = x.driver.get_screenshot_as_png() # saves screenshot of entire page

im = Image.open(BytesIO(png)) # uses PIL library to open image in memory

left = location['x']
top = location['y'] + 85
right = location['x'] + size['width']
bottom = location['y'] + size['height'] + 85


im = im.crop((left, top, right, bottom)) # defines crop points
im.save('screenshot.png') # saves new cropped image
"""