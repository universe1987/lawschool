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

def gen_dummy():
    df = pd.read_csv('../../data/edit/df_details_race_college_major_numeric_EC_cleaned.csv')
    df = df.fillna('')
    # Categorical variables: gender, years out of undergrad, race, college name or type, 
    #                        major, state, extra curricular
    
    # Correct false values
    df.loc[df['group']=='national','group'] = 'national_univ'
    df.loc[df['group']=='lac','group'] = 'national_lac'
    
    # Bundle over-small groups
    region_json = {'northeast':['connecticut', 'maine', 'massachusetts', 'new hampshire', 'rhode island', 'Vermont',
                                'new jersey','new york','pennsylvania'],
                   'midwest':['illinois', 'indiana', 'michigan', 'ohio', 'wisconsin',
                              'iowa', 'kansas', 'minnesota', 'missouri', 'nebraska', 'north dakota', 'south dakota'],
                   'south':['delaware', 'florida', 'georgia', 'maryland', 'north carolina', 'south carolina', 'virginia', 'washington - d.c.', 'west virginia',
                            'alabama', 'kentucky', 'mississippi', 'tennessee',
                            'arkansas', 'louisiana', 'oklahoma', 'texas'],
                   'west':['arizona', 'colorado', 'idaho', 'montana', 'nevada', 'new mexico', 'utah', 'wyoming',
                           'alaska', 'california', 'hawaii', 'oregon', 'washington']
                  }
    df['region'] = ''
    for key, value in region_json.iteritems():
        for s in value:
            df.loc[df['State']==s,'region'] = key
    
    # Create dummies for non-major variables
    dummy_json = {'Gender':['Female','Male'], 
                 'Years out of Undergrad':['1-2 Years','3-4 Years','In Undergrad','5-9 Years','10+ Years'],
                 'Race2':['white','asian and pacific islander','african','Mixed, probably not urm','hispanic','mexican','puerto rican','Native American or alaskan'],
                 'group':['national_univ','national_lac','midwest_univ','western_univ','north_univ','hbcu','south_univ','western_college','midwest_college','south_college','eng_nodoctorate','north_college'],
                 'groups':['neutral','positive','bad','foreign','bad_school'],
                 'region':['south','west','northeast','midwest']
                }
    for key, dummy_list in dummy_json.iteritems():
		for var in dummy_list:
			df[var] = '0'
			df.loc[df[key]==var,var] = '1'
			df.loc[df[key]=='',var] = ''
    
    # Clean dummies for majors
    major_list = ['social sciences', 'arts & humanities', 'business & management', 'natural sciences', 'engineering', 'health professions', 'other']
    for item in major_list:
        df[item] = df[item].astype(str)
        df.loc[df[item] == '1.0', item] = '1'
        df.loc[df[item] == '', item] = '0'
    for item in major_list:
        df.loc[(df['social sciences']=='') & (df['arts & humanities'] =='') &
               (df['business & management']=='') & (df['natural sciences'] =='') &
               (df['engineering']=='') & (df['health professions'] =='') &
               (df['other']=='') , item] = ''
    
    # Drop redundant variables
    var_list = ['Unnamed: 0','Major list', 'Major list len', 'Major element 1', 'Major element 2', 'Major element 3', 'Major element 4', 'Major element 5', 'Major element 6',
                'College Name or Type','name','City','State_acronym', 'region','enrollment','location',
                'extra curricular', 'additional info', 'Class Rank','Race']
    df = df.drop(var_list, axis = 1)
    
    # Generate Data set with dummies
    print df.columns.tolist()
    df.to_csv('../../data/edit/df_details_dummy_cleaned.csv')
    return



