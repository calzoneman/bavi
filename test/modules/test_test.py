import unittest
from unittest.mock import MagicMock

from test.helpers import PubmsgEvent

import bavi.bot
import bavi.modules.test as test_module

class TestModuleTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = bavi.bot.Bot(None)
        test_module.init(self.bot)
        self.bot.say = MagicMock()

    def test_execute_command(self):
        self.bot.on_pubmsg(
                None,
                PubmsgEvent(
                    'test!user@example.com',
                    '#test',
                    ['.test 1 2 3']
                )
        )
        self.bot.say.assert_called_with(
                '#test',
                'The test result is: 1'
        )
