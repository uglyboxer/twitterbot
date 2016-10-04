from secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

import time
import random

from peewee import fn
import tweepy

from model import Tweet


class Bot:

    def __init__(self):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)

    def tweet(self, message):
        self.api.update_status(message)
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
                   Tweets with links are ignored, in case the tag
                   refers to the link and not the text

        @param      self   The object
        @param      tweet  The tweet
        @param      tag    The tag

        @return     the tweet, minus ending tags and the list of tags
                    or False
        """

        if 'http' in tweet:
            return False
        else:
            tweet_list = tweet.split()
            tag_list = []
            for word in reversed(tweet_list):
                if word[0] == "#":
                    tag_list.append(word[1:].lower())
                else:
                    break
            if tag not in tag_list:
                return False
        length = len(tweet_list) - len(tag_list)
        tagless_list = tweet_list[:length]

        tweet = " ".join(tagless_list).replace("#", "")
        Tweet.create_or_get(text=tweet)

        return {'text': tweet, 'tags': tag_list}

    def clean_tweet(self, tweet):
        """ Strip # character and @usernames out of tweet """
        filter_list = []
        tweet_list = tweet.split()
        for word in tweet_list:
            word = word.replace("#", "")
            if word[0] != '@' and 'http' not in word:
                filter_list.append(word)
        return " ".join(filter_list)

    def remove_hash_symbol(self, tweet):
        return tweet.replace("#", "")

    def remove_at_symbol(self, tweet):
        return tweet.replace("@", "")

    def remove_link(self, tweet):
        # TODO
        pass


if __name__ == '__main__':

    bot = Bot()

    while True:
        for tweet in bot.tag_search('sarcasm', 500):
            t = bot._filter_harsh(tweet, 'sarcasm')
            if t:
                print(bot.clean_tweet(t['text']))
        for tweet in bot.tag_search('sarcastic', 500):
            t = bot._filter_harsh(tweet, 'sarcastic')
            if t:
                print(bot.clean_tweet(t['text']))
        print(Tweet.select().count())
        msg = Tweet.select().order_by(fn.Random()).limit(1)
        for m in msg:
            print(m.text)
        suffix = random.choice([" ... Aces?",
                                " ... Well, I guess.",
                                " ... On Tuesdays?",
                                " ... So serious.",
                                " ... How do you really feel?",
                                " ... By the heavens!",
                                " ... Quick! To the batphone.",
                                " ... Well, I'm not so sure."])
        m = str(bot.clean_tweet(m.text) + suffix)
        # bot.tweet(m[:140])
        time.sleep(60 * 10 + random.randint(1, 80))
