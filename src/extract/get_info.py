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
    return {'application': application_information}, urls


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
