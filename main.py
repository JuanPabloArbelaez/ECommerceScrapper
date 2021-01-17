
import os
import argparse

from scrapers.category import CategoryScraper
from scrapers.product import ProductScraper 



# Command Line Arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--scrap", default="product", help="scrap category or product")
ap.add_argument("-u", "--url", required=False, help="url of Lazada category or product page")
ap.add_argument("-f", "--format", default="json", help="format of output file. [csv / json]")
ap.add_argument("-o", "--output", default="output", help="location of output directory")
args = vars(ap.parse_args())


def filename_from_url(url: str) -> str:
    return url.strip("https://www.").replace('/','_')[:50]  


if __name__ == "__main__":
    url = args.get("url")
    file_format = args.get("format")
    
    output_dir = f'{os.getcwd()}/{args.get("output")}'
    if not os.path.exists(output_dir):
        print(f"[INFO] creating {output_dir} directory.")
        os.makedirs(output_dir)

    scrap = args.get("scrap")
    if scrap == "category":
        if not url:
            # Example url if -u not proviced in cmd option
            url = "https://www.lazada.sg/bikes/" 
        
        filename = filename_from_url(url)  
        print(f"[INFO] Creating Scraper for: *{scrap}* in {url}")
        cs = CategoryScraper(output_dir, file_format)
        cs.scrap_and_save(filename, url)

    elif scrap == "product":
        file_format = 'json' # should always be json, as csv is not suitable for the product         

        if not url:
            # Example url if -u not proviced in cmd option
            url = "https://www.lazada.sg/products/arduino-starter-kit-official-english-i476386619-s1297160688.html"
        
        filename = filename_from_url(url)  
        print(f"[INFO] Creating Scraper for: *{scrap}* in {url}")
        ps = ProductScraper(output_dir, file_format)
        ps.scrap_and_save(filename, url)
    
    else:
        print(f"[ERROR] invalid scap operation: {args.get('scrap')}")
