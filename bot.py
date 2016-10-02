from secrets import *

import tweepy, time, random

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

while True:
    api.update_status('Howdy' + str(random.randrange(100)))
    time.sleep(120)