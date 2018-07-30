import re
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR

from StopWatch import StopWatch

def select_application_tables():
    user_applications = glob('{}/user_*'.format(JSON_DIR))
    folder_len = len(JSON_DIR)
    user_names = ['_'.join(s[folder_len:].split('_')[1:-1]) for s in user_applications]
    sw = StopWatch()
    print len(user_applications)
    
    list = []
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
                list.append(line)
    df=pd.DataFrame(list,columns=['User Name','Status','Received','Last Updated','Complete','Law School',
                                  'Decision','Type','Sent','$$$'])
    sw.tic('generating all information')
    return df

   
def select_search_tables():
    search_results = glob('{}/search_*'.format(JSON_DIR))
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
    df = pd.DataFrame(data)
    sw.tic('generate search table')
    return df
                

def select_search_tables():
    search_results = glob('{}/search_*'.format(JSON_DIR))
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
    df = pd.DataFrame(data)
    df = df[['Last Updated','LSAT','GPA','Year','User Name']] 
    sw.tic('generate search table')
    return df


def select_user_tables():
    user_applications = glob('{}/user_*'.format(JSON_DIR))
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
    user_applications = glob('{}/user_*'.format(JSON_DIR))
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


def filter_good_applicants(df, col, threshold):
    return df[df[col] > threshold]


if __name__ == '__main__':
    df = select_application_tables()
    print df.head()
    print df.tail()
    print len(df)
    df.to_csv('all.csv')
    df_all = pd.read_csv('all.csv')
    print ("finished assembling dataset")
    
    df = select_search_tables()
    df['User Name'] = df['User Name'].str.encode('utf8', 'replace').str.strip(' N').str.strip(' UN')
    print df.head()
    print df.tail()
    print len(df)
    df.to_csv('user.csv')
    df_search = pd.read_csv('user.csv')
    print ("finished user basic characteristics")
    
    df = df_all.merge(df_search,on=['User Name'],how='left').reset_index()
    print df['User Name'].nunique()
    df = df_all.merge(df_search,on=['User Name'],how='right').reset_index()
    print df['User Name'].nunique()
    df = df_all.merge(df_search,on=['User Name'],how='outer').reset_index()
    print df['User Name'].nunique()
    df = df_all.merge(df_search,on=['User Name'],how='inner').reset_index()
    print df['User Name'].nunique()
    # There are 1445 unique users in df_all but not in df_search

    for yr in range(2003,2017):
         df_yr = df[df['Year'] == yr]
         print df_yr['User Name'].nunique(), yr
         df_received = df[df['Received'].str.contains('/')]
         df_received = df_received[df_received['Year'] == yr]
         print df_received['User Name'].nunique(), yr
    

    '''
    user_names, user_stats = select_user_tables()
    df = pd.DataFrame(user_stats, index=user_names, columns=['Complete', 'Decision', 'Received', 'Sent'])
    df = filter_good_applicants(df, 'Complete', 0)
    print len(df)
    df = filter_good_applicants(df, 'Decision', 0)
    print len(df)
    df = filter_good_applicants(df, 'Sent', 0)
    print len(df)
    df = filter_good_applicants(df, 'Received', 0)
    print len(df)
    '''
