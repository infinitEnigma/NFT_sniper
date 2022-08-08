import discord
from discord.ext import commands
import os
#import random
#from replit import db
from keep_alive import keep_alive
#from datetime import datetime, timedelta
#import sys
#import json
#import undetected_chromedriver as uc
import asyncio
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from nft_data import data, channel

client = discord.Client()
#client.run(os.getenv('TOKEN'))
#print('limited:', client.is_ws_ratelimited())
class PriceGetter:
    def __init__(self, driver):
        self.driver = driver

    def getJpgStore(self, ch):
        try: self.driver.get(ch)
        except Exception as e:
            print("PriceGetter: something went wrong", e)
            return ''
        try:
            sleep(2.5)
            ada_value = self.driver.find_element(By.CSS_SELECTOR, 'body').text 
            return ada_value
        except Exception as e:
            print("PriceGetter: no ada_value", e)
            return ''

class CheckFloors:
    def __init__(self, driver):
        self.driver = driver
        self.raised = []
        self.lowered = []
        #self.client = client
    
    def checkPrices(self, coll_name, nfts_names, nfts_urls, nfts_floors):
        print(f'Collection: {coll_name}\n')
        global client
        #global msg
        chgs = []
        msg = ''
        for a in nfts_urls.values():
            adavalue = PriceGetter(self.driver).getJpgStore(a)  #.split('\n')
            if adavalue and adavalue != '':
                adavalue = adavalue.split('\n')
                for v in range(len(adavalue)-1):
                    if adavalue[v] in nfts_names:
                        if float(adavalue[v+1]) == nfts_floors[adavalue[v]]:
                            print(f"{adavalue[v]}: {(30-len(adavalue[v]))*' '}{adavalue[v+1]} - no changes")
                        else:
                            #frequency, duration  = 2500, 500  # Set Frequency To 2500 Hertz
                            change = float(adavalue[v+1])-nfts_floors[adavalue[v]]
                            if float(adavalue[v+1]) > nfts_floors[adavalue[v]]:
                                self.raised.append(f"{adavalue[v]},{adavalue[v+1]},{change}")
                                print(f"{adavalue[v]}: {(30-len(adavalue[v]))*' '}{adavalue[v+1]} - floor raised: +{change}")
                                 
                            else:
                                self.lowered.append(f"{adavalue[v]},{adavalue[v+1]},{change}")
                                print(f"{adavalue[v]}: {(30-len(adavalue[v]))*' '}{adavalue[v+1]} - floor lowered!!! {change}")
                            nfts_floors[adavalue[v]] = float(adavalue[v+1])
                            
                            chgs.append(''.join(f"{adavalue[v]}: {adavalue[v+1]}  ...  change: {'+' if change>0 else ''}{change}\n"))
                              
                        break
            else:
                print('CheckFloors: no adavalue')
                return [0]
        print("\nTOTAL:", sum(nfts_floors.values()),"\n")
        if len(self.raised)+len(self.lowered)>0:
            if coll_name == 'Cardano Summit 2021': fname = 'summit_floors.txt'
            elif 'Land' in coll_name: fname = 'vland_floors.txt'
            elif 'vFlects' in coll_name: fname = 'vflects_floors.txt'
            elif 'Vehicles' in coll_name: fname = 'vehicles_floors.txt'
            elif 'Bees' in coll_name: fname = 'bees_floors.txt'
            # write last known values to file
            with open(fname, 'w') as f:
                f.write(''.join(f'{item[0]},{item[1]}\n' for item in nfts_floors.items()))
            msg = coll_name + ' latest changes:\n' + ''.join(f'{it}' for it in chgs) + '\nCollection floors:\n' + ''.join(f"{item[0]}:{(30-len(item[0]))*chr(32)}{item[1]}\n" for item in nfts_floors.items()) + '\nTOTAL: ' + str(sum(nfts_floors.values())) + '\n_______' + '\n'  
            #if not client.is_closed(): client.connect()
            #print('limited:', client.is_ws_ratelimited())
                        
            @client.event
            async def on_ready():
                print('Logged in as')
                print(client.user.name)
                print(client.user.id)
                print('------')
                chnl = client.get_channel(channel[0])
                
                #await client.wait_until_ready()
                await chnl.send(msg)
                await asyncio.sleep(2)
                await client.close()
                print('msg sent')
            
            try: 
              client.run(os.getenv('TOKEN'))
              sleep(1)
              #client = None
            except Exception as e:
              print('client run error', e)
              #if send_msg(channel, msg) == 1: print('sent')
            #client = None
            if not client.is_closed(): 
              print('limited:', client.is_ws_ratelimited())
              print('closed:', client.is_closed())
            else: print('client closed')
        sum_lowered = sum(float(s.split(',')[2]) for s in self.lowered)
        sum_raised = sum(float(s.split(',')[2]) for s in self.raised)
        return [nfts_floors, [sum_lowered, sum_raised]]

