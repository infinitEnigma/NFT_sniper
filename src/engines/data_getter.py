import json
import io, os
import requests
import tempfile
from PIL import Image
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options



class PageGetter:
    def __init__(self, driver):
        self.driver = driver
    
    # get text from the page body 
    def get_page(self, ch):
        try: 
            self.driver.get(ch)
        except Exception as e:
            print("PageGetter: something went wrong", e)
            return ''
        if 'jpg.store' in ch: 
            b = self.get_jpgstore()
            try:
                bt = b.text
            except: 
                print('PageGetter: no data from jpg.store')
                return ''
        else:
            try:
                bt = self.driver.find_element(By.CSS_SELECTOR, 'body').text
            except Exception as e:
                print("PageGetter: no text in the body", e)
                return ''    
        try: 
            self.driver.get('chrome://settings/clearBrowserData')
        except: print("couldn't clear browser cash")
        return bt

    def get_jpgstore(self):
        try:
            # slow loding of the marketplace section - sleep(4) seems fine 
            sleep(4)
            b = self.driver.find_element(By.CSS_SELECTOR, 'body')
            bt = b.find_element(By.ID, 'marketplace')
            return bt
        except:
            print('get_jpgstore: no data from marketplace')
            return ''
       
    def get_coingecko(self):
        cg = "https://api.coingecko.com/api/v3/simple/price?ids=cardano&vs_currencies=usd"
        response = self.get_page(cg)
        json_data = json.loads(response)
        return float(json_data['cardano']['usd'])
    
    def get_quote(self):
        response = self.get_page("https://zenquotes.io/api/random")
        json_data = json.loads(response)
        return f"*{json_data[0]['q']}* - {json_data[0]['a']}"


def open_chrome():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--verbose")
    return webdriver.Chrome(options=chrome_options)


def download_image(img_url):
    buffer = tempfile.SpooledTemporaryFile(max_size=1e9)
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        downloaded = 0
        #filesize = int(r.headers['content-length'])
        for chunk in r.iter_content(chunk_size=1024):
            downloaded += len(chunk)
            buffer.write(chunk)
            #print(downloaded/filesize)
        buffer.seek(0)
        i = Image.open(io.BytesIO(buffer.read()))
        i.save(os.path.join('src/img/image.png'))#, quality=85)
        print('..image downloaded...')
    buffer.close()