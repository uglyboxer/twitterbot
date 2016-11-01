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
        print(status.text)


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
                tag_list = [d['text'].lower() for d in tweet.entities.get('hashtags', [])]
            if tag not in tag_list:
                return False

        return tweet

    def save_tweet(self, tweet):
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
            id=tweet.id,
            id_str=tweet.id_str,
            user=user_record,
            favorite_count=tweet.favorite_count,
            text=tweet.text,
            tags=' '.join(sorted(tag_list)))
        id_str = tweet.in_reply_to_status_id_str
        if id_str:
            tweet_replied_to, created = model.Tweet.create_or_get(id_str=id_str)
            if created:
                print("We don't have the tweet ({}) that this ({}) was a reply to , but we could GET it ;)".format(
                    id_str, tweet.id_str))
            model.Reply.create_or_get(tweet=tweet_record, tweet_replied_to=tweet_replied_to)
        return tweet_record

    def clean_tweet(self, tweet):
        """ Strip # character and @usernames out of tweet """
        filter_list = []
        tweet_list = tweet.split()
        for word in tweet_list:
            word = self.remove_hash_symbol(word)
            if word[0] != '@' and 'http' not in word:
                filter_list.append(word)
        return " ".join(filter_list)


# FIXME: use builtin argparse module instead
def parse_args(args):
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
    delay = 60 * 15 if delay is None else delay
    num_tweets = num_tweets or 100
    arg_dict = {
        'num_tweets': num_tweets,
        'delay': delay,
        'picky': picky,
        'hashtags': hashtags,
        }
    print('Parsed args into:')
    print(json.dumps(arg_dict, indent=4))
    return arg_dict


def stream(bot, filter_list):
    """
    @brief      Create focused stream from the Twitter firehose
    
    @param      bot          Instance of Bot class
    @param      filter_list  list of search terms
    """
    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth = bot.api.auth, listener=myStreamListener)
    myStream.filter(track=filter_list)


if __name__ == '__main__':
    args = parse_args(sys.argv)
    bot = Bot()
    min_delay = 0.5
    delay_std = args['delay'] * 0.10

    # stream(bot, ['sarcasm'])

    # since_id = 780953436837646336
    # since_id_2 = 780953436837646336
    # LastId.create(last_id=since_id)
    
    since_id = since_id_2 = LastId.get(id=1).last_id

    while True:
        num_before = bot.count()
        print('=' * 80)
        # TODO: hashtags attribute of Bot
        #       if more than 15 hashtags just search for them in pairs, tripplets, etc
        for ht in args['hashtags']:
            print('Looking for #{}'.format(ht))
            last_tweets = []
            try:
                for tweet in bot.tag_search(ht, args['num_tweets']):
                    acceptable_tweet = bot._is_acceptable(tweet, ht, picky=args['picky'])
                    if acceptable_tweet:
                        last_tweets += [bot.save_tweet(acceptable_tweet)]
                print(json.dumps(last_tweets, default=model.Serializer(), indent=2))
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
            sleep_seconds = max(random.gauss(args['delay'], delay_std), min_delay)
            print('sleeping for {} s ...'.format(round(sleep_seconds, 2)))
            time.sleep(sleep_seconds)

        num_after = bot.count()
        print("Retrieved {} tweets with the hash tags {} for a total of {}".format(
            num_after - num_before, args['hashtags'], num_after))
        # bot.tweet(m[:140])
