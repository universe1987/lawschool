import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch

def select_application_tables():
    user_applications = glob(os.path.join(JSON_DIR, 'user_*_application.json'))
    folder_len = len(JSON_DIR)
    user_names = ['_'.join(s[folder_len:].split('_')[1:-1]) for s in user_applications]
    sw = StopWatch()
    print len(user_applications)
    
    lists = []
    for i, filename in enumerate(user_applications):
        if (i + 1) % 10000 == 0:
            print i
        with open(filename, 'rb') as fp:
            table = json.load(fp)
            n_applications = int(len(table['Sent']))
            if n_applications == 0:
                continue
            for j in range(n_applications):
                line = [user_names[i], table['Status'][j], table['Received'][j], table['Updated'][j],
                table['Complete'][j], table['Law School'][j],table['Decision'][j],table['Type'][j],
                table['Sent'][j],table['$$$'][j]]
                lists.append(line)
    df=pd.DataFrame(lists,columns=['User Name','Status','Received','Last Updated','Complete','Law School',
                                  'Decision','Type','Sent','$$$'])
    sw.tic('generating all information')
    return df

   
def select_search_tables():
    search_results = glob(os.path.join(JSON_DIR, 'search_*.json')) 
    folder_len = len(JSON_DIR)
    data = {'Last Updated': [],
            'LSAT': [],
            'GPA': [],
            'User Name': [],
            'Year': []}
    sw = StopWatch()
    for filename in search_results:
        year = filename[folder_len:].split('_')[1]
        with open(filename, 'rb') as fp:
            table = json.load(fp)
        for key in table:
            data[key] += table[key]
        data['Year'] += [year] * len(table['GPA'])
    data['User Name'] = [remove_special_char(s) for s in data['User Name']]
    df = pd.DataFrame(data)
    sw.tic('generate search table')
    return df
                

def select_user_tables():
    user_applications = glob(os.path.join(JSON_DIR, 'user_*_application.json')) 
    folder_len = len(JSON_DIR)
    user_names = ['_'.join(s[folder_len:].split('_')[1:-1]) for s in user_applications]
    user_stats = np.zeros((len(user_applications), 4))
    date_cols = ['Complete', 'Decision', 'Received', 'Sent']
    sw = StopWatch()
    print len(user_applications)
    for i, filename in enumerate(user_applications):
        if (i + 1) % 10000 == 0:
            print i
        with open(filename, 'rb') as fp:
            table = json.load(fp)
            n_applications = float(len(table['Sent']))
            if n_applications == 0:
                continue
            for j, col_name in enumerate(date_cols):
                has_date = len([s for s in table[col_name] if s != '--'])
                user_stats[i, j] = has_date / n_applications
    sw.tic('generating stats')
    return user_names, user_stats


def select_user_tables2():
    user_applications = glob(os.path.join(JSON_DIR, 'user_*_application.json'))
    user_names = ['_'.join(s.split('_')[1:-1]) for s in user_applications]
    user_stats = np.zeros((len(user_applications), 4))
    date_cols = ['Complete', 'Decision', 'Received', 'Sent']
    sw = StopWatch()
    for i, filename in enumerate(user_applications):
        df = pd.read_json(filename)
        if len(df) == 0:
            continue
        for s in date_cols:
            df[s + '_flag'] = df[s] != '--'
        flag_cols = [s + '_flag' for s in date_cols]
        stats = df[flag_cols].sum() / float(len(df))
        user_stats[i] = stats.values
    sw.tic('method 2')
    return user_names, user_stats


