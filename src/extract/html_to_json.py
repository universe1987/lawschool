from get_info import get_info
from glob import glob
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, HTML_DIR
from StopWatch import StopWatch


def html_to_json(filename):
    with open(filename, 'rb') as fp:
        html_doc = fp.read()
    category, name = os.path.basename(filename).split('.')[0].split('_', 1)
    data = get_info(category, html_doc)
    uid = '{}_{}'.format(category, name)
    for key, val in data.iteritems():
        with open(os.path.join(JSON_DIR, '{}_{}.json'.format(uid, key)), 'wb') as fp:
            json.dump(val, fp)


if __name__ == '__main__':
    html_files = glob(os.path.join(HTML_DIR, 'search_*.html'))\
                 + glob(os.path.join(HTML_DIR, 'user_*.html'))\
                 + glob(os.path.join(HTML_DIR, 'school_*.html'))
    print len(html_files)
    stop_watch = StopWatch()
    for i, filename in enumerate(html_files):
        html_to_json(filename)
        if i % 100 == 0: 
            print i, filename
    stop_watch.tic('converted {} html documents to json'.format(len(html_files)))