def clean_app_rank(df_app):
    #=== Rename Key Variables ============#
    print df_app.columns
    
    #=== When using df_app_with_details as input data ===#
    #=== See "Finalize Application Data with Applicant Details Tables" at process_merge.py ===#
    #df_app_new = df_app.drop(['Unnamed: 0', 'Unnamed: 0_x', 'level_0', 'index_x','Unnamed: 0_x.1','Unnamed: 0_y',
    #                          'Last Updated_x','Unnamed: 0_y.1','LSAT_x', 'index_y'],axis=1)
    #dic = {'$$$':'grant','Last Updated_y':'Last Updated','LSAT_y':'LSAT'}
    #for key,value in dic.iteritems():
    #    df_app_new = df_app_new.rename(columns={key:value})
    
    #=== When using df_app as input data ===#
    df_app_new = df_app.drop(['Unnamed: 0','Unnamed: 0_x','Unnamed: 0_x.1','Unnamed: 0_y',
                              'Unnamed: 0_y.1','index_x','index_x','index_y','Unnamed: 0.1',
                              'Last Updated_x','Unnamed: 0_x.1'],axis=1)                                                     
    dic = {'$$$':'grant','Last Updated_y':'Last Updated'}
    for key,value in dic.iteritems():
        df_app_new = df_app_new.rename(columns={key:value})
        
    #=== Clean 'Status' ===#
    #print set(df_app_new['Status'])
    for x in ['Status_Final','Defer','Waitlist']:
        df_app_new[x] = 0 # Pending
    for x in ['Attend','Withdraw']:
        df_app_new[x] = -1 # Not reported
    
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
    
    print 'all',len(df_app_new)
    df_app_new = df_app_new[df_app_new['Status_Final']>=0]
    print 'actually applied',len(df_app_new)

    #df_app_new2 = df_app_new[df_app_new['Status_Final']>0]
    #print 'actually applied with status known', len(df_app_new2)
    
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
    
    #=== Export List of Law Schools ===#
    df_law_unique = pd.DataFrame(df_app_new['Law School'].unique())
    df_law_unique.to_csv('../../data/edit/list_law_schools.csv')
    
    #=== Export Data =====#
    df_app_new.to_csv('../../data/edit/app_new.csv')
    return df_app_new

def clean_app_date(df_app):
    #=== Clean Dates ===# Timing Consuming
    for item in ['Sent','Received','Complete','Decision']:
        df_app[item]=pd.to_datetime(df_app[item], errors = 'coerce')  
        df_app['{}_weekday'.format(item)] = df_app[item].dt.weekday
    
    #=== Convert Dates to Float ===#   
    df_app['Year'] = df_app['Year'].apply(int)
    df_yr = {}
    for yr in range(2003, 2017): 
        ##df_yr[yr-2003] = df_app[df_app['Year']==yr]
        df_yr[yr-2003] = df_app
        print df_yr[yr-2003]['Sent'].describe()
        #df_yr[yr-2003]['Sent'] = df_yr[yr-2003][['Sent','Complete','Received']].min(axis=1)
        print df_yr[yr-2003]['Sent'].describe()
        df_yr[yr-2003] = df_yr[yr-2003][(df_yr[yr-2003]['Sent']>=date(yr, 9, 1)) & (df_yr[yr-2003]['Sent']<=date(yr+1,8,31))]
        df_yr[yr-2003].loc[(df_yr[yr-2003]['Decision']<=df_yr[yr-2003]['Sent']) | (df_yr[yr-2003]['Decision']>date(yr+1,8,31)),'Decision'] = date(1900, 9, 1)
        df_yr[yr-2003]['Sent_delta'] = (df_yr[yr-2003]['Sent'] - date(yr, 9, 1))  / np.timedelta64(1,'D')
        df_yr[yr-2003]['Decision_delta'] = (df_yr[yr-2003]['Decision'] - df_yr[yr-2003]['Sent'])  / np.timedelta64(1,'D')       
        print 'Year=',yr,df_yr[yr-2003][['Sent','Sent_delta','Decision_delta','GPA','LSAT']].describe()
        
    #=== Join all sub-data-frames ===# 
    df_app_date = df_yr[0]
    for yr in range(2004,2017):
        df_app_date = df_app_date.append(df_yr[yr-2003])
    
    #=== Export Data ======#
    df_app_date.to_csv('../../data/edit/app_date.csv')
    print len(df_app_date[df_app_date['Sent_delta']>=0.0]) #190563 #207126
    print 'the end'
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
    #print df_attend_reported['Attend Reported'].unique()
    df_app = df_app.merge(df_attend_reported,on='User Name',how='left')
    df_app = df_app.sort_values(by=['User Name','Attend'])
    #print df_app[['Attend','Attend Reported','User Name']].head(35)
    df_app.loc[(df_app['Attend']== -1) & (df_app['Attend Reported']==1),'Attend'] = 0
    #print df_app[['Attend','Attend Reported','User Name']].head(35)
    print df_app['Attend'].unique()
    #raw_input('attend unique values')
    
    df_status_reported = df_app.groupby(['User Name'])['Status_Final'].max().reset_index().rename(columns={'Status_Final':'Status_Final Reported'})
    df_app = df_app.merge(df_status_reported, on='User Name',how='left')
    df_app = df_app.sort_values(by=['User Name','Status_Final'])
    print df_app[['Status_Final','Status_Final Reported','User Name']].head(35)
    print df_app['Status_Final Reported'].unique() # 0=not reported
    #raw_input('Status Final')
    
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

