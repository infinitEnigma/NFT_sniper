import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
from replit import db

#import pandas as pd

def openGoogleSheet():
    # define the scope & credentials & authorize the clientsheet 
    scope_app =['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] 
    cred = ServiceAccountCredentials.from_json_keyfile_name('./venv/creds_app.json',scope_app) 
    client = gspread.authorize(cred)
    return client.open('NFT tracker')
    

def prepareCollFloors():
    if db['discord_embed'] != []:
            coll_floors = db['discord_embed'][0]
    coll_name = coll_floors[-1][0]
    nft_floors = [[l[0], l[1]] for l in coll_floors[-1][2:-1]]
    coll_total = coll_floors[-1][-1][0].split()[-1]
    return [coll_name, coll_total, nft_floors]
    

def updateCollFloorsSheet():
    coll_floors = prepareCollFloors()
    sheet = openGoogleSheet()
        
    sheet_instance = sheet.get_worksheet(db[f'worksheet_{coll_floors[0]}'])
    print(f'got {coll_floors[0]} collection')
    
    start_date = datetime.strptime('08.04.2022. 09:04:00', '%d.%m.%Y. %H:%M:%S')
    r = len(sheet_instance.get_all_values()) + 1
    now = datetime.strptime(datetime.now(), '%d.%m.%Y. %H:%M:%S')
    dt = timedelta(now, start_date)
    sheet_instance.update_cell(r, 1, now)
    sheet_instance.update_cell(r, 2, dt) 
    c = 3
    for nft in coll_floors[2]:
        sheet_instance.update_cell(r, c, nft[1])
        c += 1
    sheet_instance.update_cell(r, c, coll_floors[1])
    print('collection spreadsheet updated..')
       
   
async def initGoogleClient(ts):
    print('google init:', ts)
    updateCollFloorsSheet()
    print('google finished at:', datetime.now())