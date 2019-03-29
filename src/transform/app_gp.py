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
from df2tex import df2tex

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch

'''
Useless Codes! Everything here has been replaced by better codes (objected oriented)
at Python file "app_type_round.py"
'''

def mark_groups_by_app_patterns(df_raw):
    # Initialize Target Datasets
    df_rounds_gp = {}
    df_user_gp = {}
    
    # Initialize Seed Datasets
    df_rounds = df_raw.groupby(['User Name','Application Time'])['Number of Offers','Number of Waitlists','Number of Rejections'].mean().reset_index()
    df_user = df_rounds.groupby(['User Name'])['Application Time'].agg(['max','min','count']).reset_index()
    print 'group all',len(df_user),len(df_rounds)
    
    # Mark those applying only once
    df_user_group1 = df_user[df_user['count']==1]
    df_user_group1['group'] = 1.0
    df_user_gp['gp1'] = df_user_group1
    df_rounds_gp['gp1'] = df_rounds.merge(df_user_group1[['User Name']],on='User Name',how='right').drop_duplicates().reset_index()
    print 'group 1',len(df_user_gp['gp1']),len(df_rounds_gp['gp1'])
    
    # Take Remaining Dataset
    df_user_rm = df_user[df_user['count']>1]
    df_rounds_rm = df_rounds.merge(df_user_group1,on=['User Name'],how='left').reset_index().drop(['max','min','count'],axis=1).drop_duplicates()
    df_rounds_rm = df_rounds_rm[df_rounds_rm['group']!=1.0]
    print 'non-group 1',len(df_user_rm),len(df_rounds_rm)
    
    # Mark those applying more than once but all before hearing any decisions
    df_tmp = df_rounds_rm.groupby(['User Name'])['Number of Offers','Number of Waitlists','Number of Rejections'].max().reset_index()
    df_tmp_group2 = df_tmp[ (df_tmp['Number of Offers']==0.0) & (df_tmp['Number of Waitlists']==0.0) & (df_tmp['Number of Rejections']==0.0)]
    df_user_gp['gp2'] = df_user.merge(df_tmp_group2[['User Name']],on='User Name',how='right').drop_duplicates().reset_index()
    df_rounds_gp['gp2'] = df_rounds.merge(df_tmp_group2[['User Name']],on='User Name',how='right').drop_duplicates().reset_index()
    print 'group2',len(df_user_gp['gp2']),len(df_rounds_gp['gp2'])
    
    # Mark those applying after receiving offers
    df_tmp_group3 = df_tmp[df_tmp['Number of Offers']>0.0]
    df_user_gp['gp3'] = df_user.merge(df_tmp_group3[['User Name']],on='User Name',how='right').drop_duplicates().reset_index()
    df_rounds_gp['gp3'] = df_rounds.merge(df_tmp_group3[['User Name']],on='User Name',how='right').drop_duplicates().reset_index()
    print 'group3',len(df_user_gp['gp3']),len(df_rounds_gp['gp3'])
    
    # Mark those applying more than once but not after receiving offers
    df_tmp_group4 = df_tmp[ (df_tmp['Number of Offers']==0.0) & ((df_tmp['Number of Waitlists']>0.0) | (df_tmp['Number of Rejections']>0.0))]
    df_user_gp['gp4'] = df_user.merge(df_tmp_group4[['User Name']],on='User Name',how='right').drop_duplicates().reset_index()
    df_rounds_gp['gp4'] = df_rounds.merge(df_tmp_group4[['User Name']],on='User Name',how='right').drop_duplicates().reset_index()
    print 'group4',len(df_user_gp['gp4']),len(df_rounds_gp['gp4'])

    return df_rounds_gp, df_user_gp

def summary_stats_by_group(df_raw, df_user_gp):
    for var in [1,2,3,4]:
        df = df_user_gp['gp{}'.format(var)][['User Name']].merge(df_raw,on='User Name',how='left').drop_duplicates().reset_index()
        print df.columns.tolist()
        print 'gp{}'.format(var), df['rank'].describe(),df['ranked'].describe()  
    return

