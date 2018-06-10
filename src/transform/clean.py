import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict
from utils import keep_ascii_file, filter_good_applicants, get_stats
from select_tables import select_application_tables, select_search_tables, select_user_tables, select_user_tables2
from process_merge import process_app_data, process_rank_data, merge_app_rank

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch

def clean_app_rank(df_app):
    #=== Rename Key Variables ============#
    print df_app.columns
    df_app_new = df_app.drop(['Unnamed: 0', 'Unnamed: 0_x', 'level_0', 'index_x','Unnamed: 0_x.1','Unnamed: 0_y',
                              'Last Updated_x','Unnamed: 0_y.1','LSAT_x', 'index_y'],axis=1)
    dic = {'$$$':'grant','Last Updated_y':'Last Updated','LSAT_y':'LSAT'}
    for key,value in dic.iteritems():
        df_app_new = df_app_new.rename(columns={key:value})
        
    #=== Clean 'Status' ===#
    #print set(df_app_new['Status'])
    for x in ['Status_Final','Defer','Attend','Waitlist','Withdraw']:
        df_app_new[x] = 0
    
    dic = {'WL, Rejected D W':'WL, Rejected', 'WL, Rejected  A':'WL, Rejected', 'WL, Rejected  W':'WL, Rejected',
           'Waitlisted  A':'Waitlisted', 'Pending  A':'Pending', 'Rejected D ':'Rejected',
           'Rejected  A':'Rejected', 'WL, Rejected D A':'WL, Rejected','Rejected  W':'Rejected',
           'Waitlisted D W':'Waitlisted W', 'Rejected D W':'Rejected'}
    for key, value in dic.iteritems():
        df_app_new.loc[df_app_new['Status']==key,'Status'] = value
    dic = {'Accepted':3, 'Rejected':1,'Waitlisted':2,'Pending':0,'Intend to Apply':-1}
    for key, value in dic.iteritems():
        df_app_new.loc[df_app_new['Status'].str.contains(key),'Status_Final'] = value
    dic = {'Waitlisted':1, 'WL':1}
    for key, value in dic.iteritems():
        df_app_new.loc[df_app_new['Status'].str.contains(key),'Waitlist'] = value
    dic = {' A':1}
    for key, value in dic.iteritems():
        df_app_new.loc[df_app_new['Status'].str.contains(key),'Attend'] = value
    dic = {' W':1}
    for key, value in dic.iteritems():
        df_app_new.loc[df_app_new['Status'].str.contains(key),'Withdraw'] = value
    
    print len(df_app_new)
    df_app_new = df_app_new[df_app_new['Status_Final']>=0]
    print len(df_app_new)
    
    #=== Clean full/part time ===#    
    df_app_new['Part Time'] = 0
    df_app_new.loc[df_app_new['Law School'].str.contains('PT'),'Part Time'] == 1 
    
    #=== Clean School Ranks =====#
    #df = pd.read_csv('../../data/edit/pig_ranks.csv')
    #for yr in (range(1990,2016)+[1987,2018]):
    #    print 'raw: year=',yr,'==',df_app_new['rank '+str(yr)].head()

    for yr in (range(1990,2016)+[1987,2018]):
        df_app_new['rank_'+str(yr)] = df_app_new['rank_'+str(yr)].fillna('').apply(str).apply(keep_ascii)

    df_app_new.loc[df_app_new['rank_2012']=='24..5','rank_2012'] = '24.5'
    df_app_new['rank_2018'] = df_app_new['rank_2018'].str.replace('#','').str.replace('Tie','')\
                              .str.replace('RNP','').str.replace('Unranked','')
                                  
    for yr in (range(1990,2016)+[1987,2018]):
        df_app_new.loc[df_app_new['rank_'+str(yr)].str.contains('NR'),'rank_'+str(yr)] = '-9999.0'
        df_app_new.loc[df_app_new['rank_'+str(yr)]=='','rank_'+str(yr)] = '-9999.0'
    
    for yr in ([1987,2018]+range(1990,2016)):
        df_app_new['rank_'+str(yr)] = df_app_new['rank_'+str(yr)].astype(float)
        df_app_new.loc[df_app_new['rank_'+str(yr)]==-9999,'rank_'+str(yr)] = np.nan
        #print 'year=',yr,'==',df_app_new['rank '+str(yr)].describe()
    
    #=== Rename =====#
    print df_app_new['Law School'].nunique()
    df_app_new = df_app_new.drop(['Law School'],axis=1)
    df_app_new = df_app_new.rename(columns={'name':'Law School'})
    print df_app_new['Law School'].nunique()
    
    #=== Export Data =====#
    df_app_new.to_csv('../../data/edit/app_new.csv')
    return df_app_new

