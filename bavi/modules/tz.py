import datetime
import pytz

import irc.strings

from bavi.db_util import create_audit_trigger

def init(bot):
    bot.add_command('settz', set_tz)
    bot.add_command('time', time)

    c = bot.db.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS tz_info (
                nick TEXT,
                tz TEXT,
                created_at DATETIME,
                updated_at DATETIME,
                PRIMARY KEY (nick)
            )
    ''')

    create_audit_trigger(c, 'tz_info', 'nick')

def set_tz(bot, source, target, message, **kwargs):
    '''
    .settz: Set your timezone for usage with .time

    Usage:
      .settz America/Los_Angeles    Set your timezone to America/Los_Angeles
    '''

    tz = message.strip()
    nick = irc.strings.lower(source.nick)

    if len(tz) == 0:
        bot.reply_to(
                source,
                target,
                'Give me a timezone, for example .settz America/Los_Angeles'
        )
        return

    if tz not in pytz.all_timezones_set:
        bot.reply_to(
                source,
                target,
                "I don't know about that timezone"
        )
        return

    c = bot.db.cursor()
    now = datetime.datetime.now()

    c.execute('''
            UPDATE tz_info
               SET tz = ?
             WHERE nick = ?
    ''', (tz, nick))

    if c.rowcount == 0:
        c.execute('''
                INSERT INTO tz_info (nick, tz) VALUES (
                    ?,
                    ?
                )
        ''', (nick, tz))

    bot.db.commit()

    bot.reply_to(
            source,
            target,
            'Your timezone has been set to {}'.format(tz)
    )

def time(bot, source, target, message, **kwargs):
    '''
    .time: Print the current time in the given user's timezone.

    Usage:
      .time                        retrieve the time in your timezone
      .time user                   retrieve the time in user's timezone
      .time America/Los_Angeles    retrieve the time in the America/Los_Angeles
                                   timezone
    '''

    if len(message.strip()) > 0:
        arg = message.strip()
    else:
        arg = source.nick

    if '/' in arg or arg in pytz.all_timezones_set:
        # '/' is not a valid nickname character; assume the argument is
        # a timezone, e.g. ".time America/Los_Angeles"
        if arg in pytz.all_timezones_set:
            tz = pytz.timezone(arg)
        else:
            bot.reply_to(source, target, "I don't know about that timezone.")
            return
    else:
        try:
            tz = tz_for_nick(bot, arg)
        except KeyError:
            bot.reply_to(
                    source,
                    target,
                    "I don't know {}'s timezone.".format(arg)
            )
            return

    now = tz.localize(datetime.datetime.now())

    bot.say(
            target,
            'Current time in {} is: {}'.format(
                tz,
                now.strftime('%Y-%m-%d %H:%M:%S %z')
            )
    )

def tz_for_nick(bot, nick):
    arg = irc.strings.lower(nick)
    c = bot.db.cursor()
    c.execute('''
            SELECT tz
              FROM tz_info
             WHERE nick = ?
    ''', (arg,))

    results = [tz for tz, in c]

    if len(results) == 0:
        raise KeyError('No timezone data found for {}'.format(nick))

    return pytz.timezone(results[0])
