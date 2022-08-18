import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from replit import db
import os
import json
#import pandas as pd

def openGoogleSheet():
    # define the scope & credentials & authorize the clientsheet 
    scope_app =['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = {'type': os.environ.get("type"),
              "project_id": os.environ.get("project_id"),
              "private_key_id": os.environ.get("private_key_id"),
              "private_key": os.environ.get("private_key"),
              "client_email": os.environ.get("client_email"),
              "client_id": os.environ.get("client_id"),
              "auth_uri": os.environ.get("auth_uri"),
              "token_uri": os.environ.get("token_uri"),
              "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
              "client_x509_cert_url": os.environ.get("client_x509_cert_url")}
    with open('./src/creds.json', 'w') as f:
        json.dump(creds, f)
    #cred = ServiceAccountCredentials.from_json_keyfile_name(creds, scope_app)
    cred = ServiceAccountCredentials.from_json_keyfile_name('./src/creds.json', scope_app) 
    client = gspread.authorize(cred)
    with open('./src/creds.json', 'w') as f:
        json.dump({'creds': 'creds'}, f)
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
    frmt = '%m-%d-%Y %H:%M:%S'
    start_date = datetime.strptime('08-04-2022 09:04:00', frmt)
    now = datetime.strptime(datetime.now().strftime(frmt), frmt)
    dt = float((now - start_date).total_seconds()/86400)
    r = len(sheet_instance.get_all_values()) + 1
    sheet_instance.update_cell(r, 1, str(now))
    sheet_instance.update_cell(r, 2, dt) 
    c = 3
    for nft in coll_floors[2]:
        sheet_instance.update_cell(r, c, float(nft[1].split()[1]))
        c += 1
    sheet_instance.update_cell(r, c, float(coll_floors[1]))
    print('collection spreadsheet updated..')
       
   
async def googleUpdateSheet(ts):
    print('google init:', ts)
    try: updateCollFloorsSheet()
    except Exception as e:
        print('google init error:', e)
    print('google finished at:', datetime.now())
    return 'sheet updated'