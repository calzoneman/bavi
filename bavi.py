#!/usr/bin/python3

import argparse
import logging
import sys

from bavi.config import load_config
from bavi.bot import Bot

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='General-purpose chat bot')
    parser.add_argument('-c', '--config', required=True)

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    conf = load_config(args.config)

    bot = Bot(conf)
    bot.start()
