from secrets import *

import tweepy, time, random

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)


class Bot:

    def __init__(self):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        self.api = tweepy.API(self.auth)

    def tweet(self, message):
        self.update_status(message)
        return True

    def tag_search(self, string):
        search_tag = '#{}'.format(string)
        tweet_list = self.api.search(q=search_tag, 
                                     count=10,
                                     lang='en')
        tweets = [x.text for x in tweet_list]
        return tweets

    def clean_tweet(self, tweet):
        filter_list = []
        tweet_list = tweet.split()
        for word in tweet_list:
            word = word.replace("#", "")
            if word[0] != '@' and 'http' not in word:
                filter_list.append(word)
        return " ".join(filter_list)

bot = Bot()
# while True:
    # message = get_message() # TODO Whatever generates the cool stuff
    # bot.tweet(message)
    # sleep_time = 900 + random.randint(1, 100)
    # time.sleep(sleep_time)

for tweet in bot.tag_search('sarcasm'):

    print(bot.clean_tweet(tweet))

for tweet in bot.tag_search('snark'):

    print(bot.clean_tweet(tweet))