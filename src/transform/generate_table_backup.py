import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict
from df2tex import df2tex

import scipy
import statsmodels.api as sm
import statsmodels.formula.api as smf

import os
import sys

# sample files in json folder
# user_crackedegg_additional_info_&_updates.json
# user_crackedegg_applicant_information.json
# user_crackedegg_application.json
# user_crackedegg_demographic_information.json
# user_crackedegg_extra_curricular_information.json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch

def keep_ascii_file(file1, file2):
    f2 = open(file2, 'w') 
    with open(file1, 'rb') as f1:
        for row in f1.read().split('\n'):
            row = keep_ascii(row)
            f2.write(row+'\n') 
        f2.close()

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


def filter_good_applicants(df, col, threshold):
    return df[df[col] > threshold]
    
def process_app_data():
    #=== Merge Tables ===#
    df = select_application_tables()
    # unquote % in urls to special characters
    df['User Name'] = df['User Name'].str.encode('utf8', 'replace').apply(urllib.unquote)
    print len(df), df.head(), df.tail()
    df.to_csv('../../data/edit/all.csv')
    df_all = pd.read_csv('../../data/edit/all.csv')
    print ("finished assembling applications dataset")
    
    df = select_search_tables()
    df['User Name'] = df['User Name'].str.encode('utf8', 'replace').str.rsplit(' ', 1).str[0]
    print len(df),df.head(),df.tail()
    df.to_csv('../../data/edit/user.csv')
    df_search = pd.read_csv('../../data/edit/user.csv')
    print ("finished assembling user basic characteristics")
    
    dic = {}
    for way in ['left','right','outer','inner']:
        dic[way] = df_all.merge(df_search,on=['User Name'],how=way).reset_index()
        print dic[way]['User Name'].nunique() 

    dif_check = list(set(dic['left']['User Name'])-set(dic['inner']['User Name']))
    print 'diff', dif_check[:20]
    # There are 'dif_check' unique users in df_all but not in df_search
    dic['inner'].to_csv('../../data/edit/inner.csv')
    
    df = dic['outer'].groupby(['Law School'])['User Name'].count().reset_index()
    df['Law School'].to_csv('../../data/edit/outer.csv')

    #=== Finalize Application Data ===#
    df_app = pd.read_csv('../../data/edit/inner.csv')
    df_app.to_csv('../../data/edit/df_app.csv')
    df_app_school = pd.DataFrame(list(set(df_app['Law School']))).rename(columns={0:'Law School'})
    df_app_school.to_csv('../../data/edit/df_app_school.csv')
    
    return 
    
