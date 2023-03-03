# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
from touyantong.settings import IMAGE_SERVICE, TAGS
import re


def is_standard_image(img):
    previous_deep = 0
    while previous_deep < 3:
        img = img.find_previous("p")
        if not img:
            return [False, None]
        if re.match(r"图\d", img.text.replace(" ", "")):
            img = re.sub(r"[\s+\.\!\/_,$%:^*(+\"\']+|[表图\d+——：！，。？、~@#￥%……&*（）]+", "", img.text.replace(" ", ""))
            return [True, img]
        else:
            previous_deep += 1
            continue
    return [False, None]


def extract_images(soup, hash):
    all_img = soup.find_all("img")
    r = [{"caption": is_standard_image(img)[1],
          "src": IMAGE_SERVICE + hash + "/" + img.get("src")} for img in all_img if is_standard_image(img)[0]]
    if not all_img:
        return []
    return r


def main(origin, category, hash):
    soup = BeautifulSoup(origin, "lxml")
    try:
        type_id = [tag["type_id"] for tag in TAGS if tag["abbreviation"] == category][0]
    except IndexError:
        return []
    if type_id != 3:
        return []
    return extract_images(soup, hash)

