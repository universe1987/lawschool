import json
from bs4 import BeautifulSoup
from utils import get_html
from utils import tokenize
from get_info import get_info
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR


def html_to_json(url):
    result = tokenize(url)
    if result is None:
        return
    category, name = result
    uid = '{}_{}'.format(category, name)
    html_doc, retry_count = get_html(url, uid)
    if html_doc is None:
        print '  fail to get', url
        return
    soup = BeautifulSoup(html_doc, 'html.parser')
    data, urls = get_info(category, soup)
    for key, val in data.iteritems():
        with open(os.path.join(JSON_DIR, '{}_{}.json'.format(uid, key)), 'wb') as fp:
            json.dump(val, fp)
    return urls
