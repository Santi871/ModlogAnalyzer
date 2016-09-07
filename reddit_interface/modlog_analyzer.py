from time import sleep
from reddit_interface.database import *
import datetime


class ModUser:

    def __init__(self, name, added, permissions):
        self.name = name
        self.added = added
        self.permissions = ','.join(permissions)

        if permissions == ['posts']:
            self.type = 'comments'
        elif not permissions:
            self.type = 'none'
            self.permissions = 'none'
        else:
            self.type = 'full'


class ModlogLogger:

    def __init__(self, r, subreddit):
        self.r = r
        self.subreddit = self.r.get_subreddit(subreddit)
        self.already_done = list()
        db.init(subreddit + '.db')
        db.connect()

        try:
            db.create_tables([Moderator, ModAction])
        except OperationalError:
            pass
        self.pull_mods()

    def pull_mods(self):

        url = 'https://www.reddit.com/r/' + self.subreddit.display_name + '/about/moderators/.json'
        children = self.r.request_json(url, as_objects=False)['data']['children']
        data_source = list()

        for item in children:
            mod = ModUser(item['name'], item['date'], item['mod_permissions'])
            mod_dict = {
                'name': mod.name,
                'added': datetime.datetime.fromtimestamp(mod.added),
                'permissions': mod.permissions,
                'type': mod.type
            }
            data_source.append(mod_dict)

        with db.atomic():
            try:
                Moderator.insert_many(data_source).execute()
            except IntegrityError:
                pass

    def pull_modlog(self, limit=50, wait=10):

        while True:
            modlog = self.subreddit.get_mod_log(limit=limit)
            data_source = list()

            for item in modlog:
                if item.mod != "ELI5_BotMod" and item.mod != 'AutoModerator':
                    item_dict = {
                        'mod': item.mod,
                        'description': item.description,
                        'mod_id36': item.mod_id36,
                        'created_utc': datetime.datetime.fromtimestamp(item.created_utc),
                        'subreddit': item.subreddit,
                        'action': item.action,
                        'target_title': item.target_title,
                        'target_author': item.target_author,
                        'target_fullname': item.target_fullname,
                        'sr_id36': item.sr_id36,
                        'item_id': item.id
                    }
                    data_source.append(item_dict)

            with db.atomic():
                try:
                    ModAction.insert_many(data_source).execute()
                except IntegrityError:
                    pass
            sleep(wait)


def count_mod_actions(moderator):
    return len(ModAction.select().join(Moderator).where(Moderator.name == moderator))




