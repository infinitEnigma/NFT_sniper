import os
import json
import asyncio
import discord
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from keep_alive import keep_alive
from datetime import datetime
from time import sleep
from replit import db
#from discord.ext import commands

client = discord.Client()

def openChrome():
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--headless')
    chrome_options.add_argument("--verbose")
    return webdriver.Chrome(options=chrome_options)


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
    def checkPrices(self, coll_name, nfts_nu, nfts_floors):
        print(f'Collection: {coll_name}\n')
        chgs = []
        quote = ''
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
                            if float(bt[v+1]) > nfts_floors[bt[v]]:
                                self.raised.append(f"{bt[v]},{bt[v+1]},{change}")
                                print(f"{bt[v]}: {(30-len(bt[v]))*' '}{bt[v+1]} - floor raised: +{change}")

                            else:
                                self.lowered.append(f"{bt[v]},{bt[v+1]},{change}")
                                print(f"{bt[v]}: {(30-len(bt[v]))*' '}{bt[v+1]} - floor lowered!!! {change}")
                            nfts_floors[bt[v]] = float(bt[v+1])
                            chgs.append((bt[v], bt[v+1], round(change,2)))
                            quote = get_quote(self.driver)
                        break
            else:
                print('CheckFloors: no body text')
                return [0]
        print("\nTOTAL:", sum(nfts_floors.values()),"\n")
        embed = []
        # if change is detected prepare reports
        if len(self.raised)+len(self.lowered)>0:
            imgs = db['data'][coll_name][4]
            # write last known values to db
            db[db['data'][coll_name][0]] = dict({it[0]: float(it[1]) for it in nfts_floors.items()})
            # prepare discord message - embed
            ic_url = [ic[1][3] for ic in db['data'].items() if ic[0]==coll_name]
            l = f'[Collection link - jpg.store]({db["data"][coll_name][1][:-12]})'
            d = l + "\n*collection latest changes:*\n" if len(chgs)>1 else l + '\n*collection latest change:*\n'
            dt = f"\nCollection Total:  ₳ {sum(nfts_floors.values())} {'for common plots & condo' if 'Land' in coll_name else ''}"
            embed, twitt = [], []
            embed1 = discord.Embed(title=coll_name, description=d, color=1127128)
            embed1.set_thumbnail(url=ic_url[0])
            embed.append(embed1)
            twitt.append([ic_url[0], f'{coll_name}\nCollection link: {db["data"][coll_name][1][:-12]}{dt}'])
            for it in chgs:
                t = f'{chgs.index(it)+1}. {it[0]}:\n... new floor: ₳ {it[1]}'
                l = f'\n[NFT link - jpg.store]({nfts_nu[1][it[0]]})'
                d = 'change: ' + str('₳ '+ str(it[2]) if it[2]<0 else f"₳ +{it[2]}") + '\n' + l
                dt = '\nchange: ' + str('₳ '+ str(it[2]) if it[2]<0 else f"₳ +{it[2]}")
                embed1 = discord.Embed(title=t, description=d, color=1157128 if it[2]<0 else 16711680)
                for img in imgs:
                    if it[0] == img[0]:
                        embed1.set_thumbnail(url=img[1])
                        twitt.append([img[1], f'{t}\n{dt}\nNFT link: {nfts_nu[1][it[0]]}'])
                        break
                embed.append(embed1)
            embed2 = discord.Embed(title=coll_name, description="*collection current floors:*")
            for item in nfts_floors.items():
                embed2.add_field(name=item[0], value='₳ ' + str(item[1]), inline=True)
            embed2.set_footer(text=f'Collection Total: ₳ {sum(nfts_floors.values())}')
            embed2.set_thumbnail(url=ic_url[0])
            embed.append(embed2)
            db['twitter'] = twitt
            print()
        # get change sums
        db['sum_lowered'] = sum(float(s.split(',')[2]) for s in self.lowered)
        db['sum_raised'] = sum(float(s.split(',')[2]) for s in self.raised)
        return [-db['sum_lowered']+db['sum_raised'], [embed, quote]]


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    chnl = client.get_channel(db['channel'][0])
    db['restarts'] = [db['restarts'][0]+1, str(datetime.now())]
    # open chrome driver
    try:
        driver = openChrome()
        sleep(5)
    except Exception as e:
        print("main1: driver error:", e)
        sleep(1)
        return
    #check_floors = {}  
    change_tracker = dict({coll:[0,0,0] for coll in db['data'].keys()})
    GCounter = 0
    c = 0
    # loop through the collections and check floors
    while True:
        GCounter += 1
        check = 'False'
        print('restarts:', db['restarts'])
        for coll in db['data'].items():
            # check floors
            check = CheckFloors(driver).checkPrices(coll[0], db['coll_urls'][c], db['coll_floors'][c])
            sleep(0.5)
            if check == 'False' or check == [0]:
                driver.quit()
                print("main2: no check_floors in while loop")
                sleep(3)
                return
            # if there's a change in price 
            # update changes tracker and send discord messages
            elif check[0] > 0:
                p = change_tracker[coll[0]][0]+db['sum_lowered']
                n = change_tracker[coll[0]][1]+db['sum_raised']
                change_tracker[coll[0]] = [p, n, change_tracker[coll[0]][2]+1]
                await sendDiscordMsgs(check[1][0], check[1][1], chnl)
            # print changes    
            print(f'changes since\nthe session start: lowered {change_tracker[coll[0]][0]}, raised +{change_tracker[coll[0]][1]}')
            print(f'\nchanges/checks: {change_tracker[coll[0]][2]}/{GCounter}\n')
            c += 1
        c = 0
        print(datetime.now(), 'pause...\n\n')
        sleep(10)


def get_quote(driver):
    response = PageGetter(driver).getPage("https://zenquotes.io/api/random")
    json_data = json.loads(response)
    return f"*{json_data[0]['q']}* - {json_data[0]['a']}"


async def sendDiscordMsgs(embeds, quote, chnl):
    for e in embeds:
        await asyncio.sleep(0.2)
        await chnl.send(embed=e)
        print(f'..discord embed {e.title} sent...')
    if quote !='': 
        await asyncio.sleep(0.2)
        await chnl.send(f'||{quote}||')
        print('..discord quote sent...\n')
 

keep_alive()
client.run(os.getenv('TOKEN'))
