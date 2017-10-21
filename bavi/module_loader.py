import importlib
import logging
import os

import bavi.modules

log = logging.getLogger('bavi.module_loader')

def load_modules(bot):
    for f in os.listdir(os.path.join(os.path.dirname(__file__), 'modules')):
        if f.endswith('.py') and not f.endswith('__init__.py'):
            load_module(bot, f)

def load_module(bot, filename):
    path = os.path.basename(filename)[:-3]
    log.info('Loading module %s', path)
    try:
        mod = importlib.import_module('.' + path, 'bavi.modules')
        mod.init(bot)
    except Exception as exception:
        log.error('Failed to load module %s: %s', path, str(exception))