def new_apps_vs_best_offer(df_user_gp,df_raw):
    # Group 3: Submit new apps to better schools than best offer
    df = df_user_gp['gp3'][['User Name']].merge(df_raw,on='User Name',how='left').drop_duplicates().reset_index()
    print df.columns.tolist()
    print 'Gp3: All apps',len(df)
    df = df[df['Number of Offers']>0.0]
    v1= len(df) #'Apps sent after arrival of offers'
    v2= len( df[df['rank']<df['Best Offer']] ) #'Strictly better, best offer ranked'
    v3= len( df[(df['Best Offer'].isnull()) & (df['rank'].notnull())]) #'Strictly better, best offer unranked'
    v4= len( df[df['rank']==df['Best Offer']] ) #'Equal, best offer ranked'
    v5= len( df[(df['Best Offer'].isnull()) & (df['rank'].isnull())]) #'Equal, best offer unranked'
    v6= len( df[ (df['rank']>df['Best Offer']) & (df['rank']<=df['Best Offer']+5.0) ]) #'Slightly worse'
    
    label = ['Sent After Arrival of Offers', 'Ranking Higher than the Best Offer at Hand (Ranked)',
             'Ranking Higher than the Best Offer at Hand (Unranked)', 'Ranking Equal to the Best Offer at Hand (Ranked)',
             'Ranking Equal to the Best Offer at Hand (Unranked)' ]
    d = {'Apps':label,'Obs':[v1, v2, v3, v4, v5],'Percent':[100.0,100.0*v2/v1,100.0*v3/v1,100.0*v4/v1,100.0*v5/v1]}
    df_cpr = pd.DataFrame(data=d)
    return df_cpr

def new_apps_median_apps_best_offer(df_user_gp,df_raw):
    # Group 3: Are Best Offers Even Worse than Median Apps?
    df = df_user_gp['gp3'][['User Name']].merge(df_raw,on='User Name',how='left').drop_duplicates().reset_index()
    print df.columns.tolist()
    print 'Gp3: All apps',len(df)
    df = df[df['Number of Offers']>0.0]
    v1= len(df)
    v2= len( df[df['Best Offer']<df['Median App']] ) #'Strictly better, best offer ranked'
    v3= len( df[(df['Median App'].isnull()) & (df['Best Offer'].notnull())]) #'Strictly better, best offer unranked'
    v4= len( df[df['Best Offer']==df['Median App']] ) #'Equal, best offer ranked'
    v5= len( df[(df['Median App'].isnull()) & (df['Best Offer'].isnull())]) #'Equal, best offer unranked'
    v6= len( df[ (df['Best Offer']>df['Median App']) & (df['Best Offer']<=df['Median App']+5.0) ]) #'Slightly worse'
    print v1,v2,v3
    print v4,v5,v6
    
    #df = df[df['Number of Offers']>0.0]


def app_group_masterboard(df_user_gp, df_rounds_gp,df_raw):
    # Construct a User-App-Group Table
    df_user_gp_all = pd.DataFrame()
    df_rounds_gp_all = pd.DataFrame()
    for var in [1,2,3,4]:
        df0 = df_user_gp['gp{}'.format(var)][['User Name']]
        df0['gp'] = var
        df_user_gp_all = df_user_gp_all.append(df0)
        
        df1 = df_rounds_gp['gp{}'.format(var)][['User Name']]
        df1['gp'] = var
        df_rounds_gp_all = df_rounds_gp_all.append(df1)
        
        df_raw_gp_all = df_raw.merge(df_rounds_gp_all,on='User Name',how='left').drop_duplicates().reset_index()
    return df_user_gp_all, df_rounds_gp_all, df_raw_gp_all

def calculate_gaps(df_in):
    df = df_in.sort_values(by=['User Name','Application Time'])
    shifted = df[['User Name','Application Time']].groupby('User Name').shift(1)
    df = df.join(shifted.rename(columns=lambda x: x+' lag'))
    df['gap'] = df['Application Time'] - df['Application Time lag']
    print df['gap'].describe()
    return df

