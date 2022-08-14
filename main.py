import os
import asyncio
import discord
from keep_alive import keep_alive
from replit import db
from time import sleep
from datetime import datetime
#from discord.ext import commands
import track_engine
#import discord_client as d
#import test
import nest_asyncio
nest_asyncio.apply()
#keep_alive()
#client.run(os.getenv('TOKEN'))
#with open('db.txt','w') as f:
    #f.write(''.join(f"{it[0]}: {it[1]}\n" for it in db.items()))
#print(db.keys())
#print(db['channel'])
#import test
#from test import test1
loop = 0 
def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)

    return wrapped

@background
async def tasksToPerform(i): # Added another argument
    #print(i)
    if i == 0:
        print('tracking mode...',i)
        await track_engine.trackChanges()
        
    else:
        
        print('discord send messages...')
        #import discord_client as d
        await d
    print(f"function finished for {i}")


def test1(c):
    #loop.create_task(c)
    print('test started', c)
    c += 1
    print('test ended', c)
#tasks = [(test.test1,0),(d.init, d.client)]
#def main():
    #while True:
#import discord_client
loop = asyncio.get_event_loop()                                              # Have a new event loop
group1 = asyncio.gather(*[track_engine.trackChanges()])# for i in range(1)]) 
import discord_client as d
group2 = asyncio.gather(*[d])# for i in range(1)]) 
all_groups = asyncio.gather(group1, group2)
#looper = asyncio.gather(*[tasksToPerform(i) for i in [test1(111)]])         # Run the loop
#tasksToPerform(3)                               
#results = loop.run_until_complete(looper) 
results = loop.run_forever(all_groups) 