import discord
#from discord.ext import commands
import os
#from replit import db
from keep_alive import keep_alive
import asyncio
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from nft_data import data, channel
import requests
import json

client = discord.Client()

class PriceGetter:
    def __init__(self, driver):
        self.driver = driver
     
    def getJpgStore(self, ch):
        try: self.driver.get(ch)
        except Exception as e:
            print("PriceGetter: something went wrong", e)
            return ''
        try:
            sleep(0.5)
            return self.driver.find_element(By.CSS_SELECTOR, 'body').text
        except Exception as e:
            print("PriceGetter: no ada_value", e)
            return ''

class CheckFloors:
    def __init__(self, driver):
        self.driver = driver
        self.raised = []
        self.lowered = []
        
  
    def checkPrices(self, coll_name, nfts_names, nfts_urls, nfts_floors):
        print(f'Collection: {coll_name}\n')
        global client
        global embed
        chgs = []
        embed = ''
        for a in nfts_urls.values():
            adavalue = PriceGetter(self.driver).getJpgStore(a) 
            if adavalue and adavalue != '':
                adavalue = adavalue.split('\n')
                for v in range(len(adavalue)-1):
                    if adavalue[v] in nfts_names:
                        if float(adavalue[v+1]) == nfts_floors[adavalue[v]]:
                            print(f"{adavalue[v]}: {(30-len(adavalue[v]))*' '}{adavalue[v+1]} - no changes")
                        else:
                            change = float(adavalue[v+1])-nfts_floors[adavalue[v]]
                            if float(adavalue[v+1]) > nfts_floors[adavalue[v]]:
                                self.raised.append(f"{adavalue[v]},{adavalue[v+1]},{change}")
                                print(f"{adavalue[v]}: {(30-len(adavalue[v]))*' '}{adavalue[v+1]} - floor raised: +{change}")
                                 
                            else:
                                self.lowered.append(f"{adavalue[v]},{adavalue[v+1]},{change}")
                                print(f"{adavalue[v]}: {(30-len(adavalue[v]))*' '}{adavalue[v+1]} - floor lowered!!! {change}")
                            nfts_floors[adavalue[v]] = float(adavalue[v+1])
                            chgs.append((adavalue[v], adavalue[v+1], round(change,2))) 
                        break
            else:
                print('CheckFloors: no adavalue')
                return [0]
        print("\nTOTAL:", sum(nfts_floors.values()),"\n")
        if len(self.raised)+len(self.lowered)>0:
            fname = data[coll_name][0]
            imgs = data[coll_name][4]
            # write last known values to file
            with open(fname, 'w') as f:
                f.write(''.join(f'{item[0]},{item[1]}\n' for item in nfts_floors.items()))
            # prepare discord message - embed 
            ic_url = [ic[1][3] for ic in data.items() if ic[0]==coll_name] 
            embed = []
            l = f'[Collection link - jpg.store]({data[coll_name][1][:-12]})'
            d = l + "\n*collection latest changes:*\n" if len(chgs)>1 else l + '\n*collection latest change:*\n'
            embed1 = discord.Embed(title=coll_name, description=d, color=1127128)
            embed1.set_thumbnail(url=ic_url[0])
            embed.append(embed1)
            for it in chgs: 
              t = f'{chgs.index(it)+1}. {it[0]}:\n... new floor ₳ {it[1]}'
              l = f'\n[NFT link - jpg.store]({nfts_urls[it[0]]})'
              d = 'change: ' + str('₳ '+ str(it[2]) if it[2]<0 else f"₳ +{it[2]}") + '\n' + l
              embed1 = discord.Embed(title=t, description=d, color=1157128 if it[2]<0 else 16711680)
              for img in imgs:
                if it[0] == img[0]: 
                    embed1.set_thumbnail(url=img[1])
                    break
              embed.append(embed1)
            embed2 = discord.Embed(title=coll_name, description="*collection current floors:*")
            for item in nfts_floors.items(): 
              embed2.add_field(name=item[0], value='₳ ' + item[1], inline=True) 
            embed2.set_footer(text=f'Collection Total: ₳ {sum(nfts_floors.values())}')
            embed2.set_thumbnail(url=ic_url[0])
            embed.append(embed2)
        # get change sums    
        sum_lowered = sum(float(s.split(',')[2]) for s in self.lowered)
        sum_raised = sum(float(s.split(',')[2]) for s in self.raised)
        return [nfts_floors, [sum_lowered, sum_raised]]

