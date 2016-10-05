from secrets import *
from model import Tweet

from peewee import fn

import tweepy, time, random

class Bot:

    def __init__(self):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
        self.api = tweepy.API(self.auth)

    def tweet(self, message):
        self.api.update_status(message)
        return True

    def tag_search(self, string, pages=1, since_id=1):
        tweets = []
        search_tag = '#{}'.format(string)
        # tweet_list = self.api.search(q=search_tag, 
        #                              count=quantity,
        #                              lang='en')
        tweet_list = tweepy.Cursor(self.api.search, q=search_tag, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, lang='en', rpp=100, since_id=since_id).pages(pages)
        for page in tweet_list:
            tweets += [x.text for x in page]
            since_id = page[-1].id
        print('Tweets found: {}'.format(len(tweets)))
        return (tweets, since_id)

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

        tweet = " ".join(tagless_list)
        tweet = self.remove_hash_symbol(tweet)
        Tweet.create_or_get(text=tweet)

        return {'text': tweet, 'tags': tag_list}


    def clean_tweet(self, tweet):
        """ Strip # character and @usernames out of tweet """
        filter_list = []
        tweet_list = tweet.split()
        for word in tweet_list:
            word = self.remove_hash_symbol(word)
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

    # tweet_list = tweepy.Cursor(bot.api.search, q="#sarcasm").pages(2)
    # for i, tweets in enumerate(tweet_list):
    #     print('------------------ {}'.format(i))
    #     for t in tweets:
    #         print(t.text)

    since_id = 1
    since_id_2 = 1
    while True:
        tweets, since_id = bot.tag_search('sarcasm', 8, since_id=since_id)
        for tweet in tweets:
            t = bot._filter_harsh(tweet, 'sarcasm')
            if t:
                print(bot.clean_tweet(t['text']))

        tweets, since_id_2 = bot.tag_search('sarcastic', 7, since_id=since_id_2)
        for tweet in tweets:
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
        time.sleep(60*5 + random.randint(1, 20))
