import time
import random
import sys
import json
from traceback import format_exc

import peewee as pw
import tweepy

from secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
import model



class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        try:
            status = status.retweeted_status
        except AttributeError:
            pass
        img_url = get_image(status)
        if img_url:
            print(img_url)
            print(status.text)
            save_tweet(status, img_url)


class Bot:

    def __init__(self):
        self.auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        self.auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(self.auth)
        try:
            print('There are {} tweets in the database.'.format(model.Tweet.select().count()))
        except pw.OperationalError:
            model.create_tables()
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
                                     tweet_mode='extended',
                                     count=quantity,
                                     lang='en')
        print("Retrieved {} tweets starting with:".format(len(tweet_list)))
        if tweet_list:
            print(tweet_list[0])

        return tweet_list

    def clean_tweet(self, tweet):
        """ Strip # character and @usernames out of tweet """
        filter_list = []
        tweet_list = tweet.split()
        for word in tweet_list:
            word = self.remove_hash_symbol(word)
            if word[0] != '@' and 'http' not in word:
                filter_list.append(word)
        return " ".join(filter_list)


def save_tweet(tweet, img_url=None):
    tag_list = [d['text'] for d in tweet.entities.get('hashtags', [])]
    # FIXME probably maintain unique User list based on id_str alone
    #       keep track of dynamic attributes over time as dated lists (jsonfields or related tables)
    user_record, created = model.User.create_or_get(
        screen_name=tweet.user.screen_name,
        followers_count=tweet.user.followers_count,
        statuses_count=tweet.user.statuses_count,
        friends_count=tweet.user.friends_count,
        favourites_count=tweet.user.favourites_count,
        )
    # FIXME: tweet text should be unique
    #        dynamic attributes should be a dated list (jsonfield)
    tweet_record, created = model.Tweet.create_or_get(  # id=tweet.id,
        tweet_id=tweet.id,
        id_str=tweet.id_str,
        user=user_record,
        favorite_count=tweet.favorite_count,
        text=tweet.text,
        tags=' '.join(sorted(tag_list)),
        img_url=img_url)
    if not created:
        print('Already had it.')
    id_str = tweet.in_reply_to_status_id_str
    if id_str:
        tweet_replied_to, created = model.Tweet.create_or_get(id_str=id_str)
        if created:
            print("We don't have the tweet ({}) that this ({}) was a reply to , but we could GET it ;)".format(
                id_str, tweet.id_str))
        model.Reply.create_or_get(tweet=tweet_record, tweet_replied_to=tweet_replied_to)
    return tweet_record


def get_image(tweet):

    img_urls = []
    if hasattr(tweet, 'extended_entities') and tweet.extended_entities['media']:
        for img in tweet.extended_entities['media']:
            if img['type'] == 'photo':
                img_urls.append(img['media_url_https'])
    if img_urls:
        return img_urls[0]
    return None


def stream(bot, filter_list):
    """
    @brief      Create focused stream from the Twitter firehose
    
    @param      bot          Instance of Bot class
    @param      filter_list  list of search terms
    """
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth = bot.api.auth, listener=myStreamListener, tweet_mode='extended')
    myStream.filter(track=filter_list)


def get_tweets(hashtags):
    bot = Bot()
    min_delay = 0.5
    delay_std = 15 * 0.10
    max_tweets = 3200

    # stream(bot, ['sarcasm'])

    while True:
        num_before = bot.count()
        print('=' * 80)
        for ht in hashtags:
            print('Looking for #{}'.format(ht))
            last_tweets = []
            try:
                for tweet in bot.tag_search(ht, quantity=max_tweets):
                    img_url = get_image(tweet)
                    if img_url:
                        print(img_url)
                        bot.save_tweet(tweet, img_url)
                # print(json.dumps(last_tweets, defauolt=model.Serializer(), indent=2))

            except:
                print('!' * 80)
                print(format_exc())
                bot.rate_limit_status = bot.api.rate_limit_status()
                print('Search Rate Limit Status')
                print(json.dumps(bot.rate_limit_status['resources']['search'], default=model.Serializer(), indent=2))
                print('Application Rate Limit Status')
                print(json.dumps(bot.rate_limit_status['resources']['application'], default=model.Serializer(), indent=2))
                print("Unable to retrieve any tweets! Will try again later.")
            print('--' * 80)
            sleep_seconds = max(random.gauss(5, delay_std), min_delay)
            print('sleeping for {} s ...'.format(round(sleep_seconds, 2)))
            time.sleep(sleep_seconds)

        num_after = bot.count()
        print("Retrieved {} tweets with the hash tags {} for a total of {}".format(
            num_after - num_before, hashtags, num_after))
        # bot.tweet(m[:140])


if __name__ == '__main__':
    # get_tweets(['brutalism', 'architecture', 'nasa'])
    tag_list = ['brutalism', 'architecture', 'nasa']
    b = Bot()
    stream(b, tag_list)
