import unittest
import mock
from unittest.mock import MagicMock
from unittest.mock import Mock
import chardet

from requests.models import Response

from irc.client import Event, NickMask

import bavi.bot
import bavi.modules.url as url_module


class Dummy:
    pass


valid_urls = [
    'http://google.com',
    'https://google.com',
    'http://www.google.com',
    'https://www.google.com',
    'https://flab.tech:443',
    'https://shitty.vodka',
    'http://www.crowneprince.horse/',
    'https://sub.domain.horse',
    'http://123.12.33.42',
    'http://123.12.33.42:80',
    'http://123.12.33.42:80/homasd/asdfgwe',
    'https://en.wikipedia.org/wiki/Harry_Potter_and_the_Philosopher%27s_Stone',
    'https://ja.wikipedia.org/wiki/%E4%BB%BB%E5%A4%A9%E5%A0%82',
    'https://implyingrigged.info/wiki//mlp/',
    'http://asdf.com/testjpg:large'
    'http://asdf.com/testflac',
]

invalid_urls = [
    '',
    'google.com',
    'www.google.com',
    'ftp://asdf.org',
    'http://192.168.1.11/',
    'http://10.2.33.23:80',
    '12.33.23.23:80',
    'http://172.16.32.11',
    'asdf.aqwet3awr',
    'https://tnDX47P7VAMzEIn.ZEnLb',
    'http://cKDcNsfi.nOQ2wlJWm7.g9',
    'http://asdf.com/test.jpg',
    'http://asdf.com/test.jpg:large',
    'http://asdf.com/test.png',
    'http://asdf.com/test.gif',
    'http://asdf.com/test.bmp',
    'http://asdf.com/test.tiff',
    'http://asdf.com/test.psd',
    'http://asdf.com/test.mp4',
    'http://asdf.com/test.mkv',
    'http://asdf.com/test.avi',
    'http://asdf.com/test.mov',
    'http://asdf.com/test.mpg',
    'http://asdf.com/test.vob',
    'http://asdf.com/test.mp3',
    'http://asdf.com/test.aac',
    'http://asdf.com/test.wav',
    'http://asdf.com/test.flac',
    'http://asdf.com/test.ogg',
    'http://asdf.com/test.mka',
    'http://asdf.com/test.wma',
    'http://asdf.com/test.zip',
    'http://asdf.com/test.rar',
    'http://asdf.com/test.7z',
    'http://asdf.com/test.tar',
    'http://asdf.com/test.iso',
    'http://asdf.com/test.exe',
    'http://asdf.com/test.dll',
]

example_pages = [
    ('http://cyzon.us/', 'Index - calzoneman.net',
     'cyzon.us'), ('http://dinsfire.com', 'DinsFire64', 'dinsfire.com'),
    ('https://ja.wikipedia.org/wiki/%E3%83%9E%E3%82%A4%E3%83%'
     'AA%E3%83%88%E3%83%AB%E3%83%9D%E3%83%8B%E3%83%BC%E3%80%9C'
     '%E3%83%88%E3%83%A2%E3%83%80%E3%83%81%E3%81%AF%E9%AD%94%E6%B3%95%E3%80%9C',
     'マイリトルポニー〜トモダチは魔法〜 - Wikipedia', 'ja.wikipedia.org'),
    ('https://ko.wikipedia.org/wiki/%ED%8E%8C%ED%94%84_%EC%9E%87_%EC%97%85',
     '펌프 잇 업 - 위키백과, 우리 모두의 백과사전', 'ko.wikipedia.org'),
    ('https://zh.wikipedia.org/wiki/%E4%B8%89%E6%98%9F%E9%9B%86%E5%9B%A2',
     '三星集团 - 维基百科，自由的百科全书',
     'zh.wikipedia.org'), ('http://xn--yt8h.ws/',
                           '📙 Emojipedia — 😃 Home of Emoji Meanings 💁👌🎍😍',
                           'xn--yt8h.ws')
]


def fake_get(page_title):
    response = Mock()
    data = u'<html><head><title>{0}</title></head></html>'.format(
        page_title).encode('utf-8')

    def iter_content(chunk_size=128):
        rest = data

        while rest:
            chunk = rest[:chunk_size]
            rest = rest[chunk_size:]
            yield chunk

    def open(var):
        return response

    def close(var, var2, var3, var4):
        return True

    response.headers = {'content-length': str(len(data))}
    response.iter_content = iter_content
    response.__enter__ = open
    response.__exit__ = close

    return response


class URLModuleTestCase(unittest.TestCase):
    def setUp(self):
        self.bot = bavi.bot.Bot(None)
        self.bot.connection = Dummy()
        self.bot.connection.get_nickname = lambda: 'TestBot'
        url_module.init(self.bot)
        self.bot.say = MagicMock()
        self.bot.reply_to = MagicMock()

    def test_url_valid_urls(self):
        empty_list = []

        for url in valid_urls:
            self.assertEqual(url_module.get_valid_urls(url), [url])

        for url in invalid_urls:
            self.assertEqual(url_module.get_valid_urls(url), empty_list)

    def test_url_full_query_stack(self):
        for url, title, hostname in example_pages:

            with mock.patch(
                    'bavi.modules.url.requests.get',
                    return_value=fake_get(title)):
                self.assertEqual(
                    url_module.get_user_readable_response(url),
                    url_module.TITLE_FORMAT.format(title, hostname))

    def test_url_command_trigger(self):

        with mock.patch(
                'bavi.modules.url.requests.get',
                return_value=fake_get("sample page")):
            self.bot.on_pubmsg(None,
                               Event('pubmsg',
                                     NickMask('test!user@example.com'),
                                     '#test', ['.title http://example.com']))

            self.bot.say.assert_called_with('#test',
                                            '[ sample page ] - example.com')

    def test_url_match_trigger(self):
        with mock.patch(
                'bavi.modules.url.requests.get',
                return_value=fake_get("only the shittiest")):
            self.bot.on_pubmsg(None,
                               Event('pubmsg',
                                     NickMask('user!ident@host'), '#test',
                                     ['http://shitty.vodka']))

            self.bot.say.assert_called_with(
                '#test', '[ only the shittiest ] - shitty.vodka')

    def test_multiple_url_match_trigger(self):

        with mock.patch(
                'bavi.modules.url.requests.get',
                side_effect=[
                    fake_get("first webpage"),
                    fake_get("second webpage")
                ]):
            self.bot.on_pubmsg(
                None,
                Event('pubmsg',
                      NickMask('user!ident@host'), '#test',
                      ['http://first.web.site http://second.web.io']))

            self.bot.say.assert_has_calls(
                [
                    mock.call('#test', '[ first webpage ] - first.web.site'),
                    mock.call('#test', '[ second webpage ] - second.web.io')
                ],
                any_order=False)
