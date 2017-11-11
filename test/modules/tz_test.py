import sqlite3
import unittest
from unittest.mock import MagicMock

from irc.client import Event, NickMask

import bavi.bot
import bavi.modules.tz as tz_module

class TzModuleTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = bavi.bot.Bot(None)
        self.bot.db = sqlite3.connect(':memory:')
        tz_module.init(self.bot)
        self.bot.say = MagicMock()
        self.bot.reply_to = MagicMock()

    def test_settz_create_and_update(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.settz America/Chicago']
                )
        )
        self.bot.reply_to.assert_called_with(
                NickMask('test!user@example.com'),
                '#test',
                'Your timezone has been set to America/Chicago'
        )

        c = self.bot.db.cursor()
        c.execute('SELECT tz FROM tz_info WHERE nick = ?', ('test',))

        tz, = next(c)
        assert tz == 'America/Chicago'

        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'), '#test',
                    ['.settz America/New_York']
                )
        )
        self.bot.reply_to.assert_called_with(
                NickMask('test!user@example.com'),
                '#test',
                'Your timezone has been set to America/New_York'
        )

        c = self.bot.db.cursor()
        c.execute('SELECT tz FROM tz_info WHERE nick = ?', ('test',))

        tz, = next(c)
        assert tz == 'America/New_York'

    def test_settz_invalid_timezone(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.settz NotA/RealTimezone']
                )
        )
        self.bot.reply_to.assert_called_with(
                NickMask('test!user@example.com'),
                '#test',
                "I don't know about that timezone"
        )

        c = self.bot.db.cursor()
        c.execute('SELECT tz FROM tz_info WHERE nick = ?', ('test',))

        assert len(list(c)) == 0

    def test_settz_missing_timezone(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.settz']
                )
        )
        self.bot.reply_to.assert_called_with(
                NickMask('test!user@example.com'),
                '#test',
                'Give me a timezone, for example .settz America/Los_Angeles'
        )

        c = self.bot.db.cursor()
        c.execute('SELECT tz FROM tz_info WHERE nick = ?', ('test',))

        assert len(list(c)) == 0

    def test_time_for_self(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.settz America/Chicago']
                )
        )
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.time']
                )
        )

        response = self.bot.say.call_args[0][1]
        assert response.startswith('Current time in America/Chicago is: ')

    def test_time_for_other(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('other!user@example.com'),
                    '#test',
                    ['.settz America/Chicago']
                )
        )
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.time other']
                )
        )

        response = self.bot.say.call_args[0][1]
        assert response.startswith('Current time in America/Chicago is: ')

    def test_time_for_other_case_insensitive(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('other!user@example.com'),
                    '#test',
                    ['.settz America/Chicago']
                )
        )
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.time OThER']
                )
        )

        response = self.bot.say.call_args[0][1]
        assert response.startswith('Current time in America/Chicago is: ')

    def test_time_for_other_not_found(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.time other']
                )
        )

        self.bot.reply_to.assert_called_with(
                NickMask('test!user@example.com'),
                '#test',
                "I don't know other's timezone."
        )

    def test_time_in_tz(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.time America/New_York']
                )
        )

        response = self.bot.say.call_args[0][1]
        assert response.startswith('Current time in America/New_York is: ')

    def test_time_in_tz_utc(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.time UTC']
                )
        )

        response = self.bot.say.call_args[0][1]
        assert response.startswith('Current time in UTC is: ')

    def test_time_in_tz_not_found(self):
        self.bot.on_pubmsg(
                None,
                Event(
                    'pubmsg',
                    NickMask('test!user@example.com'),
                    '#test',
                    ['.time NotA/Timezone']
                )
        )

        self.bot.reply_to.assert_called_with(
                NickMask('test!user@example.com'),
                '#test',
                "I don't know about that timezone."
        )