def process_rank_data():
    #=== Load Ranking Data===#
    keep_ascii_file('../../data/raw/ranking/law_school_ranking_2012_2015.csv', '../../data/edit/rank_2012_2015.txt')
    df_1215 = pd.read_csv('../../data/edit/rank_2012_2015.txt')
    dic = {'USNews RANK':'rank_2012', 'Unnamed: 1':'rank_2013', 'USNews SCORE':'rank_2014',
           'Unnamed: 3':'rank_2015', 'Unnamed: 4':'Law School', 'Unnamed: 5':'score 2012',
           'Unnamed: 6':'score 2013','Unnamed: 7':'score 2014', 'Unnamed: 8':'score 2015'}
    for key, value in dic.iteritems():
        df_1215 = df_1215.rename(columns={key: value})
    df_1215 = df_1215.drop(df_1215.index[:1])

    keep_ascii_file('../../data/raw/ranking/law_school_ranking_1987_1999.csv', '../../data/edit/rank_1987_1999.txt')
    df_8799 = pd.read_csv('../../data/edit/rank_1987_1999.txt')
    lists = ['Nov','Mar','Apr','Mar.1','Mar.2','Mar.3','Mar.4','Mar.5', 'Mar.6','Mar.7','Mar.8']
    for item in lists:
        df_8799 = df_8799.rename(columns={item:'rank_'+str(int(df_8799.loc[0,item]))})
    df_8799 = df_8799.rename(columns={'Unnamed: 0': 'Law School'})
    df_8799 = df_8799.drop(df_8799.index[:1]).drop(['Unnamed: 12','Aver'],axis = 1)

    keep_ascii_file('../../data/raw/ranking/law_school_ranking_2000_2008.csv', '../../data/edit/rank_2000_2008.txt')
    df_0008 = pd.read_csv('../../data/edit/rank_2000_2008.txt')
    df_0008 = df_0008.rename(columns={'April':'April.0','LAW SCHOOL':'Law School'})
    for item in range(9):
        df_0008 = df_0008.rename(columns={'April.'+str(item):'rank_'+str(df_0008.loc[0,'April.'+str(item)])})
    df_0008 = df_0008.drop(df_0008.index[:1]).drop(['blank','Rank'],axis=1)

    keep_ascii_file('../../data/raw/ranking/law_school_ranking_2009_2011.csv', '../../data/edit/rank_2009_2011.txt')
    df_0911 = pd.read_csv('../../data/edit/rank_2009_2011.txt')
    dic = {'2009-2012 USNews SCORE':'score 2009','Law Schools Ordered by':'score 2010',
           'USNews ANNUAL Score Change':'score 2011','3 YEARS':'score 2012', 'Unnamed: 4':'Law School'}
    for key, value in dic.iteritems():
        df_0911 = df_0911.rename(columns={key:value})
    df_0911 = df_0911[['score 2009', 'score 2010', 'score 2011', 'score 2012','Law School']].drop(df_0911.index[:1])\
        .append({'score 2009':100,'score 2010':100,'score 2011':100,'score 2012':100, 'Law School':'Yale U (CT)'},ignore_index=True).reset_index()
    for item in range(2009,2013):
        df_0911.loc[df_0911['score '+str(item)].apply(str).str.contains('Tier 3'),'score '+str(item)] = -3
        df_0911['rank_'+str(item)] = df_0911['score '+str(item)].apply(float).rank(ascending=0)  
    
    keep_ascii_file('../../data/raw/ranking/school_names_ranking_2018.csv', '../../data/edit/rank_2018.txt')
    df_18 = pd.read_csv('../../data/edit/rank_2018.txt',header=None)
    df_18 = df_18.rename(columns={0:'rank_2018',1:'Law School', 2:'Tuition',3:'FT Enrollment'})
    df_18_v1 = df_18[~df_18['rank_2018'].isnull()].reset_index()
    df_18_v2 = df_18[df_18['rank_2018'].isnull()].reset_index().rename(columns={'Law School':'Location'}).drop(['Tuition','FT Enrollment'],axis=1)
    for data in [df_18_v1, df_18_v2]:
        data['index'] = data.index
    df_18 = df_18_v1.merge(df_18_v2, on='index',how='inner')
    df_18['Law School'] = df_18['Law School'].str.replace('-_',' ').str.replace('_',' ').str.replace(',','')
    df_18.to_csv('../../data/edit/rank_2018_new.txt')

    #=== Build Masterfile for School Ranking 87-15 ===#
    keep_ascii_file('../../data/raw/ranking/school_names_ranking_old.csv', '../../data/edit/rank_old.txt')
    master1 = pd.read_csv('../../data/edit/rank_old.txt')
    master1 = master1[['threshold','rank1215','rank0008','rank0911','rank8799']]
    
    df_ranks = master1
    df_list = [df_1215,df_0911,df_0008,df_8799,df_18]
    name_list = ['1215','0911','0008','8799','18']
    for i in range(len(df_list)): # applies to items in df_list, not df_1215,df_0911, etc
        df_list[i] = df_list[i][df_list[i]['Law School'].notnull()]
    for i in range(len(df_list)-1):
        df_ranks = df_ranks.merge(df_list[i],left_on='rank'+name_list[i],right_on='Law School',how='outer').drop(['Law School'],axis=1)
    df_ranks = df_ranks.drop(['score 2012_y','rank_2012_y'],axis=1).rename(columns={'score 2012_x':'score 2012','rank_2012_x':'rank_2012'})\
               .drop(['rank1215','rank0911','rank0008','rank8799'],axis=1)
    df_ranks.to_csv('../../data/edit/ranks.csv')

    
    #=== Load pig_match masterfile for school names ===#
    #name<==df_18, match<==threshold and law_school_numbers website
    keep_ascii_file('../../data/raw/ranking/pig_match.csv', '../../data/edit/pig_match.txt')
    df_pig_match_flat = pd.read_csv('../../data/edit/pig_match.txt')
    
    #=== Explode pig_match masterfile for school names ===#
    df_pig_match_flat.loc[df_pig_match_flat['match'].isnull(),'match']=['Temporary']
    df_pig_match = df_pig_match_flat['match'].str.split(';', expand=True).stack().reset_index(level=0).set_index('level_0')\
              .rename(columns={0:'match'}).join(df_pig_match_flat.drop('match',1), how='left')
    df_pig_match.loc[df_pig_match['match']=='Temporary','match']=''
    for var in ['match','name']:
        df_pig_match[var] = df_pig_match[var].str.lstrip().str.rstrip()
    df_pig_match.loc[df_pig_match['match']=='UCLA','name'] = 'University of California_Los Angeles'
    df_pig_match['name'] = df_pig_match['name'].str.replace('-_',' ').str.replace('_',' ').str.replace(',','')
    df_pig_match.to_csv('../../data/edit/pig_match_long.txt') 


    #=== Revise pig_match masterfile for school names ===#
    df_pig_match = df_pig_match[df_pig_match['score']>0.0]
    dic = {'Louisiana State University Baton Rouge (Hebert)':['Louisiana SU','Louisana State U'],
           'Mitchell Hamline School of Law':['Hamline U','Hamline University PT', 'Hamline University', 
                                             'Hamline University F','Hamline University F PT','William Mitchell',
                                             'William Mitchell College of Law','William Mitchell College of Law F PT',
                                             'Hamline University PT','Hamline University F','William Mitchell College of Law F',
                                             'William Mitchell College of Law PT','Hamline University F PT'],
           'Lewis & Clark College (Northwestern)':['Lewis Clark C','Lewis and Clark College',
                                                   'Lewis and Clark College PT','Lewis and Clark College F PT',
                                                   'Lewis and Clark College F','Lewis and Clark College PT'],
           'The John Marshall Law School':['John Marshall Law School - Chicago F','John Marshall Law School - Chicago PT',
                                           'John Marshall Law School - Chicago','John Marshall Law School - Chicago F PT'],
           'Yeshiva University (Cardozo)':['Cardozo-Yeshiva University PT','Cardozo-Yeshiva University',
                                           'Cardozo-Yeshiva University F PT','Cardozo-Yeshiva University F'],
           'Indiana University Indianapolis (McKinney)':['Indiana University Robert H. McKinney School of Law PT',
                                                         'Indiana University Robert H. McKinney School of Law F PT',
                                                         'Indiana University Robert H. McKinney School of Law F',
                                                         'Indiana University Robert H. McKinney School of Law'],
           'Texas A&M University':['Texas A&M University School of Law F PT','Texas A&M University School of Law PT',
                                   'Texas A&M University School of Law','Texas A&M University School of Law F'],
           'Faulkner University (Jones)':['Jones School of Law PT','Jones School of Law F','Jones School of Law'],
           'Western Michigan University Thomas M. Cooley Law School':['Thomas M Cooley Law School F PT','Thomas M Cooley Law School PT',
                                                                      'Thomas M Cooley Law School','Thomas M Cooley Law School F'],
           'Arizona Summit Law School':['Phoenix School of Law','Phoenix School of Law F','Phoenix School of Law PT','Phoenix School of Law F PT'],
           'Illinois Institute of Technology (Chicago Kent)':['Chicago-Kent College of Law (IIT)','Chicago-Kent College of Law (IIT) F',
                                                              'Chicago-Kent College of Law (IIT) F PT','Chicago-Kent College of Law (IIT) PT'],
           'Rutgers The State University of New Jersey' :['Rutgers Camden','Rutgers Newark','Rutgers State University Camden PT',
                                                          'Rutgers Law School PT','Rutgers Law School F','Rutgers State University Camden F',
                                                          'Rutgers Law School F PT','Rutgers State University Camden F PT',
                                                          'Rutgers Law School','Rutgers State University Camden'],
           'University of California (Hastings)':['UC Hastings','University of California Hastings F',
                                                  'University of California Hastings','University of California Hastings F PT',
                                                  'University of California Hastings PT'],
           'CUNY':['CUNY Queens College F','CUNY Queens College','CUNY Queens College PT','CUNY Queens College F PT'],
           'Loyola Marymount University':['Loyola Law School F PT','Loyola Law School','Loyola Law School F','Loyola Law School PT'],
           'Georgia State University':['Georgia State U'],
           'University of Missouri':['U Missouri Columbia'],
           'University at Buffalo SUNY':['SUNY Buffalo Law School'],
           'University of Missouri Kansas City':['U Missouri Kansas'],
           }
    for key, value in dic.iteritems():
        for i in range(len(value)):
            df_pig_match = pd.DataFrame(np.array([[key,value[i],1.0]]), columns=['name', 'match', 'score']).append(df_pig_match, ignore_index=True)
    df_pig_match.to_csv('../../data/edit/pig_match_long_new.txt')
    
    #=== Merge pig_match with rankings 18 ===#
    df_pig_rank_18 = df_18.merge(df_pig_match,left_on='Law School',right_on='name',how='outer').reset_index()
    df_pig_rank_18 = df_pig_rank_18[df_pig_rank_18['Law School'].notnull() & df_pig_rank_18['name'].notnull()].rename(columns={'rank_2018_x':'rank_2018'}).drop(['Law School','rank_2018_y'],axis=1)
    
    #=== Merge pig_match further with rankings 87-15 ===#
    df_ranks['threshold'] = df_ranks['threshold'].str.lstrip().str.rstrip()
    df_pig = df_ranks.merge(df_pig_rank_18,left_on='threshold',right_on='match',how='outer').reset_index()
    for col in df_pig.columns:
        if ('index' in col) | ('Unnamed' in col)|('level' in col):
            df_pig = df_pig.drop(col,axis=1)
    df_pig = df_pig[df_pig['threshold'].notnull()]
    df_pig = df_pig[df_pig['name'].notnull()].drop(['match','score'],axis=1)
    df_pig = df_pig.drop(['rank_2018','Tuition','FT Enrollment','Location'],axis=1)
    df_pig_rank_18_sub = df_pig_rank_18[['name','match','rank_2018','Tuition','FT Enrollment','Location']]
    df_pig_ranks = df_pig_rank_18_sub.merge(df_pig,left_on=['name'],right_on=['name'],how='outer').reset_index()
    df_pig_ranks.to_csv('../../data/edit/pig_ranks.csv')
    
    return
    
