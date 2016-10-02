from secrets import *

import tweepy, time, random

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

while True:
    message = get_message() # TODO Whatever generates the cool stuff
    api.update_status(message)
    sleep_time = 900 + random.randint(1, 100)
    time.sleep(sleep_time)