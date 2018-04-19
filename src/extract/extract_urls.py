from bs4 import BeautifulSoup


def _find_urls_from_trs(trs):
    result = []
    for tr in trs:
        tds = tr.find_all('td')
        if tds:
            links = tds[0].find_all('a')
            if links:
                url = links[0].get('href')
                result.append(url)
    return result


def _extract_urls_from_user(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    trs = soup.find_all('tr', class_='arow')
    return _find_urls_from_trs(trs)


def _extract_urls_from_search(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    table = soup.find_all('tbody')
    trs = table[0].find_all('tr')
    return _find_urls_from_trs(trs)


def _extract_urls_from_school(html_doc):
    return []


def extract_urls(category, html_doc):
    handler_lookup = {'school': _extract_urls_from_school,
                      'search': _extract_urls_from_search,
                      'user': _extract_urls_from_user}
    return handler_lookup[category](html_doc)
