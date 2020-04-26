from PIL import Image, ImageFont, ImageDraw
from enum import Enum
import re

IMG_HEIGHT = 720
IMG_WIDTH = 1280


class Color(Enum):
    WHITE = (255, 255, 255)
    ORANGE = (255, 128, 0)
    RED = (255, 0, 0)
    GREEN = (112, 210, 13)
    BLUE = (0, 0, 255)


def draw_text(img_draw, text, color):
    posList = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    font = find_fontsize(img_draw, text)
    num_rows = (IMG_HEIGHT//img_draw.textsize(text, font)[1])
    text = format_text(text, num_rows, font)
    #for val in posList:
    #    img_draw.text((val[0], val[1]), text, Color.WHITE.value, font)
    img_draw.text((0, 0), text, color, font)

def find_fontsize(img_draw, text):
    font_size = 128
    font = ImageFont.truetype("C:/Windows/Fonts/ARLRDBD.TTF", font_size)
    text_size = img_draw.textsize(text, font)
    num_rows = (IMG_HEIGHT // text_size[1])
    while text_size[0] // num_rows >= IMG_WIDTH:
        font_size -= 1
        font = ImageFont.truetype("C:/Windows/Fonts/ARLRDBD.TTF", font_size)
        text_size = img_draw.textsize(text, font)
        num_rows = (IMG_HEIGHT // text_size[1])
    return font

def format_text(text, num_rows, font):
    i = 0
    new_text = ""
    print(text)
    while i != num_rows + 1:
        text = re.split(r'(\s+)', text)
        splitpoint = find_splitpoint(img_draw, text, font)
        if splitpoint == -1:
            new_text += "".join(text)
        else:
            print(text[:splitpoint])
            new_text += "".join(text[:splitpoint]) + "\n"
            text = "".join(text[splitpoint:])
        i += 1
    return new_text


def find_splitpoint(img_draw, text, font):
    l = 0
    r = len(text)
    idx = -1
    while l <= r:
        mid = l + (r - l) // 2
        text_size = img_draw.textsize("".join(text[:mid]), font)
        if text_size[0] <= IMG_WIDTH:
            l = mid + 1
            idx = mid
        elif text_size[0] > IMG_WIDTH:
            r = mid - 1
    return idx


im = Image.open("resources/images/base.jpg")
img_draw = ImageDraw.Draw(im)
for i, color in enumerate(Color):
    im = im.copy()
    img_draw = ImageDraw.Draw(im)
    string = "r/askreddit \nLawyers who read wills to families, what is the most interesting bizarre, offensive, surprising thing you have had to read out loud?"
    # string = "r/askreddit \nBill Gates passed away at the age of 95."
    draw_text(img_draw, string, color.value)
    im.save(f"first{i}.png")
