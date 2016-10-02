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

    def tag_search(self, string, quantity=1):
        search_tag = '#{}'.format(string)
        tweet_list = self.api.search(q=search_tag, 
                                     count=quantity,
                                     lang='en')
        tweets = [x.text for x in tweet_list]
        return tweets

    def _filter_harsh(self, tweet, tag):
        """
        @brief     This will pull off hash tags just at the end of
                   tweet.  If your tag is not in the ending list
                   the tweet will not be returned
        
        @param      self   The object
        @param      tweet  The tweet
        @param      tag    The tag
        
        @return     the tweet, minus ending tags or False
        """
        if 'http' in tweet:
            return False
        else:
            tweet_list = tweet.split()
            tag_list = []
            for word in reversed(tweet_list):
                if word[0] == "#":
                    tag_list.append(word[1:])
                else:
                    break
            if tag not in tag_list:
                return False
        length = len(tweet_list) - len(tag_list)
        tagless_list = tweet_list[:length]

        return " ".join(tagless_list).replace("#", "") 


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

for tweet in bot.tag_search('sarcasm', 100):
    t = bot._filter_harsh(tweet, 'sarcasm')
    if t:
        print(bot.clean_tweet(t))

