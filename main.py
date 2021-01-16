import re
import json
import time
import argparse
from typing import List, Dict
from abc import abstractmethod

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from utilities import SaveToDisc


#### TODO: LOGGGING THE PROCESS AS IT GOES
#### TODO: SCRAP multiple pages
#### TODO: csv
#### TODO: Comment

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--scrap", default="product", help="scrap category or product")
ap.add_argument("-u", "--url", default="https://www.lazada.sg/products/xiaomi-mi-note-10-lite-i729314564-s2320984579.html", help="url of Lazada category or product page")
ap.add_argument("-n", "--filename", default="testing", help="name of output file")
ap.add_argument("-f", "--format", default="json", help="format of output file. csv / json")
ap.add_argument("-o", "--output", default="output", help="location of output directory")
args = vars(ap.parse_args())

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
        sd = SaveToDisc(self._output_dir, self._save_format)
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

        html = r.text
        return BeautifulSoup(html, "html.parser")


class CategoryScraper(Scraper):
    def scrap_page(self, url: str) -> List:
        output_array = []
        stripped_url = url.strip()
        soup = self.get_soup(url)

        target_element = soup.find(HTML_TARGET, text=RE_PATTERN)
        if not target_element:
            return None

        target_str = str(target_element.next)[len(ELEMENT_TARGET):]
        json_data = json.loads(target_str)
        json_data = json_data.get(JSON_TARGETS[0]).get(JSON_TARGETS[1])

        ix = 0
        for e in json_data:
            output_array.append(dict())
            for d in CATEGORY_RELEVANT_DETAILS:
                output_array[ix][d] = e.get(d)
            ix += 1

        return output_array


class ProductScrapper(Scraper):
    _base = None

    def scrap_page(self, url: str) -> Dict:
        output_dict = {}
        soup = self.get_soup(url)
        ELEMENT_TARGET = '{"data":{"root":'
        RE_PATTERN = re.compile(ELEMENT_TARGET)
        target_element = soup.find(HTML_TARGET, text=RE_PATTERN)
        if not target_element:
            return None

        target_str = str(target_element.next)
        start_idx = target_str.find(ELEMENT_TARGET) + len(ELEMENT_TARGET)
        target_str = target_str[start_idx:]
        end_idx = target_str.find('"module_core":')
        target_str = target_str[:end_idx-1]
        json_data = json.loads(target_str)

        self._base = json_data.get("fields")

        output_dict = {
            "seller": self._get_seller_dict(),
            "product": self._get_product_dict(),
            "specifications": self._get_specifications_dict(),
            "variations": self._get_variations_dict(),
            "promotions": self._get_promotions_dict(),
            "delivery": self._get_delivery_dict(),
            "review": self._get_reviews_dict(),
            "images": self._get_images_dict()
        }
        return output_dict

    def _get_seller_dict(self) -> Dict:
        seller = self._base.get("seller")
        seller_dict = {
            "name": seller.get("name"),
            "rating": seller.get("percentRate")}

        return seller_dict
        
    def _get_delivery_dict(self) -> Dict:
        delivery = self._base.get("deliveryOptions")
        delivery_dict = {
            "options": [
                {"fee": d[0].get("fee"),
                "time": d[0].get("duringTime")
                }
                for d in delivery.values() if d]  
        }
        return delivery_dict

    def _get_promotions_dict(self) -> Dict:
        promotions = self._base.get("promotionTags").get("data")
        promotions_dict = {
            "vouchers": [
                {"name": p[0].get("name"),
                "description": p[0].get("description")
                }
                for p in promotions.values() if p]
        }
        return promotions_dict

    def _get_product_dict(self) -> Dict:
        product = self._base.get("tracking")
        product_dict = {
            "name": product.get("pdt_name"),
            "image": f'https:{product.get("pdt_photo")}',
            "price": product.get("pdt_price"),
            "discount": product.get("pdt_discount"),
            "categories": product.get("pdt_category"),   
        }
        return product_dict

    def _get_variations_dict(self) -> Dict:
        variations = self._base.get("productOption").get("skuBase").get("properties")
        variations_dict = {}
        for i in variations:
            variations_dict[i.get("name")] = [
                {"name": v.get("name"),
                "image": v.get("image")
                } 
                for v in i.get("values") if v]
        return variations

    def _get_reviews_dict(self) -> Dict:
        review = self._base.get("review")
        review_dict = {
            "averageRating": review.get("ratings").get("average"),
            "rateCount": review.get("ratings").get("rateCount"),
            "reviewCount": review.get("ratings").get("reviewCount"),
            "visible_reviews": [ 
                {"rating": r.get("rating"),
                "content": r.get("reviewContent"),
                "reviewer": r.get("reviewer"),
                "reviewTime": r.get("reviewTime")
                }     
                for r in review.get("reviews") if r]
        }
        return review_dict

    def _get_specifications_dict(self) -> Dict:
        return self._base.get("specifications")

    def _get_images_dict(self) -> Dict:
        images = self._base.get("skuGalleries")
        images_dict = {}
        for n, i in enumerate(images.values()):
            images_dict[n] = [f'https:{v.get("src")}' for v in i if v]

        return images_dict
        


# REGION = BASE_URL.split(".")[-1].upper()
if __name__ == "__main__":
    url = args.get("url")
    filename = args.get("filename")
    file_format = args.get("format")
    output_dir = args.get("output")

    if args.get("scrap") == "category":
        cs = CategoryScraper(output_dir, file_format)
        cs.scrap_and_save(filename, url)

    elif args.get("scrap") == "product":
            ps = ProductScrapper(output_dir, file_format)
            ps.scrap_and_save(filename, url)
    else:
        print(f"[ERROR] invalid scap operation: {args.get('scrap')}")