def new_apps_post_offers(df_in):
    df_pre_offer = df_in[df_in['Number of Offers']==0.0]
    df_get_offer = df_in[df_in['Number of Offers']>0.0].groupby(['User Name']).nth(0)
    df_post_offer = df_in[df_in['Number of Offers']>0.0].groupby(['User Name']).apply(lambda x:x.iloc[1:])    
    print 'pre_offer_gaps',df_pre_offer['gap'].describe()
    print 'get_offer_gaps',df_get_offer['gap'].describe()
    print 'post_offer_gaps',df_post_offer['gap'].describe()
    
    print 'pre_offer_ranks',df_pre_offer['rank'].describe()
    print 'get_offer_ranks',df_get_offer['rank'].describe()
    print 'post_offer_ranks',df_post_offer['rank'].describe()
    return df_pre_offer,df_get_offer,df_post_offer
    
def simulate_stats():
    # Load dataset
    df_raw = pd.read_csv('../../data/edit/simulate_outputs.csv')
      
    df_rounds_gp, df_user_gp = mark_groups_by_app_patterns(df_raw)
    summary_stats_by_group(df_raw,df_user_gp)
    df_apps_offer_ranks = new_apps_vs_best_offer(df_user_gp,df_raw)
    new_apps_median_apps_best_offer(df_user_gp,df_raw)
    df_user_gp_all, df_rounds_gp_all, df_raw_gp_all = app_group_masterboard(df_user_gp,df_rounds_gp,df_raw)
    
    df_gaps = {}
    for v in [2,3,4]:
        df_gaps['gp{}'.format(v)] = calculate_gaps(df_rounds_gp['gp{}'.format(v)])
    
    df_pre_offer, df_get_offer, df_post_offer = new_apps_post_offers(df_gaps['gp3'])
   
    # Merge App-Group Affiliations to Main Data
    df_main = pd.read_csv('../../data/edit/qpig_dynamic_sample.csv')
    df_all = df_main.merge(df_user_gp_all,on='User Name',how='left').drop_duplicates().reset_index()
    
    return df_all,df_user_gp_all, df_rounds_gp_all,df_raw_gp_all,\
           df_pre_offer, df_get_offer, df_post_offer, df_apps_offer_ranks
           
def pct_gp_over_time(df_all):
    df = df_all.groupby(['gp','Year'])['User Name'].count().reset_index()
    df_dic = {}
    df_wide = pd.DataFrame()
    for yr in range(df['Year'].min(), df['Year'].max()+1):
        df_dic[yr] = df[df['Year']==yr].reset_index()
        df_dic[yr]['User Name'] = df_dic[yr]['User Name']/df_dic[yr]['User Name'].sum()*100.0
        df_dic[yr] = df_dic[yr].rename(columns={'User Name':'{}'.format(yr)})
        df_wide = pd.concat([df_wide,df_dic[yr][['{}'.format(yr)]]],axis=1)
    #df_wide = df_wide.assign(Group = ['Group 1','Group 2','Group 3','Group 4'])
    return df_wide

def calculate_simu_stats(df_user_gp_all, df_rounds_gp_all, df_all,df_raw_gp_all,
                         df_pre_offer, df_get_offer,df_post_offer,df_apps_offer_ranks):
    df_stats_dic = {}
    df_stats = pd.DataFrame()
    for key, df_v in {'Users':df_user_gp_all, 'Rounds':df_rounds_gp_all, 'Apps':df_all}.iteritems():
        gr_ct = df_v.groupby(['gp']).size()
        gr_pct = gr_ct/len(df_v)*100.0
        df_stats = pd.concat([df_stats,gr_ct],axis = 1).rename(columns={0:'\# of {}'.format(key)})
        df_stats = pd.concat([df_stats,gr_pct], axis = 1).rename(columns={0:'\% of {}'.format(key)})
    df_stats = df_stats.reset_index().rename(columns={'gp':'App Groups'})
    df_stats_dic['stats_group_size'] = df_stats
    
    df_tmp = df_raw_gp_all.groupby(['gp','User Name','Application Time'])['ranked'].count().reset_index()
    df_tmp = df_tmp.groupby(['gp','User Name'])['Application Time'].agg(['min','max','count']).reset_index()
    df_tmp['Span'] = df_tmp['max'] - df_tmp['min']+1.0
    df_stats = df_tmp.groupby(['gp'])[['min','Span','count']].mean().reset_index()
    df_stats_dic['stats_group_time'] = df_stats
    
    df_stats = df_raw_gp_all.groupby(['gp'])[['rank','ranked']].mean().reset_index()
    df_stats['ranked'] = df_stats['ranked']*100.0
    df_stats_dic['stats_group_rank'] = df_stats
    
    df_stats = pd.DataFrame()
    for key, df_v in {'pre':df_pre_offer,'get':df_get_offer,'post':df_post_offer}.iteritems():
        df_tmp = pd.DataFrame(df_v['gap'].agg(['mean','std','median'])).rename(columns= lambda x: '{} '.format(key)+x)
        df_stats = pd.concat([df_stats,df_tmp],axis=1)
    df_stats_dic['stats_group_gap'] = df_stats.transpose()
        
    df_stats_dic['stats_group_best'] = df_apps_offer_ranks
    
    df_stats_dic['group_pct_over_time'] = pct_gp_over_time(df_all)
    
    return df_stats_dic


