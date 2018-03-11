#!/usr/bin/python3

import argparse
import configparser
import logging
import sys

from bavi.bot import Bot
from bavi.module_loader import load_modules

LOG_FMT = '%(asctime)-15s [%(levelname)s] %(name)s: %(message)s'

def setup_logging(conf):
    if 'log' in conf:
        log_config = conf['log']
    else:
        log_config = None

    handlers = [
        logging.StreamHandler(stream=sys.stdout)
    ]

    if not log_config:
        level = logging.INFO
        filename = None
        logging.warn('Missing logging configuration; defaulting to stdout')
    else:
        filename = log_config.get('file')

        if filename:
            handlers.append(logging.FileHandler(
                filename=filename,
                mode='a',
                encoding='utf8'
            ))

        level = log_config.get('level')

        if level not in {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}:
            raise ValueError('Unknown log level: {}'.format(level))

        level = getattr(logging, level)

    logging.basicConfig(
            level=level,
            format=LOG_FMT,
            handlers=handlers
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='General-purpose chat bot')
    parser.add_argument('-c', '--config', required=True)

    args = parser.parse_args()

    conf = configparser.ConfigParser()
    conf.read(args.config)

    setup_logging(conf)

    bot = Bot(conf)
    bot.init_irc()
    bot.init_db()
    load_modules(bot)
    bot.start()
