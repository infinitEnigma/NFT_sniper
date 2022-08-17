import sys
import asyncio
from keep_alive import keep_alive
from replit import db
#from time import sleep
from datetime import datetime
import track_engine
import twitter_client
import google_client
import importlib
import nest_asyncio
nest_asyncio.apply()

keep_alive()
loop = asyncio.get_event_loop()    
while True:
    group1 = asyncio.gather(*[track_engine.trackChanges()])# for i in range(1)]) #add init timestamp
    print('check twitter_client & google client')
    group2 = asyncio.gather(*[twitter_client.twitterSendTwitt(datetime.now()),
                             google_client.initGoogleClient(datetime.now())])
    
    print('check discord_client')
    if 'discord_client' not in sys.modules:
        import discord_client
        print('discord_client imported')
    else: 
        importlib.reload(discord_client)
        print('discord_client module reloaded')
    group3 = asyncio.gather(*[discord_client.init(datetime.now())])# for i in range(1)]) #add init timestamp
    all_groups = asyncio.gather(group1, group2, group3)
    results = loop.run_until_complete(all_groups)
    print(f'cycle finished: {datetime.now()}\n')
    if results: print(f'\nresults: {results}')
    elif db['discord_errors'] in db.keys():
        if db['discord_errors'][1] == 429:
            import subprocess
            subprocess.run(['kill 1'])