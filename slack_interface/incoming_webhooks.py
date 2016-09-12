import json
import requests


class IncomingWebhook:

    def __init__(self, url):
        self.url = url

    def send_message(self, response):
        requests.post(self.url, data=response.get.json())


class SlackField:

    def __init__(self, title, value, short="true"):
        self.field_dict = dict()
        self.field_dict['title'] = title
        self.field_dict['value'] = value
        self.field_dict['short'] = short


class SlackAttachment:

    def __init__(self, title=None, text=None, fallback=None, callback_id=None, color=None, title_link=None,
                 image_url=None, footer=None, author_name=None, ts=None):

        self.attachment_dict = dict()

        if fallback is not None:
            self.attachment_dict['fallback'] = fallback
        if callback_id is not None:
            self.attachment_dict['callback_id'] = callback_id
        if color is not None:
            self.attachment_dict['color'] = color
        if title_link is not None:
            self.attachment_dict['title_link'] = title_link
        if image_url is not None:
            self.attachment_dict['image_url'] = image_url
        if title is not None:
            self.attachment_dict['title'] = title
        if text is not None:
            self.attachment_dict['text'] = text
        if footer is not None:
            self.attachment_dict['footer'] = footer
        if author_name is not None:
            self.attachment_dict['author_name'] = author_name
        if ts is not None:
            self.attachment_dict['ts'] = ts

        self.attachment_dict['mrkdwn_in'] = ['title', 'text']

    def add_field(self, title, value, short="true"):

        if 'fields' not in self.attachment_dict:
            self.attachment_dict['fields'] = []

        field = SlackField(title, value, short)
        self.attachment_dict['fields'].append(field.field_dict)


class SlackMessage:

    """Class used for easy crafting of a Slack response"""

    def __init__(self, text=None, response_type="in_channel", replace_original=True):
        self.response_dict = dict()
        self.attachments = []
        self._is_prepared = False

        if text is not None:
            self.response_dict['text'] = text

        if not replace_original:
            self.response_dict['replace_original'] = 'false'

        self.response_dict['response_type'] = response_type

    def add_attachment(self, title=None, text=None, fallback=None, callback_id=None, color=None,
                       title_link=None, footer=None,
                       image_url=None, author_name=None, ts=None):

        if 'attachments' not in self.response_dict:
            self.response_dict['attachments'] = []

        attachment = SlackAttachment(title=title, text=text, fallback=fallback, callback_id=callback_id, color=color,
                                     title_link=title_link, image_url=image_url, footer=footer, author_name=author_name,
                                     ts=ts)

        self.attachments.append(attachment)

    def _prepare(self):
        self.response_dict['attachments'] = []
        for attachment in self.attachments:
            self.response_dict['attachments'].append(attachment.attachment_dict)

    def get_json(self):

        """Returns the JSON form of the response, ready to be sent to Slack via POST data"""

        self._prepare()

        return json.dumps(self.response_dict)

    def get_dict(self):

        """Returns the dict form of the response, can be sent to Slack in GET or POST params"""

        self._prepare()

        return self.response_dict