def export_simu_stats(df_stats_dic):
    complex_row_col = {
            'stats_group_size':[['Group 1','Group 2','Group 3','Group 4'],{'':''},
                                ['\# of Users','\% of Users','\# of Rounds','\% of Rounds','\# of Apps','\% of Apps']],
            'stats_group_time':[['Group 1','Group 2','Group 3','Group 4'],{'min':'Avg Days Taken to 1st App','Span':'Avg Length of Span','count':'Avg Number of Rounds'},
                                ['Avg Days Taken to 1st App','Avg Length of Span','Avg Number of Rounds']],
            'stats_group_rank':[['Group 1','Group 2','Group 3','Group 4'],{'rank':'Avg Ranks','ranked':'Pct Ranked'},
                                ['Avg Ranks','Pct Ranked']],
            'stats_group_gap':[['Before 1st Offer','After 1st Offer','Between'],{'mean':'Mean','std':'SD','median':'Median'},
                               ['Mean','SD','Median']],
            'stats_group_best':[['Sent After Arrival of Offers', 'Ranking Higher than the Best Offer at Hand (Ranked)',
                                 'Ranking Higher than the Best Offer at Hand (Unranked)', 'Ranking Equal to the Best Offer at Hand (Ranked)',
                                 'Ranking Equal to the Best Offer at Hand (Unranked)' ],{'':''},
                                ['Obs','Percent']],
            'group_pct_over_time':[['Group 1','Group 2','Group 3','Group 4'],{'':''},
                                ['2006','2007','2008','2009','2010','2011','2012']]
            }
    for key, df in df_stats_dic.iteritems():
        df = df.assign(Variable=complex_row_col[key][0]) 
        df = df.rename(columns=complex_row_col[key][1])
        cols = complex_row_col[key][2]
        df = df[cols+['Variable']]
        df2tex(df, '../../model/tables/','{}.tex'.format(key), "%8.2f", 0, cols, ['Variable'], cols)
    return

'''
# Redundant, Wrong, Useless Craps
def merge3(df0,df1,df2):
    print 'pre-merge length',len(df0)
    df = df0.merge(df1,on='User Name',how='left').drop_duplicates().reset_index()
    df = df.drop('level_0',axis=1).merge(df2,on='Year',how='left').drop_duplicates().reset_index()
    print 'post-merge length',len(df0)
    return df

def LSAT_release_df_gp3(df_pre_offer,df_get_offer,df_post_offer):
    df_release = pd.read_csv('../../data/edit/LSAT_release_delta.csv')
    df_all_compress = df_all.groupby(['User Name'])['Year'].min().reset_index()
    df_pre_offer = merge3(df_pre_offer,df_all_compress,df_release)
    df_get_offer = merge3(df_get_offer,df_all_compress,df_release)
    df_post_offer = merge3(df_post_offer,df_all_compress,df_release) 
    df_pre_offer_app = df_pre_offer.merge(df_all,left_on=['User Name','Application Time'],right_on=['User Name','Sent_delta'],
                                          how='left').reset_index()
    df_get_offer_app = df_get_offer.merge(df_all,left_on=['User Name','Application Time'],right_on=['User Name','Sent_delta'],
                                          how='left').reset_index()
    df_post_offer_app = df_post_offer.merge(df_all,left_on=['User Name','Application Time'],right_on=['User Name','Sent_delta'],
                                          how='left').reset_index()    
    return df_pre_offer,df_get_offer,df_post_offer,df_pre_offer_app,df_get_offer_app,df_post_offer_app
'''