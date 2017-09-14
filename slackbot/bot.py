import sys
import shutil

import io
import requests

import time
from slackclient import SlackClient

from slackbot import lag
from slackbot.lag import format_response


class SlackBot(object):

    def __init__(self, config=None):
        self.config = config
        self.token = config.get('slack_token')
        self.bot_name = config.get('bot_name')
        self.respond_to = ['lag', 'graphs', 'help']

        self.help_msg = '```\n'
        for answer in self.respond_to:
            self.help_msg += '{}\n'.format(answer)
        self.help_msg += '```'

        self.graph_urls = {}
        for key, value in config['broker_groups'].items():
            for name, url in value['graphs'].items():
                self.graph_urls[name] = url
        self.slack_client = SlackClient(self.token)

    def start(self):
        if self.slack_client.rtm_connect():
            print("Bot is alive and listening for messages...")
            while True:
                events = self.slack_client.rtm_read()
                for event in events:
                    if event.get('type') == 'message':
                        response = self.on_message(event)
                        if response:
                            channel = event['channel']
                            self.respond(channel, response)
                time.sleep(1)
        else:
            print('Connection failed, invalid token?')
            sys.exit(1)

    def on_message(self, msg):
        if msg.get('subtype', '') == u'message_changed':
            return

        bot_name = "<@{}>".format(self.bot_name)

        if msg.get('user', '') == self.bot_name:
            return

        full_text = msg.get('text', '') or ''
        if full_text.startswith(bot_name):
            question = full_text[len(bot_name):]
            if len(question) > 0:
                question = question.lower()
                if 'lag' in question:
                    lag_responder = lag.KafkaLag(self.config)
                    try:
                        return format_response(lag_responder.report())
                    except Exception:
                        return 'Hmm, I\'m having trouble connecting to Kafka'

                elif 'graph' in question:
                    return 'Generating graphs...'

                elif 'help' in question:
                    return 'I can answer questions about: {}'.format(
                        self.help_msg)
                else:
                    return 'Sorry, I can only answer ' \
                           'questions about: {}'.format(self.help_msg)

    def respond(self, channel, text):
        self.slack_client.api_call(
            'chat.postMessage',
            channel=channel,
            text=text,
            as_user='true:')
        if 'graph' in text and 'help' not in text:
            for graph_name, url in self.graph_urls.items():
                self.upload_file(graph_name, url, channel)

    def upload_file(self, filename, url, channel):
        url_response = requests.get(url, stream=True)
        with open(filename, 'wb') as out_file:
            shutil.copyfileobj(url_response.raw, out_file)
        del url_response
        try:
            with open(filename, 'rb') as in_file:
                ret = self.slack_client.api_call(
                    "files.upload",
                    filename=filename,
                    channels=channel,
                    title=filename,
                    file=io.BytesIO(in_file.read()))
                if 'ok' not in ret or not ret['ok']:
                    print('File upload failed %s', ret['error'])
        except Exception as e:
            print(e)
