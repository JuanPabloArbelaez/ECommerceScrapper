import re
import json
import time
from typing import List, Dict
from abc import abstractmethod

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from utilities import SaveToDisc


#### TODO: LOGGGING THE PROCESS AS IT GOES
#### TODO: ARGPARSER
#### TODO: Comment
#### TODO: ProductScrapper


HEADER = {"User-Agent": str(UserAgent().chrome)}
HTML_TARGET = "script"
ELEMENT_TARGET = "window.pageData="
RE_PATTERN = re.compile(ELEMENT_TARGET)
JSON_TARGETS = ("mods", "listItems")

CATEGORY_RELEVANT_DETAILS = ["brandName", "name", "price", "discount", "ratingScore"]


class Scraper:
    _save_format: str = None
    _output_dir: str = None
    
    _save_format: str = None
    def __init__(self, ouput_dir:str, save_format: str):
        self._save_format = save_format
        self._output_dir = ouput_dir

    def scrap_and_save(self, filename: str, url: str) -> bool:
        data = self.scrap_page(url)
        sd = SaveToDisc(self._output_dir ,self._save_format)
        if sd.save_file(filename, data):
            return True
        else:
            return False

    @abstractmethod
    def scrap_page(self, url: str) -> None:
        pass

    def get_soup(self, url: str):
        r = requests.get(url, headers=HEADER)
        time.sleep(1)
        if not r.ok:
            return None

        html = r.content
        return BeautifulSoup(html, "html.parser")


class CategoryScraper(Scraper):
    def scrap_page(self, url: str) -> List:
        output_array = []
        soup = self.get_soup(url)

        target_element = soup.find(HTML_TARGET, text=RE_PATTERN)
        if not target_element:
            return None

        target_str = str(target_element.next)[len(ELEMENT_TARGET):]
        json_data = json.loads(target_str)
        json_data = json_data.get(JSON_TARGETS[0]) # reduce one line?
        json_data = json_data.get(JSON_TARGETS[1])

        ix = 0
        for e in json_data:
            output_array.append(dict())
            for d in CATEGORY_RELEVANT_DETAILS:
                output_array[ix][d] = e.get(d)
            ix += 1

        return output_array


class ProductScrapper(Scraper):
    def scrap_page(self, url: str) -> Dict:
        output_dict = []
        soup = self.get_soup(url)

        ELEMENT_TARGET = "var __moduleData__ ="
        RE_PATTERN = re.compile(ELEMENT_TARGET)

        target_element = soup.find(HTML_TARGET, text=RE_PATTERN)
        if not target_element:
            return None

        target_str = str(target_element.next)
        start_idx = target_str.find(ELEMENT_TARGET)
        target_str = target_str[start_idx:]
        start_idx = target_str.find('"root":')
        target_str = target_str[start_idx:]
        end_idx = target_str.find(";\n")
        target_str = target_str[:end_idx]
        end_str = target_str[-30:]
        # json_data = json.loads(target_str)


        print(target_str)
        json_data = json.loads(target_str)




# BASE_URL = "https://www.lazada.vn"
BASE_URL = "https://www.lazada.co.th"
# CATEGORY = "dieu-khien-choi-game"

CATEGORY = "shop-laptops"
OUTPUT_DIR = "output/"
FORMAT = "csv"

REGION = BASE_URL.split(".")[-1].upper()
FILENAME = f"{REGION}_{CATEGORY}"
DEFAULT_URL = f"{BASE_URL}/{CATEGORY}/"

if __name__ == "__main__":
    # cs = CategoryScraper(OUTPUT_DIR, FORMAT)
    # cs.scrap_and_save(FILENAME, DEFAULT_URL)

    ps = ProductScrapper(OUTPUT_DIR, FORMAT)
    ps.scrap_and_save("testing", 'https://www.lazada.sg/products/xiaomi-mi-note-10-lite-i729314564-s2320984579.html?spm=a2o42.searchlistcategory.list.115.af433f03j1LDQv&search=1')
