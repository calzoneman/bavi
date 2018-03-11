import logging
from random import choice

log = logging.getLogger('bavi.modules.random')

supported_split = [',', '|', '/', '\\']


def init(bot):
    bot.add_command('choose', choose_command)
    bot.add_command('pick', choose_command)


def choose_command(bot, source, target, message, **kwargs):
    response = ''
    result_list = make_list(message)

    if len(result_list) > 1:
        response = 'Your choices: {0}, I chose: {1}.'.format(
            ', '.join(result_list),
            choice(result_list)
        )
    else:
        response = 'You need to give me more than one thing to choose!'

    bot.reply_to(source, target, response)


def make_list(message):
    result = []

    #iterate over the spliters and pick the first one with results
    for s in supported_split:
        result = message.split(s)

        if len(result) > 1:
            break

    #strip trailing whitespace
    result = list(map(str.strip, result))

    return result
