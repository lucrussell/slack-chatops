"""

Usage:
    slackbot [options]

Options:
    --config-file=<file>        Config file path.
"""
import os

import yaml
from docopt import docopt

from slackbot import bot


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
    mybot = bot.SlackBot(config)
    mybot.start()


if __name__ == "__main__":
    main()
