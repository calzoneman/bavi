import re
import unittest
from unittest.mock import MagicMock

from irc.client import NickMask, Event

import bavi.bot

class Dummy:
    pass

class BotTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = bavi.bot.Bot(None)
        self.bot.connection = Dummy()
        self.bot.connection.get_nickname = lambda: 'TestBot'
        self.bot.connection.privmsg = MagicMock()
        self.bot.channels = { '#test' }

    def test_command_with_no_args_works(self):
        def handler(bot, source, target, message, **kwargs):
            bot.say(target, 'This is an example')
        def handler2(bot, source, target, message, **kwargs):
            bot.say(target, 'This is a second example')

        self.bot.add_command('example', handler)
        self.bot.add_command('example2', handler2)
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['.example']
                )
        )
        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'This is an example'
        )

        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['TestBot: example2']
                )
        )
        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'This is a second example'
        )

    def test_command_alias_works(self):
        def handler(bot, source, target, message, **kwargs):
            bot.say(target, 'This is an example')

        self.bot.add_command('example', handler, aliases=['a1', 'a2'])
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['.a1']
                )
        )
        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'This is an example'
        )

        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['.a2']
                )
        )
        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'This is an example'
        )

    def test_command_already_exists_registration_fails(self):
        def handler(bot, source, target, message, **kwargs):
            bot.say(target, 'This is an example')

        self.bot.add_command('example', handler)

        try:
            self.bot.add_command('example', handler)
        except RuntimeError:
            return
        else:
            raise AssertionError('Expected RuntimeError due to duplicate cmd')

    def test_command_not_found_replies_to_user(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['.notacommand 1 2']
                )
        )

        self.bot.connection.privmsg.assert_called_with(
                '#test',
                "user: I don't know about that command."
        )

    def test_command_failure_replies_with_error(self):
        def handler(bot, source, target, message, **kwargs):
            raise KeyError('frobulator')

        self.bot.add_command('example', handler)
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['.example']
                )
        )
        self.bot.connection.privmsg.assert_called_with(
                '#test',
                "KeyError: 'frobulator'"
        )

    def test_say_sanitizes_message(self):
        self.bot.say('#test', 'Invalid \0m\ressa\nge')

        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'Invalid message'
        )

    def test_say_raises_when_given_invalid_channel(self):
        try:
            self.bot.say('#wrong-channel', 'Some message')
        except KeyError:
            pass
        else:
            raise AssertionError('Expected KeyError for wrong channel')

        self.bot.connection.privmsg.assert_not_called()

    def test_reply_to_sanitizes_message(self):
        self.bot.reply_to(
                NickMask('user!ident@host'),
                '#test',
                'Invalid \0m\ressa\nge'
        )

        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'user: Invalid message'
        )

    def test_reply_to_raises_when_given_invalid_channel(self):
        try:
            self.bot.reply_to(
                    NickMask('user!ident@host'),
                    '#wrong-channel',
                    'Some message'
            )
        except KeyError:
            pass
        else:
            raise AssertionError('Expected KeyError for wrong channel')

        self.bot.connection.privmsg.assert_not_called()

    def test_add_matcher(self):
        def handler(bot, source, target, message, match):
            bot.say(target, 'Matched {}'.format(match.group(1)))

        self.bot.add_matcher(re.compile(r'matchme:([0-9]+)'), handler)

        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['this is an matchme:123 example']
                )
        )
        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'Matched 123'
        )

    def test_matcher_raises_error_prints_error(self):
        def handler(bot, source, target, message, match):
            raise ValueError('Something is wrong')

        self.bot.add_matcher(re.compile(r'matchme:([0-9]+)'), handler)

        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['this is an matchme:123 example']
                )
        )
        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'ValueError: Something is wrong'
        )

    def test_add_matcher_high_priority(self):
        def handler(bot, source, target, message, match):
            bot.say(target, 'Matched {}'.format(match.group(1)))

        def important_handler(bot, source, target, message, match):
            bot.say(target, 'Important {}'.format(match.group(1)))

        self.bot.add_matcher(re.compile(r'matchme:([0-9]+)'), handler)
        self.bot.add_matcher(
                re.compile(r'matchme:([0-9]+)'),
                important_handler,
                priority='high'
        )

        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['this is an matchme:123 example']
                )
        )
        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'Important 123'
        )

    def test_add_matcher_med_priority(self):
        def handler(bot, source, target, message, match):
            bot.say(target, 'Matched {}'.format(match.group(1)))

        def important_handler(bot, source, target, message, match):
            bot.say(target, 'Important {}'.format(match.group(1)))

        self.bot.add_matcher(re.compile(r'matchme:([0-9]+)'), handler)
        self.bot.add_matcher(
                re.compile(r'matchme:([0-9]+)'),
                important_handler,
                priority='medium'
        )

        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('user!ident@host'),
                    '#test',
                    ['this is an matchme:123 example']
                )
        )
        self.bot.connection.privmsg.assert_called_with(
                '#test',
                'Important 123'
        )

    def test_add_matcher_invalid_priority(self):
        def handler(bot, source, target, message, match):
            bot.say(target, 'Matched {}'.format(match.group(1)))

        try:
            self.bot.add_matcher(
                    re.compile(r'matchme:([0-9]+)'),
                    handler,
                    priority='invalid'
            )
        except ValueError:
            pass
        else:
            raise AssertionError('Expected ValueError for priority')

    def test_add_matcher_regex_not_compiled(self):
        def handler(bot, source, target, message, match):
            bot.say(target, 'Matched {}'.format(match.group(1)))

        try:
            self.bot.add_matcher(r'matchme:([0-9]+)', handler)
        except TypeError:
            pass
        else:
            raise AssertionError('Expected TypeError for regex')
