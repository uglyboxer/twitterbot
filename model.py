import datetime

import peewee as pw


db = pw.SqliteDatabase('tweets.db')


class BaseModel(pw.Model):
    class Meta:
        database = db


class Place(BaseModel):
    """Twitter API json "place" key"""
    place_type = pw.CharField()
    country_code = pw.CharField()
    country = pw.CharField()
    name = pw.CharField()
    full_name = pw.CharField()
    url = pw.CharField()  # URL to json polygon of place boundary
    bounding_box_coordinates = pw.CharField()  # json list of 4 [lat, lon] pairs


class User(BaseModel):
    # id = pw.BigIntegerField()
    screen_name = pw.CharField(unique=True)
    # location = pw.ForeignKey(Place)
    followers_count = pw.IntegerField(null=True)
    created_date = pw.DateTimeField(default=datetime.datetime.now)
    statuses_count = pw.IntegerField(null=True)
    friends_count = pw.IntegerField(null=True)


class Tweet(BaseModel):
    id = pw.BigIntegerField(null=True)
    id_str = pw.CharField(null=True)
    user = pw.ForeignKeyField(User, null=True, related_name='tweets')
    source = pw.CharField(null=True)  # e.g. "Twitter for iPhone"
    text = pw.CharField()
    tags = pw.CharField(null=True)  # e.g. "#sarcasm #angry #trumped"
    created_date = pw.DateTimeField(default=datetime.datetime.now)
    is_published = pw.BooleanField(default=True)
    location = pw.CharField(null=True)
    place = pw.ForeignKeyField(Place)
    verified = pw.BooleanField(null=True)
    favourites_count = pw.IntegerField(null=True)
    # tweet_replied_to = pw.ForeignKeyField("Tweet", related_name='replies')


class Reply(BaseModel):
    # in_reply_to_status_id
    tweet_replied_to = pw.ForeignKeyField(Tweet, related_name='replies')
    tweet = pw.ForeignKeyField(Tweet, related_name='prompts')


def create_tables():
    db.connect()
    db.create_tables([Place, User, Tweet, Reply])
