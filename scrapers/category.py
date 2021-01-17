
from scrapers.base import *



class CategoryScraper(Scraper):
    _page_notation = "?page="              # to add at the end of the url string and change page
    _element_target = "window.pageData="   # string to create a reg expression and find in soup
    _json_targets = ("mods", "listItems")  # path inside the generated json to get the products data
    
    _relevant_details = (                  # details to get from the json dict 
        "name",
        "brandName",
        "description",
        "priceShow",
        "discount",
        "location",
        "sellerName",
        "ratingScore",
        "categories")
    
    def scrap_page(self, url: str) -> List:
        output_array = []
        page_idx = 1
        
        while True:
            print(f"[INFO] Attempting to scrape category page: {page_idx} ...")

            paginated_url = f"{url}{self._page_notation}{page_idx}"  # change url to get a new page
            soup = self.get_soup(paginated_url, sleep=5)  # Delay time to make each request
            if not soup:
                print("[ERROR] soup object is None.")
                break
            
            # find target element in soup where the data of the products is represented
            target_element = soup.find(self._html_target, text=re.compile(self._element_target))
            if not target_element:
                print("[ERROR] Failure getting 'target_element' from 'soup'.")
                break

            print("[INFO] Success getting 'target_element' from 'soup'.")
            # cast soup element as string, and slice it accordingly, before loading it as a json string
            target_str = str(target_element.next)[len(self._element_target):]
            json_data = json.loads(target_str) 
            # use the '_json_targets' tuple to access the specific dict item, where the products data resides
            json_data = json_data.get(self._json_targets[0]).get(self._json_targets[1])

            ix = 0
            # iterate through the 'dict' 
            print("[INFO] Apending relevant product information to output array ...")
            for e in json_data:
                output_array.append(dict())
                # iterate thtough the _relavant_details'
                for d in self._relevant_details: 
                    output_array[ix][d] = e.get(d) # get all details for each product
                ix += 1
            
            page_idx += 1

        return output_array
