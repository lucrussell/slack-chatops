"""

Usage:
    slackbot [options]

Options:
    --config-file=<file>        Config file path.
"""
import io
import os
import sys
import time

import docker
import yaml
from docopt import docopt
from slackclient import SlackClient


class SlackBot(object):

    def __init__(self, config=None):
        self.config = config
        self.token = self.config.get('slack_token')
        self.slack_client = SlackClient(self.token)
        self.bot_id = self.get_bot_id()

        self.respond_to = ['list graph shortcuts',
                           'graph <shortcut>',
                           'help']
        self.help_msg = '```\n'
        for answer in self.respond_to:
            self.help_msg += f'{answer}\n'
        self.help_msg += '```'

        # This is a set of predefined shortcuts for commonly used graphs
        self.graph_urls = {}
        self.graph_shortcuts = '```\n'
        for name, url in config['graph_urls'].items():
            self.graph_urls[name] = url
            self.graph_shortcuts += f'{name}\n'
        self.graph_shortcuts += '```'

    def get_bot_id(self):
        api_call = self.slack_client.api_call("users.list")
        if api_call.get('ok'):
            # List all users so we can find our bot
            users = api_call.get('members')
            for user in users:
                if 'name' in user and user.get('name') == self.config.get('bot_name'):
                    return "<@" + user.get('id') + ">"

            return None

    def start(self):
        if self.slack_client.rtm_connect():
            print("Bot is alive and listening for messages...")
            while True:
                events = self.slack_client.rtm_read()
                for event in events:
                    if event.get('type') == 'message':
                        # If we received a message, read it and respond if necessary
                        self.on_message(event)

                time.sleep(1)
        else:
            print('Connection failed, invalid token?')
            sys.exit(1)

    def on_message(self, event):
        # Ignore edits and uploads
        subtype = event.get('subtype', '')
        if subtype == u'message_changed' or subtype == u'file_share':
            return

        # Don't respond to messages sent by the bot itself
        if event.get('user', '') == self.bot_id:
            return

        full_text = event.get('text', '') or ''

        # Only respond to messages addressed directly to the bot
        if full_text.startswith(self.bot_id):
            # Strip off the bot id and parse the rest of the message as the question
            question = full_text[len(self.bot_id):]
            if len(question) > 0:
                question = question.strip().lower()
                channel = event['channel']
                if 'list graph shortcuts' in question:
                    self.respond(channel, f'Graph shortcuts: {self.graph_shortcuts}')
                elif 'graph' in question:
                    self.respond(channel, 'Please wait...', True)
                elif 'help' in question:
                    self.respond(channel, f'I can answer questions about: {self.help_msg}')
                else:
                    self.respond(channel, f'Sorry, I can only answer questions about: {self.help_msg}')

    def respond(self, channel, text, upload=False):
        self.slack_client.api_call(
            'chat.postMessage',
            channel=channel,
            text=text,
            as_user='true:')
        if upload:
            for graph_name, url in self.graph_urls.items():
                self.generate_and_upload_graph(graph_name, url, channel)

    def generate_and_upload_graph(self, filename, url, channel):
        # Create the graph in the current directory
        dir_name = os.path.dirname(os.path.abspath(__file__))

        client = docker.APIClient()

        # Use the Docker Python API to dynamically create a container based on the alekzonder/puppeteer image
        # Bind to the current directory so we can write the file somewhere accessible
        # Use network_mode=host so the container can access Grafana over localhost
        container = client.create_container(
            image='alekzonder/puppeteer:1.0.0',
            command=f'screenshot \'{url}\' 1366x768',
            volumes=[dir_name],

            host_config=client.create_host_config(binds={
                dir_name: {
                    'bind': '/screenshots'
                }
            }, network_mode='host')
        )

        files1 = prepare_dir(dir_name)

        client.start(container)

        # Poll for new files
        while True:
            time.sleep(2)
            files2 = os.listdir(dir_name)
            new = [f for f in files2 if all([f not in files1, f.endswith(".png")])]
            for f in new:
                with open(f, 'rb') as in_file:
                    ret = self.slack_client.api_call(
                        "files.upload",
                        filename=filename,
                        channels=channel,
                        title=filename,
                        file=io.BytesIO(in_file.read()))
                    if 'ok' not in ret or not ret['ok']:
                        print('File upload failed %s', ret['error'])
                os.remove(f)
            break


def prepare_dir(dir_name):
    # Check for any images from a previous run and remove them
    files1 = os.listdir(dir_name)
    for item in files1:
        if item.endswith(".png"):
            os.remove(os.path.join(dir_name, item))
    return os.listdir(dir_name)


def configure(filename):
    if os.path.exists(filename) is False:
        raise IOError("{0} does not exist".format(filename))

    with open(filename) as config_file:
        config_data = yaml.load(config_file)

    return config_data


def main(arguments=None):
    if not arguments:
        arguments = docopt(__doc__)
    config = configure(arguments['--config-file'])
    mybot = SlackBot(config)
    mybot.start()


if __name__ == "__main__":
    main()
