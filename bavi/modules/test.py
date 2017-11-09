import logging

log = logging.getLogger('bavi.modules.test')

def init(bot):
    log.info('initializing the test module')
    bot.add_command('test', test_command)

def test_command(bot, source, target, message, **kwargs):
    bot.say(target, 'The test result is: ' + message.split()[0])
