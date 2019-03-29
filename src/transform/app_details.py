import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict
from scipy.stats.mstats import mode

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch


' Everything here is useless! Ignore everything on this py file.'

def app_state_var(df):
    df.to_csv('../../data/edit/qpig_dynamic_sample.csv')
    # predict future behaviors using state variables
    # number of offers - max/min/avg rank, max/min/avg response time
    # number of rejections - max/min/avg rank, max/min/avg response time
    # number of waitlists - max/min/avg rank, max/min/avg response time
    # number of unknowns - max/min/avg rank, max/min/avg waiting time
    # Days past since sep 1
    # Days past since last round of apps
    # Days past since first round of apps
    # each row corresponds to a round (date) and a user
    # weekday
    return

def app_state_var2():
    df = pd.read_csv('../../data/edit/outputs.csv')
    print df.head()
    df = df.groupby(['User Name','Application Time'])['Number of Offers','Number of Waiting List', 'Number of Rejections'].mean().reset_index()
    df_ind = df.groupby(['User Name'])['Number of Offers','Number of Waiting List', 'Number of Rejections'].max().reset_index()
    print df_ind.head(30)
    print len(df_ind)
    for x in ['Number of Offers']: #,'Number of Waiting List', 'Number of Rejections'
        print x, len(df_ind[df_ind[x]>0])
        print df_ind[df_ind[x]>0]['User Name'].unique()
    return

def app_indvdl(df):
    #========= Initialize Stat-Dataframes ===========#
    print df.columns.tolist()
    
    # By User Name
    df_user = df.groupby(['User Name'])['Sent_delta'].agg(['count','nunique']).reset_index()\
                .rename(columns={'count':'Total Apps','nunique':'Num Rounds'})
    
    # By User Name + App Rounds
    df_rd = df.groupby(['User Name','Sent_delta'])['Law School'].count().reset_index()\
                 .rename(columns={'Law School':'Num Apps per Round'})
    
    df['rank_2010_cp'] = pd.to_numeric(df['rank_2010_cp'])
    df_temp = df.groupby(['User Name','Sent_delta'])['rank_2010_cp'].mean().reset_index()\
                 .rename(columns={'rank_2010_cp':'Avg Ranks'})
    df_rd = df_rd.merge(df_temp,on=['User Name','Sent_delta'],how='left').reset_index()
    df_rd = df_rd.merge(df_user, on=['User Name'],how='left').reset_index()
    
    shifted = df_rd[['User Name','Sent_delta']].groupby(['User Name']).shift(1)
    df_rd = df_rd.join(shifted.rename(columns=lambda x: x+' Lead'))
    df_rd['Interval'] = df_rd['Sent_delta'] - df_rd['Sent_delta Lead'] 
    
    #========= Calculate Stats at Stat-DataFrames =======#
    df_rd_apps = df_rd.groupby(['User Name','Total Apps'])['Num Apps per Round'].agg(['min','max'])\
                .reset_index()
    for item in ['min','max']:
        df_rd_apps = df_rd_apps.rename(columns={'{}'.format(item):'{} Num Apps per Round'.format(item)})
        df_rd_apps['{} Pct Apps per Round'.format(item)] = df_rd_apps['{} Num Apps per Round'.format(item)]\
                /df_rd_apps['Total Apps']*100.0           
    
    df_rd_int = df_rd.groupby(['User Name'])['Interval'].agg(['max','min','median','mean']).reset_index()
    dic_rename = {'min':'Shortest Interval','max':'Longest Interval','median':'Median Interval','mean':'Avg Interval'}
    for key, value in dic_rename.items():
        df_rd_int = df_rd_int.rename(columns={key:value})
    
    df_days = df.groupby(['User Name'])['Sent_delta'].agg(['max','min','median','mean']).reset_index()
    df_days['Span'] = df_days['max'] - df_days['min']
    dic_rename = {'min':'Days 1st','max':'Days Last','median':'Days Median','mean':'Days Avg'}
    for key, value in dic_rename.items():
        df_days = df_days.rename(columns={key:value})
    
    #========= Merge and Finalize Stat-DataFrames ==================#
    df_user_stat = df_user.merge(df_rd_apps,on=['User Name','Total Apps'],how='left').reset_index()
    df_user_stat = df_user_stat.merge(df_rd_int,on='User Name',how='left').reset_index().drop(['level_0'],axis=1)
    df_user_stat = df_user_stat.merge(df_days,on='User Name',how='left').reset_index().drop(['level_0'],axis=1)
    
    #========= Initialize Master-Dictionaries ===========#
    dic_ind = {}
        
    dic_ind['master'] = {}  # Master dictionary
    list_list = ['Sent_delta','Sent_rounds','Num Apps per Round','Sent_intervals','Avg Ranks per Round']
    for i in list_list:
        dic_ind['master'][i] = {}  
    for index, row in df_user.iterrows():
        for i in list_list:
            dic_ind['master'][i][row['User Name']] = []    

    #========= Fill Master-Dictionary ===========#
    for index, row in df.iterrows():
        dic_ind['master']['Sent_delta'][row['User Name']].append(row['Sent_delta'])
    for key, value in dic_ind['master']['Sent_delta'].items():
        dic_ind['master']['Sent_delta'][key] = sorted(value) # List of dates of each app by User Name
        dic_ind['master']['Sent_rounds'][key] = sorted(list(set(value))) # List of dates with apps by User Name
    
    df_rd_sort = df_rd.sort_values(by=['User Name','Sent_delta'])
    for index, row in df_rd_sort.iterrows():
        dic_ind['master']['Num Apps per Round'][row['User Name']].append(row['Num Apps per Round'])
        dic_ind['master']['Sent_intervals'][row['User Name']].append(row['Interval'])
        dic_ind['master']['Avg Ranks per Round'][row['User Name']].append(row['Avg Ranks'])
    #========= Export Stat-DataFrames and Master-Dictionaries ==========================#
    df_user_stat.to_csv('../../data/edit/df_stat_indvdl.csv')
    
    df_master = df_user_stat[['User Name']]
    for i in list_list:
        for key, value in dic_ind['master'][i].items():
            dic_ind['master'][i][key] = ';'.join(str(e) for e in value)
        df_s = pd.DataFrame.from_dict(dic_ind['master'][i],orient='index')\
                 .rename(columns={0:'{}'.format(i)})
        df_s['User Name'] = df_s.index
        df_master = df_master.merge(df_s,on=['User Name'],how='left').reset_index(drop=True)
    df_master.to_csv('../../data/edit/df_master_indvdl.csv')
    
    return