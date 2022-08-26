import os
from twitter import *
from replit import db
from time import sleep
from datetime import datetime
from src.engines.data_getter import download_image


### for automated account access
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
oauth_token = os.environ.get("oauth_token")
oauth_secret = os.environ.get("oauth_secret")



def check_twitts(twitts):
    download_image(twitts[0][0])
    with open('src/img/image.png', "rb") as imagefile:
        img = imagefile.read()
    print('twitt T length:', len(twitts[0][1]))
    twitt = [[img, twitts[0][1]]]
    for t in twitts[1:]:
        download_image(t[0])
        with open('src/img/image.png', "rb") as imagefile:
            img = imagefile.read()
        print('twitt B length:', len(twitts[0][1]))
        twitt.append([img, t[1]])
    return twitt
    
    
def send_twitt(img, twitt, twitter):
    params = {"media[]": img, "status": twitt}
    #params = {"media[]": img, "status": twitt, "_base64": True}
    twitter.statuses.update_with_media(**params)
   
   
  
async def send_twitts(dt):
    print('twitter init:', dt)
    if db['twitter_twitt'] != []:
        try:
            twitt = check_twitts(db['twitter_twitt'])
            if twitt:
                twitter = Twitter(auth=OAuth(
                    oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))
                for t in twitt:
                    send_twitt(t[0], t[1], twitter)
                    print('twitt sent...', t[1])
                    sleep(1)
                db['twitter_twitt'] = []
                print('twitter finished:', datetime.now())
                return 'twitts sent'
            else: 
                print('no twitt from checkTwitt')
                return 'no twitts'
        except Exception as e: 
            print('twitter start error:', e)
            return 'twitter error'
    print('no twitts to send')
    return 'no twitts'
    
### for owner's account automated access
#ACCESS_KEY = os.environ.get("ACCESS_TOKEN")
#ACCESS_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
#t = Twitter(auth=OAuth(ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET))

# Get your "home" timeline
#print(t.statuses.home_timeline())
#MY_TWITTER_CREDS = os.path.expanduser('~/.my_app_credentials')
#if not os.path.exists(MY_TWITTER_CREDS):
#    oauth_dance("My App Name", CONSUMER_KEY, CONSUMER_SECRET,
#                MY_TWITTER_CREDS)

#oauth_token, oauth_secret = read_token_file(MY_TWITTER_CREDS)
#print(oauth_token, oauth_secret)
