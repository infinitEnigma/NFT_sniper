import sys
import asyncio
from keep_alive import keep_alive
#from replit import db
#from time import sleep
from datetime import datetime
import track_engine
import importlib
import nest_asyncio
nest_asyncio.apply()

keep_alive()
loop = asyncio.get_event_loop()    
while True:
    group1 = asyncio.gather(*[track_engine.trackChanges()])# for i in range(1)]) 
    print('check discord_client')
    if 'discord_client' not in sys.modules:
        import discord_client
        print('discord_client imported')
    else: 
        importlib.reload(discord_client)
        print('discord_client module reloaded')
    group2 = asyncio.gather(*[discord_client.init()])# for i in range(1)]) 
    all_groups = asyncio.gather(group1, group2)
    results = loop.run_until_complete(all_groups)
    print(f'cycle finished: {datetime.now()}\n')
    #if results: 
        #del sys.modules['discord_client']
        #importlib.reload(discord_client)
        #print('discord_client module deleted')