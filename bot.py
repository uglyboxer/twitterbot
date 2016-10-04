import time
# import random
import sys

import peewee as pw
import tweepy

from secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import model


class Bot:

    def __init__(self):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)
        try:
            print('There are {} tweets in the database.'.format(model.Tweet.select().count()))
        except pw.OperationalError:
            model.db.create_tables([model.Tweet])
            print('There are {} tweets in the newly created Tweet table.'.format(model.Tweet.select().count()))

    def tweet(self, message):
        self.api.update_status(message)
        return True

    def count(self, tags=None):
        tags = ' '.join(tags) if isinstance(tags, (list, tuple)) else tags
        return model.Tweet.select().count() if tags is None else model.db.filter(tags=' '.join(sorted(tags.split())))

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

        tweet = " ".join(tagless_list)  # .replace("#", "")
        model.Tweet.create_or_get(text=tweet, tags=' '.join(sorted(tag_list)))

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


if __name__ == '__main__':

    hashtags = [ht.lstrip('#') for ht in sys.argv[1:]] if len(sys.argv) > 1 else ['sarcasm', 'sarcastic']

    bot = Bot()
    delay = 1  # 60 * 15 + random.randint(1, 240)
    num_requests = 1

    for i in range(num_requests):
        num_before = bot.count()
        for ht in hashtags:
            for tweet in bot.tag_search(ht, 100):
                tweet_dict = bot._filter_harsh(tweet, ht)
        num_after = bot.count()
        # if t:
        #     print(bot.clean_tweet(t['text']))
        #     break
        # for tweet in bot.tag_search('sarcastic', 500):
        #     t = bot._filter_harsh(tweet, 'sarcastic')
        #     if t:
        #         print(bot.clean_tweet(t['text']))
        print("Retrieved {} tweets with the hash tags {} for a total of {}".format(
            num_after - num_before, hashtags, num_after))
        # bot.tweet(m[:140])
        time.sleep(delay)
