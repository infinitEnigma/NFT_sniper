import os
import asyncio
import discord
#from keep_alive import keep_alive
from replit import db
from time import sleep
from datetime import datetime
#from discord.ext import commands


    
client = discord.Client()

@client.event
async def on_ready():
    global client
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    print(db['channel'][0])
    chnl = client.get_channel(db['channel'][0])
    while True:
        sleep(1)
        if db['discord_embed'] != []:
            embeds = db['discord_embed'][0]
            quote  = db['discord_embed'][1]

            for e in embeds[:-1]:
                embed = discord.Embed(title=e[0], description=e[1], color=e[2])
                embed.set_thumbnail(url=e[3])
                #await asyncio.sleep(0.2)
                await chnl.send(embed=embed)
                print(f'..discord embed {embed.title} sent...')
            embed = discord.Embed(title=embeds[-1][0], description=embeds[-1][1])#, color=e[2])
            for l in embeds[-1][2:-1]:
                embed.add_field(name=l[0], value=l[1], inline=l[2])
            embed.set_thumbnail(url=embeds[-1][-1][-1])
            embed.set_footer(text=embeds[-1][-1][0])
            #await asyncio.sleep(0.2)
            await chnl.send(embed=embed)
            print(f'..discord embed {embed.title} sent...')
            if quote !='':
                #await asyncio.sleep(0.2)
                await chnl.send(f'||{quote}||')
                print('..discord quote sent...\n')
            db['discord_embed'] = []
            print(f'finished....{datetime.now()}....\n')
            break
            
    try: 
        await client.close()
        print('loop closed')   
    except: print('loop killed')


async def init():
    print('init')

try: asyncio.run(client.start(os.getenv('TOKEN')))
except: print('client start error')

 
