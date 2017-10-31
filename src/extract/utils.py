import requests
from time import sleep
import urlparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import HTML_DIR


def get_html(url, saveas, max_retry=5):
    local_cache = os.path.join(HTML_DIR, '{}.html'.format(saveas))
    if not os.path.exists(local_cache):
        retry_count = 0
        while True:
            retry_count += 1
            if retry_count > max_retry:
                return None, retry_count
            try:
                resp = requests.get(url, timeout=20 * (retry_count + 1))
            except Exception as e:
                print e
                continue
            if resp.status_code == 200:
                html_doc = resp.content
                with open(local_cache, 'wb') as fp:
                    fp.write(html_doc)
                return html_doc, retry_count
            sleep(3)
    else:
        with open(local_cache, 'rb') as fp:
            return fp.read(), 0


def is_valid_url(url):
    result = tokenize(url)
    return result is not None
    
def keep_ascii(s):
    ascii_part = [c for c in s if ord(c) < 128]
    x = ''.join(ascii_part).strip()
    return ' '.join(x.split())


def remove_special_char(s, special='"?*<>:|\\'):
    for c in special:
        s = s.replace(c, '')
    return s


def tokenize(url):
    parsed = urlparse.urlparse(url)
    if parsed.scheme != 'http':
        return
    host_name = parsed.hostname
    path_name = parsed.path.lstrip('/')
    if host_name == 'lawschoolnumbers.com':
        if path_name == '' or '/' in path_name:
            return
        user_name = path_name
        return 'user', remove_special_char(user_name)
    if host_name == 'search.lawschoolnumbers.com':
        query_parameters = urlparse.parse_qs(parsed.query)
        if 'cycle_id' not in query_parameters or 'page' not in query_parameters:
            return
        year = int(query_parameters['cycle_id'][0]) + 2002
        page = query_parameters['page'][0]
        search_name = '{}_{}'.format(year, page)
        return 'search', search_name
    if 'lawschoolnumbers.com' in host_name and path_name == '':
        return 'school', '_'.join(host_name.split('.')[:-2])
