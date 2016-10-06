from peewee import *
# from playhouse.fields import ManyToManyField


db = SqliteDatabase('tweets.db')


class Tweet(Model):

    text = CharField(unique=True)
    

class LastId(Model):

    last_id = IntegerField()


# class Tag(Model):

#     tag = CharField()
#     tweet = ManyToManyField(Tweet, related_name='tags')

# db.create_tables([Tweet, LastId])