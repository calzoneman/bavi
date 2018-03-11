import irc.bot
import irc.connection
import logging
import re
import sqlite3
import ssl

from .module_loader import load_modules

log = logging.getLogger('bavi')
log.setLevel(logging.INFO)

# TODO: look into whether setting lenient decoder is necessary
# to avoid crashes on badly-encoded messages

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, config):
        self.config = config

        self._command_prefix = '.' # TODO: configurable
        self._commands = {}
        self._matchers = []

    def init_irc(self):
        irc_config = self.config['irc']
        spec = irc.bot.ServerSpec(
                irc_config.get('ServerHost'),
                int(irc_config.get('ServerPort')),
                irc_config.get('ServerPassword')
        )

        additional_args = {}

        if irc_config.getboolean('SSL'):
            additional_args['connect_factory'] = irc.connection.Factory(
                    wrapper=ssl.wrap_socket
            )

        nick = irc_config.get('Nickname')

        irc.bot.SingleServerIRCBot.__init__(
                self,
                [spec],
                nick,
                nick,
                **additional_args
        )

        log.info(
                'Connecting to %s:%d using nick %s',
                spec.host,
                spec.port,
                nick
        )

    def init_db(self):
        db_config = self.config['sqlite3']
        self.db = sqlite3.connect(db_config.get('Filename'))

    def _addressed_to_me(self, msg):
        name = self.connection.get_nickname()

        return msg.startswith(name + ': ') or msg.startswith(name + ', ')

    def _sanitize(self, message):
        '''
        Sanitize a message according to RFC 1459 by removing
        NUL, CR, and LF characters
        '''

        return ''.join(
                ch for ch in message if ch not in {'\r', '\n', '\0'}
        )

    def reply_to(self, source, target, message):
        '''
        Reply to a message originator by name.

        Sends a message target formatted as "nick: message" to target
        '''

        if target not in self.channels:
            raise KeyError(target)

        message = self._sanitize(message)
        # TODO: log outbound message to chat log
        self.connection.privmsg(target, '{}: {}'.format(source.nick, message))

    def say(self, target, message):
        '''
        Send a message to the given target
        '''

        if target not in self.channels:
            raise KeyError(target)

        message = self._sanitize(message)
        # TODO: log outbound message to chat log
        self.connection.privmsg(target, message)

    def add_command(self, cmd, handler, aliases=[]):
        '''
        Register a command
        '''
        for trigger in [cmd] + aliases:
            if trigger in self._commands:
                raise RuntimeError('Command "{}" is already registered'.format(
                    trigger
                ))

        for trigger in [cmd] + aliases:
            self._commands[trigger] = handler

    def add_matcher(self, regex, handler, priority='low'):
        if priority not in { 'low', 'medium', 'high' }:
            raise ValueError('priority must be low, medium, or high')

        if type(regex) != type(re.compile('')):
            raise TypeError('regex argument must be a compiled regex')

        if priority == 'low':
            self._matchers.append((regex, handler))
        elif priority == 'high':
            self._matchers = [(regex, handler)] + self._matchers
        else:
            idx = len(self._matchers)//2
            self._matchers = (
                    self._matchers[:idx] +
                    [(regex, handler)] +
                    self._matchers[idx:]
            )

    def _dispatch_command(self, event, cmd, message):
        if cmd not in self._commands:
            self.reply_to(
                    event.source,
                    event.target,
                    "I don't know about that command."
            )
            return

        try:
            self._commands[cmd](
                    self,
                    event.source,
                    event.target,
                    message,
                    command=cmd
            )
        except BaseException as e:
            exception_msg = type(e).__name__ + ': ' + str(e)
            log.exception('Command "%s" failed', cmd)
            self.say(event.target, exception_msg)

    def _dispatch_matcher(self, event, message):
        for regex, handler in self._matchers:
            match = regex.search(message)
            if match:
                log.debug('Matched pattern: %s', regex.pattern)
                try:
                    handler(
                            self,
                            event.source,
                            event.target,
                            message,
                            match=match
                    )
                except BaseException as e:
                    exception_msg = type(e).__name__ + ': ' + str(e)
                    log.exception('Message handler failed')
                    self.say(event.target, exception_msg)
                finally:
                    return

    def on_welcome(self, conn, event):
        for chan in self.config.get('irc', 'Channels').split(','):
            log.info('Joining channel %s', chan.strip())
            conn.join(chan.strip())

    def on_pubmsg(self, conn, event):
        # TODO: log the message to a chat log file
        try:
            msg = event.arguments[0].strip()

            if msg.startswith(self._command_prefix):
                # Syntax: ".command", "!command", etc.
                if ' ' in msg:
                    cmd, rest = msg.split(' ', 1)
                else:
                    cmd, rest = msg, ''
                cmd = cmd[len(self._command_prefix):]
                self._dispatch_command(event, cmd, rest)
                return
            elif self._addressed_to_me(msg):
                # Syntax: "Bot: command"
                _, rest = msg.split(' ', 1)
                if ' ' in rest:
                    cmd, rest = rest.split(' ', 1)
                else:
                    cmd, rest = rest, ''
                self._dispatch_command(event, cmd, rest)
                return
            else:
                self._dispatch_matcher(event, msg)
        except BaseException as e:
            log.exception('Failed to process pubmsg event "%s"', str(event))

    def on_privmsg(self, conn, event):
        # TODO: support private messages
        pass
