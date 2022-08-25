from replit import db
import os
from twitter import *
from time import sleep
from datetime import datetime
from src.engines.data_getter import download_image


### for automated account access
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
oauth_token = os.environ.get("oauth_token")
oauth_secret = os.environ.get("oauth_secret")



def checkTwitts(twitts):
    download_image(twitts[0][0])
    with open('src/img/image.png', "rb") as imagefile:
        img = imagefile.read()
    print('twitt T length:', len(twitts[0][1]))
    sendTwitt(img, twitts[0][1])
    print('twitt sent...', twitts[0][1])
    sleep(1)
    for t in twitts[1:]:
        download_image(t[0])
        with open('src/img/image.png', "rb") as imagefile:
            img = imagefile.read()
        print('twitt B length:', len(twitts[0][1]))
        sendTwitt(img, t[1])
        print('twitt sent...', t[1])
        sleep(1)
    print(f'\n...finished....{datetime.now()}..\n')
    
    
def sendTwitt(img, twitt):
    ### for bot account access
    twitter = Twitter(auth=OAuth(
        oauth_token, oauth_secret, CONSUMER_KEY, CONSUMER_SECRET))
    
    #twitter.statuses.update(status='api test3...')
    
    # for media using the old deprecated
    params = {"media[]": img, "status": twitt}
    # Or for an image encoded as base64:
    #params = {"media[]": img, "status": twitt, "_base64": True}
    
    twitter.statuses.update_with_media(**params)
    print('status updated')
    

   

async def twitterSendTwitt(dt):
   if db['twitter_twitt'] != []:
        try:
            checkTwitts(db['twitter_twitt'])
            db['twitter_twitt'] = []
            print('twitter init:', dt)
            print('finished:', datetime.now())
            return 'twitts sent'
        except Exception as e: 
            #if not 'twitter_errors' in db.keys():
            #    db['twitter_errors'] = [e]
            #else: 
            #    db['twitter_errors'].append([e])
            print('twitter start error:', e)

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
