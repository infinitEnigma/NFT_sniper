import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from replit import db
import os


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
    cred = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope_app)
    client = gspread.authorize(cred)
    return client.open('NFT tracker')
   

def updateCollFloorsSheet():
    frmt = '%Y-%m-%d %H:%M:%S'
    start_date = datetime.strptime('2022-08-23 14:57:06', frmt)
    now = datetime.strptime(datetime.now().strftime(frmt), frmt)
    dt = float((now - start_date).total_seconds()/86400)

    sheet = openGoogleSheet()
    sheet_instance = sheet.get_worksheet(5)
    r = len(sheet_instance.get_all_values()) + 1
    pf = [str(now), round(dt, 3)]
    ch = []
    for change in db['google_sheet']:
        ch.append(dict({'range': f'A{r}:J{r}', 'values': [[*pf, *change]]}))
        r += 1
    sheet_instance.batch_update(ch)
    db['google_sheet'] = []
    print('google spreadsheet updated..')  
    
   
async def googleUpdateSheet(ts):
    print('google init:', ts)
    try: updateCollFloorsSheet()
    except Exception as e:
        print('google init error:', e)
    print('google finished at:', datetime.now())
    return 'sheet updated'