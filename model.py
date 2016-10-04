import peewee as pw


db = pw.SqliteDatabase('tweets.db')


class BaseModel(pw.Model):
    class Meta:
        database = db


class Tweet(BaseModel):
    text = pw.CharField()
    tags = pw.CharField()
