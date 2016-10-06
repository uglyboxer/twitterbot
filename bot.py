from secrets import *
from model import Tweet, LastId

from peewee import fn

import tweepy, time, random



class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)


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
        print("first id: {}".format(since_id))
        search_tag = '#{}'.format(string)

        tweet_list = tweepy.Cursor(self.api.search,
                                   q=search_tag,
                                   wait_on_rate_limit=True,
                                   wait_on_rate_limit_notify=True,
                                   lang='en',
                                   rpp=100,
                                   since_id=since_id).pages(pages)
        i = 1
        for page in tweet_list:
            print("page {}".format(i))
            tweets += [x.text for x in page]
            since_id = page[-1].id
            i+=1

        last = LastId.get(id=1)
        last.last_id = since_id
        last.save()
        
        print("last id: {}".format(since_id))
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
    
    bot = Bot()

    # stream(bot, ['sarcasm'])

    # since_id = 780953436837646336
    # since_id_2 = 780953436837646336
    # LastId.create(last_id=since_id)
    
    since_id = since_id_2 = LastId.get(id=1).last_id

    while True:
        tweets, since_id = bot.tag_search('sarcasm', 10, since_id=since_id)
        for tweet in tweets:
            t = bot._filter_harsh(tweet, 'sarcasm')
            if t:
                print(bot.clean_tweet(t['text']))

        tweets, since_id_2 = bot.tag_search('sarcastic', 10, since_id=since_id_2)
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
