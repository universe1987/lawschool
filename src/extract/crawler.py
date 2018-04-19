import os
import sys
from collections import deque
from utils import tokenize
from utils import get_html
from extract_urls import extract_urls

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from StopWatch import StopWatch


def _download_and_get_children(url):
    result = tokenize(url)
    if result is None:
        return
    category, name = result
    uid = '{}_{}'.format(category, name)
    html_doc, retry_count = get_html(url, uid)
    if html_doc is None:
        print '  fail to get', url
        return
    return extract_urls(category, html_doc)


def crawl():
    url_template = 'http://search.lawschoolnumbers.com/users/profiles?' \
                   'utf8=true&' \
                   'cycle_id={}&' \
                   'searchLSAT=true&' \
                   'blanksLSAT=true&' \
                   'LSAT_Slider_val=120+-+180&' \
                   'searchLGPA=true&' \
                   'blanksLGPA=true&' \
                   'LGPA_Slider_val=1.00+-+4.33&' \
                   'searchDGPA=true&' \
                   'blanksDGPA=true&' \
                   'DGPA_Slider_val=1.00+-+4.33&' \
                   'school_type_s=Any&' \
                   'school_type=&' \
                   'major_s=Any&' \
                   'major=&' \
                   'state%5Bstate_s%5D=Any&' \
                   'location_s=Any&' \
                   'location=&' \
                   'race_s=Any&' \
                   'race=&' \
                   'sex=Any&' \
                   'international=Included&' \
                   'urm=Included&' \
                   'nontr=Included&' \
                   'mlast=Included&' \
                   'commit=Search+Applicants&' \
                   'page={}'
    num_pages = [65, 120, 141, 149, 201, 126, 100, 70, 58, 52, 34, 40, 22, 28, 31, 1]
    url_list = []
    cycle_id = 0
    for max_page in num_pages:
        cycle_id += 1
        for page_num in range(1, max_page + 1):
            url_list.append(url_template.format(cycle_id, page_num))
    task_queue = deque(url_list)
    task_set = set(url_list)
    stop_watch = StopWatch()
    count = 0
    while task_queue:
        url = task_queue.popleft()
        count += 1
        if count % 100 == 0:
            tokens = tokenize(url)
            if tokens is not None:
                category, name = tokenize(url)
                print '{}, crawling {}, name = {}, len(q) = {}'.format(count, category, name, len(task_queue))
        to_crawl = _download_and_get_children(url)
        if to_crawl is not None:
            for child_url in to_crawl:
                if child_url not in task_set:
                    task_set.add(child_url)
                    task_queue.append(child_url)
        if count > 70000:
            with open('timeout.txt', 'wb') as fp:
                fp.write('\n'.join(list(task_queue)))
            break
    stop_watch.tic('crawl {} urls'.format(count))


if __name__ == '__main__':
    crawl()
