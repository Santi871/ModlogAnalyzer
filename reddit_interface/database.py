from peewee import *

db = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = db


class Moderator(BaseModel):
    name = TextField(unique=True)
    added = DateTimeField()
    permissions = TextField(null=True)
    type = TextField()


class ModAction(BaseModel):
    mod = ForeignKeyField(Moderator, related_name='modactions', to_field='name')
    description = TextField(null=True)
    mod_id36 = TextField(null=True)
    created_utc = DateTimeField(null=True)
    subreddit = TextField(null=True)
    target_title = TextField(null=True)
    target_permalink = TextField(null=True)
    details = TextField(null=True)
    action = TextField(null=True)
    target_author = TextField(null=True)
    target_fullname = TextField(null=True)
    sr_id36 = TextField(null=True)
    item_id = TextField(unique=True)
