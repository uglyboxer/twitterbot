import time
import random
import sys
import json

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
        print("Retrieved {} tweets starting with:".format(len(tweet_list)))
        if tweet_list:
            print(tweet_list[0])

        return tweet_list

    def _is_acceptable(self, tweet, tag, picky=False):
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
        if picky and 'http' in tweet.text:
            return False
        else:
            if picky:
                tweet_list = tweet.text.split()
                tag_list = []
                for word in reversed(tweet_list):
                    if word[0] == "#":
                        tag_list.append(word[1:].lower())
                    else:
                        break
            else:
                tag_list = [d['text'] for d in tweet.entities.get('hashtags', [])]
            if tag not in tag_list:
                return False

        # length = len(tweet_list) - len(tag_list)
        # tagless_list = tweet_list[:length]
        # tweet.tag_list = tag_list
        # tweet.filtered_text = " ".join(tagless_list)  # .replace("#", "")
        user, created = model.User.create_or_get(
            screen_name=tweet.user.screen_name,
            followers_count=tweet.user.followers_count,
            statuses_count=tweet.user.statuses_count,
            friends_count=tweet.user.friends_count,
            favourites_count=tweet.user.favourites_count,
            )
        tweet_obj, created = model.Tweet.create_or_get(  # id=tweet.id,
            id=tweet.id,
            id_str=tweet.id_str,
            user=user,
            favorite_count=tweet.favorite_count,
            text=tweet.text,
            tags=' '.join(sorted(tag_list)))
        id_str = tweet.in_reply_to_status_id_str
        if id_str:
            tweet_replied_to, created = model.Tweet.create_or_get(id_str=id_str)
            if created:
                print("We don't have the tweet ({}) that this ({}) was a reply to , but we could GET it ;)".format(
                    id_str, tweet.id_str))
            model.Reply.create_or_get(tweet=tweet_obj, tweet_replied_to=tweet_replied_to)
        return tweet_obj

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
    args = sys.argv
    num_tweets, delay, picky = None, None, None
    # --picky flag means to ignore any tweets that contain "http" and does not end with one of the desired hashtags
    if '--picky' in args:
        del args[args.index('--picky')]
        picky = True
    hashtags = []
    # the first float found on the command line is the delay in seconds between twitter search queries
    # the first int after the first float is the number of tweets to retrieve with each twitter search query
    for arg in args[1:]:
        try:
            num_tweets = int(arg) if not num_tweets else int('unintable')
        except ValueError:
            try:
                delay = float(arg) if delay is None else float('unfloatable')
            except ValueError:
                hashtags += [arg.lstrip('#')]

    hashtags = hashtags if len(hashtags) else ['sarcasm', 'sarcastic']

    bot = Bot()
    min_delay = 0.5
    delay = 60 * 15 if delay is None else delay
    num_tweets = num_tweets or 100
    delay_std = delay * 0.20

    while True:
        num_before = bot.count()
        for ht in hashtags:
            print('=' * 80)
            print('Looking for #{}'.format(ht))
            last_tweets = []
            for tweet in bot.tag_search(ht, num_tweets):
                acceptable_tweet = bot._is_acceptable(tweet, ht, picky=picky)
                if acceptable_tweet:
                    last_tweets += [acceptable_tweet]
            print(json.dumps(last_tweets, default=model.Serializer(), indent=2))
            time.sleep(max(random.gauss(delay, delay_std), min_delay))

        num_after = bot.count()
        print("Retrieved {} tweets with the hash tags {} for a total of {}".format(
            num_after - num_before, hashtags, num_after))
        # bot.tweet(m[:140])