def clean_app_date(df_app):
    #=== Clean Dates ===# Timing Consuming
    for item in ['Sent','Received','Complete','Decision']:
        df_app[item]=pd.to_datetime(df_app[item], errors = 'coerce')
    
    #=== Convert Dates to Float ===#   
    df_app['Year'] = df_app['Year'].apply(int)
    df_yr = {}
    for yr in range(2003, 2017):
        df_yr[yr-2003] = df_app[(df_app['Sent']>=date(yr, 9, 1)) & (df_app['Sent']<=date(yr+1,8,31))]
        df_yr[yr-2003]['Sent_delta'] = (df_yr[yr-2003]['Sent'] - date(yr, 9, 1))  / np.timedelta64(1,'D')
        df_yr[yr-2003]['Decision_delta'] = (df_yr[yr-2003]['Decision'] - df_yr[yr-2003]['Sent'])  / np.timedelta64(1,'D')       
        print 'Year=',yr,df_yr[yr-2003][['Sent','Sent_delta','Decision_delta','GPA','LSAT']].describe()
    
    #=== Join all sub-data-frames ===# 
    df_app_date = df_yr[0]
    for yr in range(2004,2017):
        df_app_date = df_app_date.append(df_yr[yr-2003])
    
    #=== Export Data ======#
    df_app_date.to_csv('../../data/edit/app_date.csv')
    return df_app_date


def clean_sample(df_app):
    lookup = {'Status_Final':{'Accepted':3,'Rejected':1,'Pending':0,'Waitlisted':2},
              'Type':{'ED':'ED','SP':'SP'}}
    for key_out, value_out in lookup.iteritems():
        # print df_app[key_out].unique()
        for key_in, value_in in value_out.iteritems():
            df_app[key_in] = (df_app[key_out] == value_in)*1.0

    df_app['grant'] = df_app['grant'].str.replace('$','').str.replace(',','').apply(float)
    df_app.loc[df_app['grant']<1000,'grant'] = np.nan
    df_app['grant yes'] = (df_app['grant']>0)*1.0
    
    df_attend_reported = df_app.groupby(['User Name'])['Attend'].max().reset_index().rename(columns={'Attend':'Attend Reported'})
    df_app = df_app.merge(df_attend_reported,on='User Name',how='left')
    df_app.loc[~df_app['Attend']==1,'Attend'] = 0
    
    df_yr = {}
    df_school = {}
    type_list = ['ED','SP']
    for yr in range(2003,2016):
        df_yr[yr-2003] = df_app[df_app['Year'] == yr]
        
        df_yr[yr-2003]['unranked'] = (df_yr[yr-2003]['rank_{}'.format(yr)].isnull())*1.0
        df_yr[yr-2003]['rank_cross'] = (1.0-df_yr[yr-2003]['unranked'])*df_yr[yr-2003]['rank_{}'.format(yr)].fillna(0)
        
        for tp in type_list:
            df_school[tp] = df_yr[yr-2003].groupby(['Law School'])['{}'.format(tp)].max().reset_index().rename(columns={'{}'.format(tp):'{}_school'.format(tp)})
            df_yr[yr-2003] = df_yr[yr-2003].merge(df_school[tp],on='Law School',how='left')
            df_yr[yr-2003]['{}_cross'.format(tp)] = df_yr[yr-2003]['{}'.format(tp)]*df_yr[yr-2003]['{}_school'.format(tp)]

            
    df_app = df_yr[0]
    for yr in range(2004,2016):
        df_app = df_app.append(df_yr[yr-2003])
    
    #=== Export Data ======#
    df_app.to_csv('../../data/edit/app_clean.csv')
    return df_app
