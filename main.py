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
    db['discord_errors'][1] = 0
    db['saved_state'][0] = 0
    try:
        import subprocess
        subprocess.run(['kill', '1'])
    except Exception as e: 
        print("\nsuicide didn't work\n", e)
        db['saved_state'][0] = 1

keep_alive()
loop = asyncio.get_event_loop() 
while True:
    group1 = None
    if db['discord_embed'] == [] and db['twitter_twitt'] == []:
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
    if group1:
        all_groups = asyncio.gather(group1, group2, group3)
    else: 
        all_groups = asyncio.gather(group2, group3)
    results = loop.run_until_complete(all_groups)
    print(f'loop completed: {datetime.now()}')
    
    if results:
        print(f'results: {results}')
        if db['discord_errors'][1] != 0:
                    print('\ndiscord error!!!...killing main process..\n')
                    killMain()
        if len(results)==3:
            if [None] in results[1] or results[0] == [None]:
                print('\nresults_3 error!!!...killing main process..\n')
                killMain()
        else:
            if [None] in results[0]:
                print('\nresults_2 error!!!...killing main process..\n')
                killMain()
    else: 
        print('\nno results!!!...killing main process..\n')
        killMain()
    print('results ok... next loop...\n')