class CollectionNFT:
    def __init__(self, coll_floors, collurl, sufix):
        self.cf = coll_floors
        self.url = collurl
        self.sufx = sufix
    # prepare urls
    def createURLs(self):
        nft_urls = dict({name: url  for name,url in zip(self.cf.keys(),[f'{self.url}{s}' for s in self.sufx])})
        nft_names = list(nft_urls.keys())
        return [nft_names, nft_urls]

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    chnl = client.get_channel(channel[0])
    # open chrome driver
    try:
        driver = openChrome()
        sleep(1)
    except Exception as e:
        driver = None
        print("main: driver error:", e)
        sleep(3)
        #main()
        await client.close()
        return
    coll_urls, check_floors = [], {}
    global coll_floors
    global embed
    coll_floors = []
    for coll in data.items():
        with open(coll[1][0], 'r') as f:
            cf = [l.split(',') for l in f]
        coll_floors.append(dict({it[0]: float(it[1]) for it in cf}))
        coll_urls.append(CollectionNFT(coll_floors[-1], coll[1][1], coll[1][2]).createURLs())
        check_floors[coll[0]] = (CheckFloors(driver).checkPrices(coll[0], coll_urls[-1][0], coll_urls[-1][1], coll_floors[-1]))
        # if there's a change in price send discord messages 
        if len(check_floors[coll[0]])<=1:
            driver.quit()
            print("main: no check_floors")
            sleep(3)
            #main()
            await client.close()
            return
        if -check_floors[coll[0]][1][0]+check_floors[coll[0]][1][1] > 0:
            for e in embed:
              await chnl.send(embed=e)
              await asyncio.sleep(0.1)
            quote = get_quote()
            await chnl.send(f'||{quote}||')
            print('discord message sent..\n\n')
    driver.quit()
    sleep(34)
    change_tracker = dict({coll:[0,0,0] for coll in data.keys()})
    GCounter = 0
    c = 0
    while True:
        GCounter += 1
        driver = openChrome()
        sleep(3)
        for coll in data.items():
            check_floors[coll[0]] = CheckFloors(driver).checkPrices(coll[0], coll_urls[c][0], coll_urls[c][1], check_floors[coll[0]][0])
            if len(check_floors[coll[0]])<=1:
                driver.quit()
                print("main: no check_floors in while loop")
                sleep(3)
                #main()
                await client.close()
                return
            # if there's a change in price send discord messages
            if -check_floors[coll[0]][1][0]+check_floors[coll[0]][1][1] > 0:
                change_tracker[coll[0]] = [change_tracker[coll[0]][0]+check_floors[coll[0]][1][0], change_tracker[coll[0]][1]+check_floors[coll[0]][1][1], change_tracker[coll[0]][2]+1]
                for e in embed:
                    await chnl.send(embed=e)
                    await asyncio.sleep(0.1)
                quote = get_quote()
                await chnl.send(f'||{quote}||')
                print('discord message sent..\n\n')
            print(f'changes since\nthe session start: lowered {change_tracker[coll[0]][0]}, raised +{change_tracker[coll[0]][1]}')
            print(f'\nchanges/checks: {change_tracker[coll[0]][2]}/{GCounter}')
            c += 1
        c = 0
        print('pause...\n')
        driver.quit()
        sleep(34)
      
def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = f"*{json_data[0]['q']}* - {json_data[0]['a']}"
  return(quote)

def openChrome():   
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--disable-dev-shm-usage')
  chrome_options.add_argument('--headless')
  return webdriver.Chrome(options=chrome_options)

#coll_floors = []

def main():
  global client
  while True:
    client.run(os.getenv('TOKEN'))
    client = discord.Client()
    
if __name__ == "__main__":
  keep_alive()
  main()
  #client = None
    