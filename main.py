import sys
import asyncio
from src.engines.keep_alive import keep_alive
from replit import db
#from time import sleep
from datetime import datetime
from src.engines import track_engine
from src.clients import twitter_client
from src.clients import google_client
import importlib
import nest_asyncio
nest_asyncio.apply()

def killMain():
    try:
        import subprocess
        subprocess.run(['kill', '1'])
    except Exception as e: print("\nsuicide didn't work\n", e)

keep_alive()
loop = asyncio.get_event_loop() 
while True:
    print('check engines')
    group1 = asyncio.gather(*[track_engine.trackChanges()])# for i in range(1)]) #add init timestamp
    print('check twitter & google client')
    group2 = asyncio.gather(*[twitter_client.twitterSendTwitt(datetime.now()),
                             google_client.googleUpdateSheet(datetime.now())])
    
    print('check discord client')
    if 'src.clients.discord_client' not in sys.modules:
        import src.clients.discord_client
        print('discord_client imported')
    else: 
        importlib.reload(src.clients.discord_client)
        print('discord_client module reloaded')
    group3 = asyncio.gather(*[src.clients.discord_client.init(datetime.now())])
    all_groups = asyncio.gather(group1, group2, group3)
    results = loop.run_until_complete(all_groups)
    print(f'cycle finished: {datetime.now()}\n')
    #kill = 0
    if results: 
        print(f'\nresults: {results}')
        if db['discord_errors'][1] == 429 or results[1] == [[],[]] or results[2] == []:
            print('error!!!...killing main process..')
            db['discord_errors'][1] = 0
            killMain()
    else: killMain()

