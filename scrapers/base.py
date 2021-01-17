
import re
import json
import time
from typing import List, Dict
from abc import abstractmethod

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from utilities import SaveToDisc



# Base Scraper
class Scraper:
    _header = {"User-Agent": str(UserAgent().chrome)}
    print(_header)
    _html_target = "script"
    _output_dir: str = None
    _save_format: str = None

    def __init__(self, ouput_dir:str, save_format: str):
        self._save_format = save_format
        self._output_dir = ouput_dir

    def scrap_and_save(self, filename: str, url: str) -> bool:
        data = self.scrap_page(url)
        if not data:
            print("[ERROR] No data from page scrapping process.")
            return False

        print("[INFO] Proceeding to save data from scrapping process.")  
        sd = SaveToDisc(self._output_dir, self._save_format)
        if not sd.save_file(filename, data):
            print("[ERROR] Saving scraping data to disk failed.")
            return False
        
        print("[INFO] Successfully saved scraped data to disk.")
        return True

    # asbtract method to be defined by each concrete Scraper
    @abstractmethod
    def scrap_page(self, url: str) -> None:
        pass

    # method to  make request to url, and get soup object
    def get_soup(self, url: str, sleep: int=1):
        try:
            print(f"[INFO] Waiting to make request for {sleep}s.")
            time.sleep(sleep)
            r = requests.get(url, headers=self._header)
            if not r.ok:
                print(f"[ERROR] Failure making request to {url}.")
                return None
            else:
                print(f"[INFO] Success making request to {url}.")
                html = r.text
                return BeautifulSoup(html, "html.parser")

        except Exception as e:
            print(f"[ERROR] {e}")
            return None