class CollectionNFT:
    def __init__(self, coll_floors, collurl, sufix):
        self.cf = coll_floors
        self.url = collurl
        self.sufx = sufix

    def createURLs(self):
        nft_urls = dict({name: url  for name,url in zip(self.cf.keys(),[f'{self.url}{s}' for s in self.sufx])})
        nft_names = list(nft_urls.keys())
        return [nft_names, nft_urls]

def openChrome():   
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument('--headless')
  return webdriver.Chrome(options=chrome_options)

coll_floors = []



#msg = ''
#client.run(os.getenv('TOKEN'))
#client.run('token')

def main():
    try:
        driver = openChrome()
        sleep(1)
    except Exception as e:
        driver = None
        print("main: driver error:", e)
        sleep(5)
        main()
    #global client
    # read last known values from files and create dictionary
    #if client.is_closed: 
    #  client = discord.Client()
    coll_urls, check_floors = [], {}
    global coll_floors
    #global client
    coll_floors = []
    for coll in data.items():
        with open(coll[1][0], 'r') as f:
            cf = [l.split(',') for l in f]
        coll_floors.append(dict({it[0]: float(it[1]) for it in cf}))
        coll_urls.append(CollectionNFT(coll_floors[-1], coll[1][1], coll[1][2]).createURLs())
        check_floors[coll[0]] = (CheckFloors(driver).checkPrices(coll[0], coll_urls[-1][0], coll_urls[-1][1], coll_floors[-1]))
        #if len(msg)>0: client.run(os.getenv('TOKEN'))
        if len(check_floors[coll[0]])<=1:
            driver.quit()
            main()
    driver.quit()
    sleep(34)
    #floors = coll_floors
    change_tracker = dict({coll:[0,0,0] for coll in data.keys()})
    GCounter = 0
    c = 0
    while True:
        GCounter += 1
        driver = openChrome()
        sleep(3)
        #if client.is_closed:
        #if client == None:
          #client = discord.Client()
        for coll in data.items():
            check_floors[coll[0]] = CheckFloors(driver).checkPrices(coll[0], coll_urls[c][0], coll_urls[c][1], check_floors[coll[0]][0])
            #if len(msg)>0: client.run(os.getenv('TOKEN'))
            if len(check_floors[coll[0]])<=1:
                driver.quit()
                main()
            if -check_floors[coll[0]][1][0]+check_floors[coll[0]][1][1] > 0:
                change_tracker[coll[0]] = [change_tracker[coll[0]][0]+check_floors[coll[0]][1][0], change_tracker[coll[0]][1]+check_floors[coll[0]][1][1], change_tracker[coll[0]][2]+1]
                
            print(f'changes since\nthe session start: lowered {change_tracker[coll[0]][0]}, raised +{change_tracker[coll[0]][1]}')
            print(f'\nchanges/checks: {change_tracker[coll[0]][2]}/{GCounter}')
            c += 1
        c = 0
        print('pause...\n')
        driver.quit()
        sleep(34)
      

if __name__ == "__main__":
  #keep_alive()
  #client.run(os.getenv('TOKEN'))
  main()
  keep_alive()
  #driver.quit()
    