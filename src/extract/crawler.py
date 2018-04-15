import os
import sys
from collections import deque
from utils import tokenize
from html_to_json import html_to_json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from StopWatch import StopWatch


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
    for i, n in enumerate(num_pages):
        for p in range(n):
            url_list.append(url_template.format(i + 1, p + 1))
    q = deque(url_list)
    visited = set(url_list)
    sw = StopWatch()
    count = 0
    while q:
        url = q.popleft()
        count += 1
        if count % 100 == 0:
            category, name = tokenize(url)
            print '{}, crawling {}, name = {}, len(q) = {}'.format(count, category, name, len(q))
        to_crawl = html_to_json(url)
        if to_crawl is None:
            visited.add(url)
        else:
            for child_url in to_crawl:
                if child_url not in visited:
                    visited.add(child_url)
                    q.append(child_url)
        if count > 70000:
            with open('timeout.txt', 'wb') as fp:
                fp.write('\n'.join(list(q)))
            break
    sw.tic('crawl {} urls'.format(count))


if __name__ == '__main__':
    crawl()
