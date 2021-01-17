
from scrapers.base import *



class ProductScraper(Scraper):
    _element_target = '{"data":{"root":'   # string to create a reg expression and find in soup
    _element_target_end = '"module_core":' # string to find the end of the target
    _base = None                           # dict where the scrapped data will reside temporarily

    def set_base(self, base: dict) -> None:
        self._base = base

    def scrap_page(self, url: str) -> Dict:
        output_dict = {}

        soup = self.get_soup(url)
        if not soup:
            print("[ERROR] soup object is None.")
            return None

        # find target element in soup where the data of the products is represented
        target_element = soup.find(self._html_target, text=re.compile(self._element_target))
        if not target_element:
            print("[ERROR] Failure getting 'target_element' from 'soup'.")
            return None

        print("[INFO] Success getting 'target_element' from 'soup'.")
        target_str = str(target_element.next)               
        start_idx = target_str.find(self._element_target) + len(self._element_target) 
        end_idx = target_str.find(self._element_target_end)
        json_data = json.loads(target_str[start_idx:end_idx-1])  # slice and load json string

        base  = json_data.get("fields")     # get the item where the relevant data resides
        self.set_base(base)                 # set self._base, used for getter methods.
        
        # create the output dict by calling the methods for each item
        print("[INFO] Creating output dictionary with relevant information ...")
        output_dict = {
            "seller":           self._get_seller_dict(),
            "product":          self._get_product_dict(),
            "specifications":   self._get_specifications_dict(),
            "variations":       self._get_variations_dict(),
            "promotions":       self._get_promotions_dict(),
            "delivery":         self._get_delivery_dict(),
            "review":           self._get_reviews_dict(),
            "images":           self._get_images_dict()}

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
                for d in delivery.values() if d]  # list comprehension to create array of dicts
        }
        return delivery_dict

    def _get_promotions_dict(self) -> Dict:
        promotions = self._base.get("promotionTags").get("data")
        promotions_dict = {
            "vouchers": [
                {"name": p[0].get("name"),
                "description": p[0].get("description")
                }
                for p in promotions.values() if p] # list comprehension to create array of dicts
        }
        return promotions_dict

    def _get_product_dict(self) -> Dict:
        product = self._base.get("tracking")
        product_dict = {
            "name": product.get("pdt_name"),
            "image": f'https:{product.get("pdt_photo")}',
            "price": product.get("pdt_price"),
            "discount": product.get("pdt_discount"),
            "categories": product.get("pdt_category")}

        return product_dict

    def _get_variations_dict(self) -> Dict:
        variations = self._base.get("productOption").get("skuBase").get("properties")
        variations_dict = {}
        for i in variations:
            variations_dict[i.get("name")] = [
                {"name": v.get("name"),
                "image": v.get("image")
                } 
                for v in i.get("values") if v] # list comprehension to create array of dicts
        
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
                for r in review.get("reviews") if r] # list comprehension to create array of dicts
            }
        return review_dict

    def _get_images_dict(self) -> Dict:
        images = self._base.get("skuGalleries")
        images_dict = {}
        for n, i in enumerate(images.values()):
            # list comprehension to create array of img urls 
            images_dict[n] = [f'https:{v.get("src")}' for v in i if v]

        return images_dict

    def _get_specifications_dict(self) -> Dict:
        return self._base.get("specifications") # return full specifications item

        