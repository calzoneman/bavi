import irc.bot
import irc.connection
import logging
import ssl

from .module_loader import load_modules

log = logging.getLogger('bavi')
log.setLevel(logging.INFO)

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, config):
        self.config = config

        self._init_irc(config['irc'])
        self._init_modules()

    def _init_irc(self, irc_config):
        spec = irc.bot.ServerSpec(
                irc_config.get('ServerHost'),
                int(irc_config.get('ServerPort')),
                irc_config.get('ServerPassword')
        )

        log.info('Connecting to %s:%d', spec.host, spec.port)

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

    def _init_modules(self):
        load_modules(self)

    def on_welcome(self, conn, event):
        for chan in self.config.get('irc', 'Channels').split(','):
            log.info('Joining channel %s', chan.strip())
            conn.join(chan.strip())