def merge_app_rank():
    #=== Merge pig_match with rankings 87-15 to law school numbers ===#
    df_app = pd.read_csv('../../data/edit/df_app.csv')
    df_app_school = pd.read_csv('../../data/edit/df_app_school.csv')
    df_pig_ranks = pd.read_csv('../../data/edit/pig_ranks.csv')
    list_df = [df_app_school,df_app]  
    list_str = ['app_school','app']  
    list_ca = ['University of Windsor','University of British Columbia F','University of Alberta',
               'University of New Brunswick','University of Saskatchewan','Dalhousie University','University of Windsor F',
               'University of Manitoba','York University (Osgoode Hall)',"Queen's University",'University of Victoria',
               'University of Ottawa','University of Toronto F','University of Toronto','University of British Columbia',
               'University of Western Ontario','McGill University','University of Calgary']
    list_bad = ['Nashville School of Law F','Nashville School of Law','Nashville School of Law PT']
    for i in range(len(list_df)):
        list_df[i]['Law School'] = list_df[i]['Law School'].str.replace('\n','').str.lstrip().str.rstrip().str.replace('  ',' ')
        list_df[i]['Law School'] = list_df[i]['Law School'].str.replace('Texas A&M;','Texas A&M')
        for item in (list_ca + list_bad):
            list_df[i] = list_df[i][list_df[i]['Law School']!=item]
        df = list_df[i].merge(df_pig_ranks,left_on='Law School',right_on='match',how='outer')
        df.to_csv('../../data/edit/{}_test.csv'.format(list_str[i]))
        df[df['match'].notnull() & df['Law School'].notnull()].to_csv('../../data/edit/{}_matched.csv'.format(list_str[i]))
    return

