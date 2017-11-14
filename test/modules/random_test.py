import sqlite3
import unittest
from unittest.mock import MagicMock
import unittest.mock as mock
import random

from irc.client import Event, NickMask

import bavi.bot
import bavi.modules.random as random_module


class RandomModuleTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = bavi.bot.Bot(None)
        random_module.init(self.bot)
        self.bot.say = MagicMock()
        self.bot.reply_to = MagicMock()

    def test_random_make_list(self):
        commas = random_module.make_list('1,2,3,4,5,6,7,8,9,0')
        bar = random_module.make_list('a|b|c|d|e')
        forward_slash = random_module.make_list('b/d/e/f/g')
        back_slash = random_module.make_list('q\\v\\e\\3\\f\\b\\g\\g')
        mixed = random_module.make_list('q,v,e\\3\\f\\b,g\\g\\a|b|c|d|e')
        nothing = random_module.make_list('')

        self.assertEqual(len(commas), 10)
        self.assertEqual(len(bar), 5)
        self.assertEqual(len(forward_slash), 5)
        self.assertEqual(len(back_slash), 8)
        self.assertEqual(len(mixed), 4)
        self.assertEqual(len(nothing), 1)

        self.assertEqual(commas[0], '1')
        self.assertEqual(mixed[2], 'e\\3\\f\\b')
        self.assertEqual(nothing[0], '')

    def test_random_normal(self):
        with mock.patch(
                'bavi.modules.random.choice', return_value=4) as mock_random:
            self.bot.on_pubmsg(None,
                               Event('pubmsg',
                                     NickMask('user!ident@host'), '#test',
                                     ['.choose 1,2,3,4,5']))

            self.bot.reply_to.assert_called_with(
                NickMask('user!ident@host'), '#test',
                'Your choices: [\'1\', \'2\', \'3\', \'4\', \'5\'], I chose: 4.'
            )

    def test_random_pick(self):
        with mock.patch(
                'bavi.modules.random.choice', return_value='g') as mock_random:
            self.bot.on_pubmsg(None,
                               Event('pubmsg',
                                     NickMask('user!ident@host'), '#test',
                                     ['.pick a|b|c|d|e|f|g']))

            self.bot.reply_to.assert_called_with(
                NickMask('user!ident@host'), '#test',
                'Your choices: [\'a\', \'b\', \'c\', \'d\','
                ' \'e\', \'f\', \'g\'], I chose: g.')

    def test_random_trailing_whitespace(self):
        with mock.patch(
                'bavi.modules.random.choice',
                return_value='blue fish') as mock_random:
            self.bot.on_pubmsg(
                None,
                Event('pubmsg',
                      NickMask('user!ident@host'), '#test',
                      ['.pick one fish, two fish, red fish, blue fish']))

            self.bot.reply_to.assert_called_with(
                NickMask('user!ident@host'), '#test',
                'Your choices: [\'one fish\', \'two fish\','
                ' \'red fish\', \'blue fish\'], I chose: blue fish.')
