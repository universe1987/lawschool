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
from select_tables_details import select_applicant_information_tables, select_demographic_information_tables,\
                                  select_extra_curricular_information_tables,select_additional_info_updates_tables


import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch

def process_app_data():
    #=== Import Application Tables ===#
    df = select_application_tables()
    # unquote % in urls to special characters
    df['User Name'] = df['User Name'].str.encode('utf8', 'replace').apply(urllib.unquote)
    print len(df), df.head(), df.tail()
    df.to_csv('../../data/edit/all.csv')
    df_all = pd.read_csv('../../data/edit/all.csv')
    print ("finished assembling applications dataset")
        
    #=== Import Search Tables ===#
    df = select_search_tables()
    df['User Name'] = df['User Name'].str.encode('utf8', 'replace').str.rsplit(' ', 1).str[0]
    print len(df),df.head(),df.tail()
    df.to_csv('../../data/edit/user.csv')
    df_search = pd.read_csv('../../data/edit/user.csv')
    print ("finished assembling user basic characteristics")

    #=== Import Applicant Details Tables ===#
    #df_applicant_information = pd.DataFrame()
    #df_demographic_information = pd.DataFrame()
    #df_extra_curricular_information = pd.DataFrame()
    #df_additional_info_updates = pd.DataFrame()
    
    table_list = ['applicant_information','demographic_information','extra_curricular_information','additional_info_updates']
    df_list = [pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),pd.DataFrame()]
    fun_list = [select_applicant_information_tables,select_demographic_information_tables,select_extra_curricular_information_tables,select_additional_info_updates_tables]
    for index, item in enumerate(table_list):
        df = fun_list[index]()
        # unquote % in urls to special characters
        df['User Name'] = df['User Name'].str.encode('utf8', 'replace').apply(urllib.unquote)
        print len(df), df.head(), df.tail()
        df.to_csv('../../data/edit/{}.csv'.format(item))
        df_list[index] = df #pd.read_csv('../../data/edit/{}.csv'.format(item))
        print ("finished assembling {} dataset".format(item))

    #=== Merge All Pieces of Applicant Details Tables ===#
    df_details = df_list[0]
    for index in range(1, len(df_list)):
        df_details = df_details.merge(df_list[index],on=['User Name'],how='inner').reset_index(drop=True)
    print 'df_details', index,df_details['User Name'].nunique(), df_details.columns.tolist()
    df_details.to_csv('../../data/edit/df_details.csv')
    
    #=== Merge Application and Search Tables ===#
    dic = {}
    for way in ['left','right','outer','inner']:
        dic[way] = df_all.merge(df_search,on=['User Name'],how=way).reset_index()
        print dic[way]['User Name'].nunique() 

    dif_check = list(set(dic['left']['User Name'])-set(dic['inner']['User Name']))
    print 'diff', dif_check[:20], len(dif_check)
    # There are 'dif_check' unique users in df_all but not in df_search
    dic['inner'].to_csv('../../data/edit/inner.csv')
    
    df = dic['outer'].groupby(['Law School'])['User Name'].count().reset_index()
    df['Law School'].to_csv('../../data/edit/outer.csv')    
    
    #=== Merge Further with Applicant Details Tables ===#
    df_app_with_details = dic['inner'].merge(df_details,on=['User Name'],how='inner').reset_index()
    print 'df_app_with_details', df_app_with_details['User Name'].nunique(), df_app_with_details.columns.tolist()
    
    #=== Finalize Application Data without Applicant Details Tables ===#
    df_app = pd.read_csv('../../data/edit/inner.csv')
    df_app.to_csv('../../data/edit/df_app.csv')
    df_app_school = pd.DataFrame(list(set(df_app['Law School']))).rename(columns={0:'Law School'})
    df_app_school.to_csv('../../data/edit/df_app_school.csv')
    
    #=== Finalize Application Data with Applicant Details Tables ===#
    df_app_with_details.to_csv('../../data/edit/df_app_with_details.csv')
    df_app_school_with_details = pd.DataFrame(list(set(df_app_with_details['Law School']))).rename(columns={0:'Law School'})
    df_app_school_with_details.to_csv('../../data/edit/df_app_school_with_details.csv')
    
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