def clean_app_rank(df_app):
    #=== Rename Key Variables ============#
    #print df_app.columns
    df_app_new = df_app.drop(['Unnamed: 0', 'Unnamed: 0_x', 'Unnamed: 0.1', 'index_x',
                              'Unnamed: 0_x.1','Unnamed: 0_y','Last Updated_x','Unnamed: 0_y.1', 'index_y'],axis=1)
    dic = {'$$$':'grant','Last Updated_y':'Last Updated'}
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

def get_stats(group):
    return {'Mean': group.mean(),'SD':group.std()} #, ,'count': group.count()}

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

def stat_sample(df_app):
    dic_count = {}
    dic_detail = {}
    for yr in range(2003,2016):
        df_yr = df_app[df_app['Year'] == yr]
        
        dic_count[yr-2003] = {}
        dic_count[yr-2003]['Number of Applicants'] = pd.DataFrame(df_yr['User Name'].agg(['nunique']))
        dic_count[yr-2003]['Number of Applicants Reporting Enrollment Decisions'] = pd.DataFrame(df_yr.loc[df_yr['Attend']==1,'User Name'].agg(['nunique']))
        type_list = ['ED','SP']
        for tp in type_list:
            dic_count[yr-2003]['Number of Applicants with {} Apps'.format(tp)] = pd.DataFrame(df_yr.loc[df_yr[tp]==1,'User Name'].agg(['nunique']))
        
        df_school = df_yr.groupby(['Law School'])['User Name'].count().reset_index()
        dic_count[yr-2003]['Number of Schools'] = pd.DataFrame(df_school['Law School'].agg(['nunique']))
        dic_count[yr-2003]['Number of Schools with Over 100 Apps in Data'] = pd.DataFrame(df_school.loc[df_school['User Name']>=100,'Law School'].agg(['nunique']))
        for tp in type_list:
            dic_count[yr-2003]['Number of Schools with {} Tracks'.format(tp)] = pd.DataFrame(df_yr.loc[df_yr['{}_school'.format(tp)]==1,'Law School'].agg(['nunique']))
        #print 'year=',yr, dic_count[yr-2003]

        dic_detail[yr-2003] = {}
        dic_detail[yr-2003]['Time to Apply (Days since Sep 1)']=pd.DataFrame(df_yr['Sent_delta'].agg(['mean','std','count']))
        #print dic_detail[yr-2003]['Time to Apply (Days since Sep 1)'].iloc[:,0]
        dic_detail[yr-2003]['Time to Hear Back (Days since sent)']=pd.DataFrame(df_yr[['Decision_delta']].agg(['mean','std','count']))
        action_list = ['Sent','grant yes']
        name_list = ['Applications','Number of Grants']
        for index, act in enumerate(action_list):
            df_act = df_yr.groupby(['User Name'])['{}'.format(act)].count().reset_index()
            dic_detail[yr-2003]['{} Per Capita'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
        action_list = ['Accepted','Rejected','Pending','Waitlisted','grant yes']
        name_list = ['Admissions','Rejections','Pending','Waitlists','Number of Grants']
        for index, act in enumerate(action_list):
            df_act = df_yr.groupby(['User Name'])['{}'.format(act)].sum().reset_index()
            dic_detail[yr-2003]['{} Per Capita'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
        action_list = ['grant']
        name_list = ['Size of Grants']
        for index, act in enumerate(action_list):
            df_act = df_yr.groupby(['User Name'])['{}'.format(act)].mean().reset_index()
            dic_detail[yr-2003]['{} Per Capita'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
        #dic_gpa_lsat = 
        #print 'year=',yr,dic_detail[yr-2003]
    return dic_count, dic_detail
    

if __name__ == '__main__':
    
    process_app_data()
    process_rank_data()
    merge_app_rank()
    
    df_app = pd.read_csv('../../data/edit/app_matched.csv')
    df_app_new = clean_app_rank(df_app)
    
    df_app_new = pd.read_csv('../../data/edit/app_new.csv')
    df_app_date = clean_app_date(df_app_new)   
    
    df_app_date = pd.read_csv('../../data/edit/app_date.csv')
    df_app_clean = clean_sample(df_app_date)
    dic_count, dic_detail = stat_sample(df_app_clean)
    
    #===== Export Regression Results ======#
    # Go to Stata, sadly
    #===== Export Summary Statistics ======#
    row_name = [
			['Summary_Statistics_I', 'Number of Schools','Number of Schools with Over 100 Apps in Data',
			 'Number of Schools with ED Tracks','Number of Schools with SP Tracks','Number of Applicants',
			 'Number of Applicants with ED Apps','Number of Applicants with SP Apps',
			 'Number of Applicants Reporting Enrollment Decisions'],
			['Summary_Statistics_II', 'Time to Apply (Days since Sep 1)','Time to Hear Back (Days since sent)',
			 'Applications Per Capita','Admissions Per Capita','Rejections Per Capita','Waitlists Per Capita',
			 'Pending Per Capita','Number of Grants Per Capita','Size of Grants Per Capita'],
		]
    rename_lookup = [{'nunique':'Obs'},{'mean':'Mean','std':'SD','count':'Obs'}]
    col_name = [['Obs'],['Mean','SD','Obs']]
    for yr in range(2006,2016):
        for index, stats in enumerate([dic_count[yr-2003],dic_detail[yr-2003]]):
			df = pd.DataFrame()
			for keys,values in stats.iteritems():
				df = df.append(values.transpose().assign(Variable=[keys]))
			df = df.set_index('Variable',drop=False)
			row_head = row_name[index][0]
			row_tail = row_name[index][1:]
			df = df.reindex(row_tail).rename(columns=rename_lookup[index])
			df2tex(df, '../../model/tables/','{}_{}.tex'.format(row_head,yr), "%8.2f", 0, col_name[index], ['Variable'], col_name[index])
    
