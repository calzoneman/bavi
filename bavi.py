#!/usr/bin/python3

import argparse
import configparser
import logging
import sys

from bavi.bot import Bot
from bavi.module_loader import load_modules

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='General-purpose chat bot')
    parser.add_argument('-c', '--config', required=True)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    conf = configparser.ConfigParser()
    conf.read(args.config)

    bot = Bot(conf)
    bot.init_irc()
    load_modules(bot)
    bot.start()
