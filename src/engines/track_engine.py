from replit import db
from time import sleep
from datetime import datetime
from src.engines.data_getter import PageGetter
from src.engines.data_getter import open_chrome
from src.engines.pack_engine import prepare_messages


class CheckFloors:
    def __init__(self, driver):
        self.driver = driver
        self.raised = []
        self.lowered = []
        
    # extract prices and check for the changes
    def check_prices(self, coll_name, c):
        print(f'Collection: {coll_name}\n')
        nfts_nu = db['coll_urls'][c] 
        nfts_floors = db['coll_floors'][c]
        chgs = []
        #PG = PageGetter(self.driver)
        for a in nfts_nu[1].values():
            PG = PageGetter(self.driver)
            bt = PG.get_page(a + '&tab=items')
            if bt and bt != '':
                bt = bt.split('\n')
                for v in range(len(bt)-1):
                    if bt[v] in nfts_nu[0]:
                        nft = bt[v]
                        price = bt[v+1][1:]
                        if float(price) == nfts_floors[nft]:
                            print(f"{nft}: {(30-len(nft))*' '}{price} - no changes")
                        else:
                            change = float(price)-nfts_floors[nft]
                            if change > 0:
                                self.raised.append(f"{nft},{price},{change}")
                                print(f"{nft}: {(30-len(nft))*' '}{price} - floor raised: +{change}")
                            else:
                                self.lowered.append(f"{nft},{price},{change}")
                                print(f"{nft}: {(30-len(nft))*' '}{price} - floor lowered!!! {change}")
                            nfts_floors[nft] = float(price)
                            chgs.append((nft, price, round(change,2)))
                            db['adaprice'] = PG.get_coingecko()
                            db['quote'] = PG.get_quote()
                            PG = None
                        break
            else:
                print('CheckFloors: no body text')
                return [0]
        print("\nTOTAL:", sum(nfts_floors.values()), "\n")
        # if change is detected prepare reports
        if len(self.raised)+len(self.lowered)>0:
            # write last known values to db
            db[db['data'][coll_name][0]] = dict({it[0]: float(it[1]) for it in nfts_floors.items()})
            prepare_messages(coll_name, nfts_nu, nfts_floors, chgs)
        # get change sums
        if len(self.lowered)>0: db['sum_lowered'] = sum(float(s.split(',')[2]) for s in self.lowered)
        if len(self.raised)>0: db['sum_raised'] = sum(float(s.split(',')[2]) for s in self.raised)
        return [-db['sum_lowered']+db['sum_raised'], len(chgs)]


def loop_collections(driver):
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
            if db['saved_state'][0] == 1: 
                if coll[0] != db['saved_state'][1]:
                    print('not saved coll:', coll[0])
                    continue
            db['saved_state'] = [0, coll]
            # check floors
            check = CheckFloors(driver).check_prices(coll[0], c-1)
            #sleep(0.5)
            if check == 'False' or check == [0]:
                driver.quit()
                print("main2: no check_floors in while loop")
                sleep(3)
                return ''
            # if there's a change in price update changes tracker
            elif check[0] > 0:
                p = db['change_tracker'][coll[0]][0]+db['sum_lowered']
                n = db['change_tracker'][coll[0]][1]+db['sum_raised']
                db['change_tracker'][coll[0]] = [p, n, db['change_tracker'][coll[0]][2]+check[1]]
                print('pause while messages are sent...')
                db['saved_state'] = [1, coll[0]] 
                return 'send'
            print(f"changes since\nthe session start: lowered {db['change_tracker'][coll[0]][0]}, raised +{db['change_tracker'][coll[0]][1]}")
            print(f"\nchecks/changes: {db['gCounter']}/{db['change_tracker'][coll[0]][2]}\n")
        c = 0
        print(datetime.now(), 'pause...\n\n')
        sleep(10)


async def track_changes():
    if db['saved_state'][0] == 0:
        db['restarts'] = [db['restarts'][0]+1, str(datetime.now())]
    check = loop_collections(open_chrome()) 
    if check == 'send': return check
    else: await track_changes()