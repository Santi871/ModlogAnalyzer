from time import sleep
from reddit_interface.database import *
import datetime
from slack_interface.incoming_webhooks import IncomingWebhook, SlackMessage
import configparser


config = configparser.ConfigParser()
config.read('config.ini')
WEBHOOK_URL = config.get('slack', 'webhook_url')


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
        self.webhook = IncomingWebhook(WEBHOOK_URL)
        db.init(subreddit + '.db')
        db.connect()

        try:
            db.create_tables([Moderator, ModAction])
        except OperationalError:
            pass
        self.pull_mods()
        self.forbidden_actions = ("removelink", "approvelink", "approvecomment", "distinguish", "ignorereports",
                                  "sticky", "unsticky")

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
                        'target_permalink': item.target_permalink,
                        'sr_id36': item.sr_id36,
                        'item_id': item.id
                    }
                    data_source.append(item_dict)
                    mod_type = Moderator.get(Moderator.name == item.mod).type

                    if mod_type == "comments" and item.action in self.forbidden_actions:
                        slack_payload = SlackMessage()
                        slack_payload.add_attachment(title="Comments moderator has performed a forbidden modaction.",
                                                     title_link=item.target_permalink,
                                                     text=item.mod + " performed action '%s'" % item.action,
                                                     color='danger')
                        self.webhook.send_message(slack_payload)

            with db.atomic():
                try:
                    ModAction.insert_many(data_source).execute()
                except IntegrityError:
                    pass
            sleep(wait)


def count_mod_actions(moderator, period='all'):
    threshold_timestamp = datetime.datetime.utcnow()

    if period == 'month':
        threshold_timestamp = threshold_timestamp - datetime.timedelta(days=30)
    elif period == 'week':
        threshold_timestamp = threshold_timestamp - datetime.timedelta(days=7)
    elif period == 'day':
        threshold_timestamp = threshold_timestamp - datetime.timedelta(days=1)

    return len(ModAction.select().join(Moderator).where(Moderator.name == moderator and
                                                        ModAction.created_utc < threshold_timestamp.timestamp()))




