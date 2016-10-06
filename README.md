# Twitter Bot

## A baseline gateway for a Twitterbot.  What it has to say, will come shortly.

Instructions for obtaining keys and tokens, and the basic Python for accessing the Twitter API can be found [here](http://www.dototot.com/how-to-write-a-twitter-bot-with-python-and-tweepy/).


The rest of this document will fill out as I decide what it will actually do.

License:  Whatev's  Have fun with it.


Helper functions _filter_harsh and clean_tweet, are very specific use cases and could be abstracted out.

```python
Bot._filter_harsh(tweet, tag)
```
Is specifically for stripping the tags, only from the end a tweet, and verifying the given parameter tag is in that list.

```python
Bot.clean_tweet(tweet, tag)
```
Is specifically for pulling out the # character, usernames, and urls.


Calling the function stream will steam realtime tweets filtered on the elements
of the arg list.  Output is to the stdout but can be modifiied in class MyStreamListener

```python
bot = Bot()
stream(bot, ['sarcasm'])
```

TODO.  Make each of those a separate cleaning function.
TODO.  Remove RT.  Filter those tweets too?
TODO.  Tests.
TODO.  Make table for search tags with a Many to Many relation to the Tweets table for storing more searches.