# Twitter Bot

## A baseline gateway for a Twitterbot.  What it has to say, will come shortly.

Instructions for obtaining keys and tokens, and the basic Python for accessing the Twitter API can be found [here](http://www.dototot.com/how-to-write-a-twitter-bot-with-python-and-tweepy/).

License:  Whatev's  Have fun with it.

```bash
python bot.py <--picky> <num_tweets (int)> <delay (float)> <hashtag (string)>
```
Options:

The flag --picky will filter found tweets.  Drop anything with "http" in the text (no links).  And require that the searched hashtag be in a list of hashtags at the end of the tweet.

num_tweets : Max number to find
delay : (float) the number of seconds to pause between searches (for rate limit concerns)
hashtag : #(string)  Requires the hash symbol and a string.  Can be any number of space-delimited tags.

Tweets that are replies also capture the tweet they are replying too. 