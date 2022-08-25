from replit import db

def prepareMessages(coll_name, nfts_nu, nfts_floors, chgs):
    # prepare discord embeds & twitts
    imgs = db['data'][coll_name][4]
    imgs_d = db['thumbs_d'][coll_name]
    coll_sum = round(sum(nfts_floors.values()),2)
    coll_sumD = round(coll_sum * db['adaprice'],2)
    ic_url = [ic[1][3] for ic in db['data'].items() if ic[0]==coll_name]
    l = f'[Collection link - jpg.store]({db["data"][coll_name][1][:-12]})'
    d = l + "\n*collection latest changes:*\n" if len(chgs)>1 else l + '\n*collection latest change:*\n'
    dt = f"\nCollection Total:  ₳ {coll_sum} (${coll_sumD})\n{'for common plots & condo' if 'Land' in coll_name else ''}"
    embed, twitt, sheet = [], [], []
    embed.append([coll_name, d, 1127128, imgs_d[0]])
    twitt.append([ic_url[0], f'{coll_name}\nCollection link: {db["data"][coll_name][1][:-12]}{dt}'])
    for it in chgs:
        nft_priceD = round(float(it[1]) * db['adaprice'],2)
        t = f'{chgs.index(it)+1}. {it[0]}:\n... new floor: ₳ {it[1]} (${nft_priceD})'
        l = f'\n[NFT link - jpg.store]({nfts_nu[1][it[0]]})'
        d = 'change: ' + str('₳ '+ str(it[2]) + ' :arrow_lower_right:' if it[2]<0 else f"₳ +{it[2]} :arrow_upper_right:") + '\n' + l
        dollarP = 'usd price obtained via coingecko.com api'
        dt = f"{dollarP}\nchange: ₳ {it[2]} \u2198" if it[2]<0 else f"{dollarP}\nchange: ₳ +{it[2]} \u2197"
        for img in imgs:
            if it[0] == img[0]:
                twitt.append([img[1], f'{t}\n{dt}\nNFT link: {nfts_nu[1][it[0]]}'])
                sheet.append([coll_name, coll_sum,  db["data"][coll_name][1][:-12], 
                              ic_url[0], it[0], it[1], nfts_nu[1][it[0]], img[1]])
                break
        embed.append([t, d, 1157128 if it[2]<0 else 16711680, imgs_d[1][it[0]]])
    embed2 = [coll_name, "*collection current floors:*"]
    for item in nfts_floors.items():
        embed2.append([item[0], '₳ ' + str(item[1]), True])
    embed2.append([f'Collection Total: ₳ {round(sum(nfts_floors.values()),2)}', imgs_d[0]])
    embed.append(embed2)
    db['twitter_twitt'] = twitt
    db['google_sheet'] = sheet
    db['discord_embed'] = [embed, db['quote']]
    print('messages prepared...\n')