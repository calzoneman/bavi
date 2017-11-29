import logging
import requests
import urllib3.exceptions
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re

log = logging.getLogger('bavi.modules.url')

URL_REGEX = r'(https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=\u263a-\U0001f645]{1,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*))'

IP_REGEX = r"(https?:\/\/([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))(?<!127)(?<!10)(?<!0)\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!192\.168)(?<!172\.(16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31))\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])(?<!\.255$)([-a-zA-Z0-9@:%_\+.~#?&//=]*))"

IGNORE_REGEX = r'(?i)\.(jpg|jpg:large|png|gif|bmp|tiff|psd|mp4|mkv|avi|mov|mpg|vob|mp3|aac|wav|flac|ogg|mka|wma|zip|rar|7z|tar|iso|exe|dll|cfg|rc|reg|pxe|efi)$'

compiled_url_regex = re.compile(URL_REGEX, re.UNICODE)
compiled_ip_regex = re.compile(IP_REGEX)
compiled_ignore_regex = re.compile(IGNORE_REGEX)

TITLE_FORMAT = '[ {0} ] - {1}'


def init(bot):
    bot.add_command('title', title_command)
    bot.add_matcher(compiled_url_regex, title_command, priority='low')
    bot.add_matcher(compiled_ip_regex, title_command, priority='low')


def title_command(bot, source, target, message, **kwargs):
    log.debug('url module triggered on: ' + message)

    if len(message) > 0:
        valid_urls = get_valid_urls(message)

        #limiting to a maximum of 5 URLs in one request
        for url in valid_urls[:5]:

            try:
                response = get_user_readable_response(url)

                if len(response) > 0:
                    bot.say(target, response)

            except requests.exceptions.Timeout:
                bot.say(target, 'Server for \'{0}\' timed out.'.format(url))
                pass

            except requests.exceptions.TooManyRedirects:
                bot.say(target,
                        'URL \'{0}\' had too many redirects.'.format(url))
                pass

            except requests.exceptions.HTTPError:
                bot.say(target,
                        'An HTTP error occured for URL \'{0}\''.format(url))
                pass

            except requests.exceptions.ConnectionError as e:

                exception_msg = type(e).__name__ + ': ' + str(e)
                log.debug('ConnectionError for url: %s. %s', url,
                          exception_msg)

                #for some dumb reason,
                #requests sometimes passes through urllib3 exceptions
                #so here we are.
                if type(e.args[0]) is urllib3.exceptions.MaxRetryError:
                    bot.say(
                        target,
                        'Exceeded maximum retries to connect to URL \'{0}\''.
                        format(url))
                elif type(e.args[0]) is urllib3.exceptions.ProtocolError:
                    reason = e.args[0].args[0].replace('.', '')
                    bot.say(target, '{0} for URL \'{1}\''.format(reason, url))
                else:
                    bot.say(target,
                            'A connection error error occured for URL \'{0}\''.
                            format(url))
                pass

            except Exception as e:
                exception_msg = type(e).__name__ + ': ' + str(e)
                log.exception('Could not get title from url: %s. %s', url,
                              exception_msg)
                bot.say(target, exception_msg)


def get_user_readable_response(url):
    response = ''

    if len(url) > 0:
        #now start a request for the page title
        title = get_http_title(url)

        if (len(title) > 0):
            response = TITLE_FORMAT.format(title, get_domain_from_url(url))

    return response


def get_valid_urls(string_statement):
    valid_matches = []
    valid_urls = []

    valid_matches += re.findall(compiled_url_regex, string_statement)
    valid_matches += re.findall(compiled_ip_regex, string_statement)

    log.debug(valid_matches)

    for match in valid_matches:
        if compiled_ignore_regex.search(match[0]) is None:
            valid_urls.append(match[0])

    log.debug('Found: ' + ', '.join(str(url) for url in valid_urls))

    return valid_urls


def get_http_title(url):
    log.debug('Requesting url %s', url)

    #TODO: Possibly bring these parameters to user defined setting.
    #Currently set to first 512KBytes from server and timeout at 5s
    headers = {"Range": "bytes=0-512000"}

    page = b''

    #use `with` to make sure the connection goes back into the pool
    with requests.get(url, headers=headers, timeout=5, stream=True) as r:
        for chunk in r.iter_content(chunk_size=128):
            page += chunk

            #don't let it download a huge page or anything past the title
            if b'</title>' in page or len(page) > 512000:
                break

    bs = BeautifulSoup(page, 'html.parser')

    return bs.find('title').string


def get_domain_from_url(url):
    domain = ''

    try:
        domain = urlparse(url).netloc
    except:
        log.debug('Could not get domain from: %s', url)

    return domain
