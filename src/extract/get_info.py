from utils import sanitize_str


def parse_lgonbox(tag):
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


def get_user_info(soup):
    trs = soup.find_all('tr', class_='arow')
    keys = ['Law School', 'Status', 'Type', '$$$', 'Sent',
            'Received', 'Complete', 'Decision', 'Updated']
    application_information = {k: [] for k in keys}
    urls = []
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) == 0:
            continue
        tds = tds[-len(keys):]
        for i, key in enumerate(keys):
            application_information[key].append(tds[i].get_text())
        url = tds[0].find_all('a')[0].get('href')
        urls.append(url)
    result = {'application': application_information}

    text_blocks = soup.find_all('div', {'class': 'lft-content-show'})
    for block in text_blocks[:4]:
        title = block.find_all('h2')[0].text.lower()
        title = '_'.join(title.split())
        content = parse_lgonbox(block)
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
    return result, urls


def get_search_info(soup):
    table = soup.find_all('tbody')
    trs = table[0].find_all('tr')
    keys = ['User Name', 'LSAT', 'GPA', 'Last Updated']
    search_profiles = {k: [] for k in keys}
    urls = []
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) == 0:
            continue
        for i, key in enumerate(keys):
            search_profiles[key].append(tds[i].get_text())
        url = tds[0].find_all('a')[0].get('href')
        urls.append(url)
    return {'profiles': search_profiles}, urls


def get_school_info(soup):
    return {}, []


def get_info(category, soup):
    handler_lookup = {'school': get_school_info, 'search': get_search_info, 'user': get_user_info}
    return handler_lookup[category](soup)
