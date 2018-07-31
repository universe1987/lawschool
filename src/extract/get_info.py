from utils import sanitize_str
from bs4 import BeautifulSoup


def _parse_lgonbox(tag):
    entries = tag.find_all('div', {'class': 'lgonbox1 divalign'})
    result = {}
    for entry in entries:
        key = entry.find_all('label')
        if not key:
            continue
        key = sanitize_str(key[0].text, ' \n*', ' \n:')
        val = entry.find_all('div', {'class': 'view_field'})
        if val:
            result[key] = val[0].text.strip()
    return result


def _get_user_info(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    trs = soup.find_all('tr', class_='arow')
    keys = ['Law School', 'Status', 'Type', '$$$', 'Sent',
            'Received', 'Complete', 'Decision', 'Updated']
    application_information = {k: [] for k in keys}
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) == 0:
            continue
        tds = tds[-len(keys):]
        for i, key in enumerate(keys):
            application_information[key].append(tds[i].get_text())
    result = {'application': application_information}
    # extract information outside of the table
    text_blocks = soup.find_all('div', {'class': 'lft-content-show'})
    for block in text_blocks[:4]:
        title = block.find_all('h2')[0].text.lower()
        title = '_'.join(title.split())
        content = _parse_lgonbox(block)
        if not content:
            try:
                text = block.find_all('div', {'class': 'view_field'})
                if text:
                    content['text'] = text[0].text.strip()
            except:
                print '-' * 40
                print block
                import pdb
                pdb.set_trace()
        result[title] = content
    return result


def _get_search_info(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    table = soup.find_all('tbody')
    trs = table[0].find_all('tr')
    keys = ['User Name', 'LSAT', 'GPA', 'Last Updated']
    search_profiles = {k: [] for k in keys}
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) == 0:
            continue
        for i, key in enumerate(keys):
            search_profiles[key].append(tds[i].get_text())
    return {'profiles': search_profiles}


def _get_school_info(html_doc):
    soup = BeautifulSoup(html_doc, 'html.parser')
    early_decision = soup.find_all('p', {'class': 'important_dates div_left'})
    result = {}
    if early_decision:
        content = [line.strip() for line in early_decision[0].get_text().split('\n')]
        content = [line for line in content if line]
        for line in content:
            key, val = line.split(':')
            result[key.strip()] = val.strip()
    return {'important_dates': result}


def get_info(category, html_doc):
    handler_lookup = {'school': _get_school_info, 'search': _get_search_info, 'user': _get_user_info}
    return handler_lookup[category](html_doc)
