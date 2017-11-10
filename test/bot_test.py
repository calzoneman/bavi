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
