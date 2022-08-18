
#import os
import json
#import asyncio
#import discord
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
#from keep_alive import keep_alive
from datetime import datetime
from time import sleep
from replit import db
from src.engines.pack_engine import prepareMessages


class PageGetter:
    def __init__(self, driver):
        self.driver = driver
    # get text from the page body 
    def getPage(self, ch):
        try: self.driver.get(ch)
        except Exception as e:
            print("PriceGetter: something went wrong", e)
            return ''
        try:
            sleep(0.3)
            bt = self.driver.find_element(By.CSS_SELECTOR, 'body').text
        except Exception as e:
            print("PriceGetter: no text in the body", e)
            return ''
        try: 
            self.driver.get('chrome://settings/clearBrowserData')
        except: print("couldn't clear browser cash")
        return bt


class CheckFloors:
    def __init__(self, driver):
        self.driver = driver
        self.raised = []
        self.lowered = []
    # extract prices and check for the changes
    def checkPrices(self, coll_name, c):
        print(f'Collection: {coll_name}\n')
        nfts_nu = db['coll_urls'][c] 
        nfts_floors = db['coll_floors'][c]
        chgs = []
        for a in nfts_nu[1].values():
            bt = PageGetter(self.driver).getPage(a)
            if bt and bt != '':
                bt = bt.split('\n')
                for v in range(len(bt)-1):
                    if bt[v] in nfts_nu[0]:
                        if float(bt[v+1]) == nfts_floors[bt[v]]:
                            print(f"{bt[v]}: {(30-len(bt[v]))*' '}{bt[v+1]} - no changes")
                        else:
                            change = float(bt[v+1])-nfts_floors[bt[v]]
                            if change > 0:
                                self.raised.append(f"{bt[v]},{bt[v+1]},{change}")
                                print(f"{bt[v]}: {(30-len(bt[v]))*' '}{bt[v+1]} - floor raised: +{change}")

                            else:
                                self.lowered.append(f"{bt[v]},{bt[v+1]},{change}")
                                print(f"{bt[v]}: {(30-len(bt[v]))*' '}{bt[v+1]} - floor lowered!!! {change}")
                            nfts_floors[bt[v]] = float(bt[v+1])
                            chgs.append((bt[v], bt[v+1], round(change,2)))
                            db['adaprice'] = get_coingecko(self.driver)
                            db['quote'] = get_quote(self.driver)
                        break
            else:
                print('CheckFloors: no body text')
                return [0]
        print("\nTOTAL:", sum(nfts_floors.values()), "\n")
        # if change is detected prepare reports
        if len(self.raised)+len(self.lowered)>0:
            # write last known values to db
            db[db['data'][coll_name][0]] = dict({it[0]: float(it[1]) for it in nfts_floors.items()})
            prepareMessages(coll_name, nfts_nu, nfts_floors, chgs)
        # get change sums
        if len(self.lowered)>0: db['sum_lowered'] = sum(float(s.split(',')[2]) for s in self.lowered)
        if len(self.raised)>0: db['sum_raised'] = sum(float(s.split(',')[2]) for s in self.raised)
        return [-db['sum_lowered']+db['sum_raised'], len(chgs)]


def get_coingecko(driver):
    cg = "https://api.coingecko.com/api/v3/simple/price?ids=cardano&vs_currencies=usd"
    response = PageGetter(driver).getPage(cg)
    json_data = json.loads(response)
    return float(json_data['cardano']['usd'])

def get_quote(driver):
    response = PageGetter(driver).getPage("https://zenquotes.io/api/random")
    json_data = json.loads(response)
    return f"*{json_data[0]['q']}* - {json_data[0]['a']}"
        
def openChrome():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--verbose")
    return webdriver.Chrome(options=chrome_options)


def loopCollections(driver):
    #driver = openChrome()
    if db['saved_state'][0] == 0:
        db['change_tracker'] = dict({coll:[0,0,0] for coll in db['data'].keys()})
        db['gCounter'] = 0
    c = 0
    # loop through the collections and check floors
    while True:
        db['sum_lowered'] = 0
        db['sum_raised'] = 0
        db['gCounter'] += 1
        check = 'False'
        print('restarts:', db['restarts'])
        for coll in db['data'].items():
            c += 1
            if db['saved_state'][0] == 1: #in db.keys():
                if coll[0] != db['saved_state'][1]:
                    print('not saved coll:', coll[0])
                    continue
            db['saved_state'] = [0, coll]
            # check floors
            check = CheckFloors(driver).checkPrices(coll[0], c-1)
            sleep(0.5)
            if check == 'False' or check == [0]:
                driver.quit()
                print("main2: no check_floors in while loop")
                sleep(3)
                return
            # if there's a change in price update changes tracker
            elif check[0] > 0:
                p = db['change_tracker'][coll[0]][0]+db['sum_lowered']
                n = db['change_tracker'][coll[0]][1]+db['sum_raised']
                db['change_tracker'][coll[0]] = [p, n, db['change_tracker'][coll[0]][2]+check[1]]
                print('pause while messages are sent...')
                db['saved_state'] = [1, coll[0]] 
                return 'send'
            print(f"changes since\nthe session start: lowered {db['change_tracker'][coll[0]][0]}, raised +{db['change_tracker'][coll[0]][1]}")
            print(f"\nchanges/checks: {db['change_tracker'][coll[0]][2]}/{db['gCounter']}\n")
        c = 0
        print(datetime.now(), 'pause...\n\n')
        sleep(5)



#keep_alive()
async def trackChanges():
    if db['saved_state'][0] == 0:
        db['restarts'] = [db['restarts'][0]+1, str(datetime.now())]
    check = loopCollections(openChrome()) 
    if check == 'send': return check
    else: trackChanges()