def merge_app_details():
    df_app = pd.read_csv('../../data/edit/app_clean.csv')
    print df_app.columns.tolist()
    df_app = df_app.drop(['Unnamed: 0', 'Unnamed: 0.1', 'Unnamed: 0.1.1'],axis=1)
    df_app = df_app.fillna('')
    
    df_details = pd.read_csv('../../data/edit/df_details_dummy_cleaned.csv')
    df_details = df_details.drop(['Unnamed: 0', 'Unnamed: 0.1','level_0'],axis=1)
    df_details = df_details.fillna('')
    print df_details.columns.tolist()
    
    list = ['inner','outer','left','right']
    for var in list:
        df = df_app.merge(df_details,on=['User Name'],how='{}'.format(var)).reset_index()
        print var, df['User Name'].nunique()
    
    df_sample = df_app.merge(df_details,on=['User Name'],how='inner').reset_index()
    print df_sample.columns.tolist()
    list = ['level_0']
    df_sample = df_sample.drop(list, axis=1)
    df_sample = df_sample.rename(columns={'LSAT_y':'LSAT'})
    print 'df_sample', df_sample['User Name'].nunique(), df_sample.columns.tolist()
    
    df_sample.to_csv('../../data/edit/df_app_details.csv')
    return 

def gen_samples():
    df_sample = pd.read_csv('../../data/edit/df_app_details.csv')
    df_sample = df_sample.fillna('')
    list = ['Status_Final','Status_Final Reported','Attend']
    for var in list:
        df_sample[var] = df_sample[var].astype(str)
    df_sample['Year'] = df_sample['Year'].astype(int)
    print len(df_sample)
    df_sample = df_sample[(df_sample['Year']>=2006) & (df_sample['Year']<=2012)]
    print len(df_sample)
    df_sample = df_sample[(df_sample['ED']!=1) & (df_sample['SP']!=1)]
    print len(df_sample)
    
    #====== Reformat Values ========#
    df_sample['Gender copy'] = df_sample['Gender']
    df_sample['Gender'] = np.nan
    df_sample.loc[df_sample['Gender copy']=='Male','Gender'] = 1.0
    df_sample.loc[df_sample['Gender copy']=='Female','Gender'] = 0.0
    
    race_list = ['white', 'asian and pacific islander', 'african', 
                 'Mixed, probably not urm', 'hispanic', 'mexican', 
                 'puerto rican', 'Native American or alaskan',
                 'LSAT','GPA','LSAT 1','LSAT 2', 'LSAT 3','Degree GPA','LSDAS GPA',
                 'Decision_delta']
    for item in race_list:
        df_sample.loc[df_sample[item]=='',item] = np.nan
    
    df_sample.loc[df_sample['Decision_delta']<=0, 'Decision_delta'] = np.nan
    
    # 'LSAT' is exactly the same as 'LSAT 1'
    df_sample['LSAT'] = df_sample[['LSAT','LSAT 1','LSAT 2', 'LSAT 3']].max(axis=1) 
    print df_sample['LSAT'].describe()
    
    # 'GPA' is exactly the same as 'GPA \cup LSDAS GPA'
    print df_sample['GPA'].astype(float).describe()
    df_sample.loc[df_sample['GPA'].isnull(),'GPA'] = df_sample['LSDAS GPA']
    print df_sample['GPA'].astype(float).describe()
    
    # df_sample['Sent_delta'].notnull() is equivalent to df_sample['Sent']!='' to df_sample
    print len(df_sample[df_sample['Sent_delta'].notnull()])
    print len(df_sample[df_sample['Sent']!=''])
    print len(df_sample) # The three sizes are all the same
    
    # Major: Add up more than 100%, as there are many double-majors
    major_list = ['social sciences', 'arts & humanities', 'business & management', 
                  'natural sciences', 'engineering', 'health professions','other']
    for item in major_list:
        df_sample[item] = df_sample[item].astype(float)    
    df_sample['major sum'] = df_sample[['social sciences', 'arts & humanities', 'business & management', 
                  'natural sciences', 'engineering', 'health professions','other']].sum(axis=1)
    for item in major_list:
        df_sample.loc[df_sample['major sum']==0., item] = np.nan
    df_sample['stem & others'] = df_sample['natural sciences']+ df_sample['engineering'] + \
                                 df_sample['health professions']+df_sample['other']
    df_sample.loc[df_sample['stem & others']>1.0,'stem & others'] = 1.0                            
    
    # College Name or Types
    print df_sample['group'].unique()
    print df_sample['groups'].unique()
    group_list = ['national_univ','national_lac','south_univ','south_college',
                  'midwest_univ','western_univ','hbcu','north_univ','midwest_college',
                  'eng_nodoctorate','north_college']
    groups_list = ['neutral','positive','foreign','bad','bad_school']
    for item in group_list:
        print item, len(df_sample[df_sample['group']==item])
    for item in groups_list:
        print item, len(df_sample[df_sample['groups']==item])
    
    college_list = ['Ranked Nationally','Ranked Regionally','Described Positively',
                    'Described Negatively','Described Neutrally'] #,'Foreign' less than 1%
    for item in college_list:
        df_sample[item] = 0.0
    df_sample.loc[(df_sample['group']=='national_univ') | (df_sample['group'] == 'national_lac'),'Ranked Nationally'] = 1.0
    df_sample.loc[(df_sample['group']=='south_univ')|(df_sample['group']=='south_college')
                 |(df_sample['group']=='midwest_univ')|(df_sample['group']=='midwest_college')
                 |(df_sample['group']=='western_univ')|(df_sample['group']=='north_univ')
                 |(df_sample['group']=='hbcu')|(df_sample['group']=='eng_nodoctorate'),
                 'Ranked Regionally'] = 1.0
    df_sample.loc[df_sample['groups']=='positive','Described Positively'] = 1.0
    df_sample.loc[df_sample['groups']=='bad','Described Negatively'] = 1.0
    df_sample.loc[df_sample['groups']=='neutral','Described Neutrally'] = 1.0
    for item in college_list:
        df_sample.loc[df_sample[['Ranked Nationally','Ranked Regionally','Described Positively',
                             'Described Negatively','Described Neutrally']].max(axis=1)==0.0,
                             item] = np.nan
    
    df_sample['College types reported'] = 0.0                      
    df_sample.loc[df_sample[['Ranked Nationally','Ranked Regionally','Described Positively',
                             'Described Negatively','Described Neutrally']].max(axis=1)>0.0,
                             'College types reported'] = 1.0
    
    
    # Law School Rankings
    df_sample.loc[df_sample['rank_cross']==0.0, 'rank_cross'] = np.nan
    df_sample['rank_2010_cp'] = df_sample['rank_2010']
    df_sample.loc[df_sample['rank_2010_cp']=='','rank_2010_cp'] = np.nan
    df_sample['unranked_2010'] = 0.0
    df_sample.loc[df_sample['rank_2010_cp'].isnull(),'unranked_2010'] = 1.0
    
    # College Rankings
    df_sample['rank'] = df_sample['rank'].astype(str)
    print df_sample['rank'].unique()
    df_sample = df_sample.rename(columns={'rank':'college rank'})
    list_rank_new = df_sample['college rank'].unique()
    for index, item in enumerate(list_rank_new):
        if '-' in item:
           stt = item.split('-',1)[0]
           end = item.split('-',1)[1]
           print stt, end
           list_rank_new[index] = 0.5*(float(stt)+float(end))
        elif 'Unranked' in item:
           list_rank_new[index] = 300.0
        elif item == '':
           list_rank_new[index] = np.nan
        else:
           list_rank_new[index] = float(item)
    print list_rank_new
    list_rank_old = df_sample['college rank'].unique()
    for index, item in enumerate(list_rank_old):
        df_sample.loc[df_sample['college rank']==item,'college rank']=list_rank_new[index]
    
    # College Type : Private/Public
    print df_sample['public'].unique()
    df_sample.loc[df_sample['public']=='False','public'] = '0.0'
    df_sample.loc[df_sample['public']=='True','public'] = '1.0'
    df_sample['public'] = pd.to_numeric(df_sample['public'], errors='coerce')
    
    # College Tiers: 
    list_quantile = [.25, .5, .75]
    list_scale = ['Ranked Nationally','Ranked Regionally']
    for item in list_scale:
        df_temp = df_sample[df_sample[item] == 1.0]
        print df_temp['college rank'].describe()
        print df_temp['college rank'].quantile(list_quantile) 
    list_tier = ['National top 5','National top 6-20','National top 21-50','National below 51']
    thresholds = [[0.0,5.0],[6.0,20.0],[21.0,50.0],[51.0,1000.0]]
    for index, item in enumerate(list_tier):
        df_sample[item] = np.nan
        df_sample.loc[df_sample['Ranked Nationally']==1.0,item] = 0.0
        df_sample.loc[(df_sample['college rank']>=thresholds[index][0]) & (df_sample['college rank']<=thresholds[index][1]),item] = 1.0
        print item,df_sample[item].agg(['mean','sum'])
    
    # Law School Tiers:
    print df_sample.columns.tolist()
    df_sample['Law unranked'] = df_sample['unranked_2010']
    list_tier = ['Law unranked','Law top 14','Law top 15-50','Law below 51']
    thresholds = [[0.0,14.0],[14.0,50.0],[50.0,1000.0]]
    print df_sample['Law unranked'].agg(['mean','sum'])
    for index, item in enumerate(list_tier[1:]):
        df_sample[item] = 0.0
        df_sample.loc[(df_sample['rank_2010_cp']>thresholds[index][0]) & (df_sample['rank_2010_cp']<=thresholds[index][1]),item] = 1.0
        print df_sample[item].agg(['mean','sum'])
        
    # URM race and ethnicity:
    df_sample['minority'] = 0.0
    df_sample.loc[(df_sample['african']==1.0)|(df_sample['mexican']==1.0)
                 |(df_sample['puerto rican']==1.0)|(df_sample['Native American or alaskan']==1.0),
                 'minority'] = 1.0
    list_race = ['white', 'asian and pacific islander', 'Mixed, probably not urm', 'hispanic', 'minority']
    for index, item in enumerate(list_race):
        print df_sample[item].agg(['mean','sum'])
    
    # EC 
    softs = ['EC at all','Athletic/Varsity', 'Community/Volunteer', 'Greek', 'Leadership', 
             'Legal Work Experience', 'Military',  'Non-legal Internship', 'Legal Internship',
             'Non-legal Work Experience', 'Overseas', 'Strong Letters', 'Student Societies']
    for index, item in enumerate(softs):
        df_sample.loc[df_sample[item]=='',item] = np.nan
        print len(df_sample[df_sample[item].notnull()]),df_sample[item].agg(['mean','sum'])
    
    # Remove duplicate rows
    df_sample.drop_duplicates(subset=['User Name','Law School'],keep='first',inplace=True)
    
    #=== Export List of Law Schools ===# (App Open Dates)
    df_law_unique2 = pd.DataFrame(df_sample['Law School'].unique())
    df_law_unique2.to_csv('../../data/edit/list_law_schools2.csv')
    
    #=== Merge Back School Characteristics ===#
    df_school = pd.read_csv('../../data/edit/school_char.csv')
    df_school = df_school[['Law School','opening dates delta']]
    
    df_sample = df_sample.merge(df_school,on=['Law School'],how='left').drop_duplicates().reset_index()
    
    print df_sample.columns.tolist()
    
    #====== Application Sample: Samples with Application Dates and Decisions =====#
    df_all_samples = {}
    # Sample 1: Application Dates
    df_all_samples['a1'] = df_sample[(df_sample['Sent_delta'].notnull())]
    print len(df_all_samples['a1']) #139045 #128662

    # Sample 2: Sample 1 + Non-Trivial Decision Results (at least accepted/rejected/waiting listed by one school)
    df_all_samples['a2'] = df_all_samples['a1'][df_all_samples['a1']['Status_Final Reported']!='0']
    
    #====== Characteristics Sample: Application Samples with Characteristics ======#
    # Sample 1: GPA + LSAT
    df_all_samples['c1'] = df_all_samples['a2'][(df_all_samples['a2']['GPA'].notnull()) & (df_all_samples['a2']['LSAT'].notnull()) ]
    # Sample 2: Master Sample 2 + Gender + Race
    df_all_samples['c2'] = df_all_samples['c1'][(df_all_samples['c1']['Gender'].notnull()) & (df_all_samples['c1']['Race2']!='')]
    # Sample 3: Master Sample 3 + College Type 
    df_all_samples['c3'] = df_all_samples['c2'][df_all_samples['c2']['College types reported']==1.0]
    # Sample 4: Master Sample 3 + Major 
    df_all_samples['c4'] = df_all_samples['c3'][df_all_samples['c3']['major sum']>0.]
    # Sample 5: Master Sample 4 + Years out of Undergrad
    df_all_samples['c5'] = df_all_samples['c4'][df_all_samples['c4']['Years out of Undergrad']!='']
    # Sample 6: Master Sample 5 + State
    df_all_samples['c6'] = df_all_samples['c5'][df_all_samples['c5']['State']!='']
    # Sample 7: Master Sample 4 + EC
    df_all_samples['c7'] = df_all_samples['c4'][df_all_samples['c4']['Greek'].notnull()]
    
    
    #====== Decision Dates Sample: Characteristics Samples with Decision Dates ======#
    for c in ['1','2','3','4','5','6','7']:
        df_all_samples['d{}'.format(c)] = df_all_samples['c{}'.format(c)][df_all_samples['c{}'.format(c)]['Decision_delta']>0.]
        
    #====== Enrollment Sample: Characteristics Samples with Enrollment Outcomes =====#
    for c in ['1','2','3','4','5','6','7']:
        df_all_samples['e{}'.format(c)] = df_all_samples['c{}'.format(c)][df_all_samples['c{}'.format(c)]['Attend']!='-1']
    
    #====== Print Sample Sizes ========#
    print '----------Application sample size----------'
    for c in ['1','2'] :
        df = df_all_samples['a{}'.format(c)]
        print c,len(df),df['User Name'].nunique()
    
    print '----------Characteristics sample size----------'
    for c in ['1','2','3','4','5','6','7'] :
        df = df_all_samples['c{}'.format(c)]
        print c,len(df),df['User Name'].nunique()
        
    print '----------Decision Dates sample size----------'
    for c in ['1','2','3','4','5','6'] :
        df = df_all_samples['d{}'.format(c)]
        print c,len(df),df['User Name'].nunique()

    print '----------Enrollment sample size----------'
    for c in ['1','2','3','4','5','6','7'] :
        df = df_all_samples['e{}'.format(c)]
        print c,len(df),df['User Name'].nunique()   
    
    #====== Export Samples ========#
    df_all_samples['c1'].to_csv('../../data/edit/sample_c1_py.csv')
    return df_all_samples