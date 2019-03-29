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

def apply_only_on_weekends(str_sample):
    # This has to use c-series sample. d-series sample yields wrong results!
    # To classify d-series users, use c-series sample, and merge to d-series user-list
    # In d-series samples, users' application data is incomplete - some apps are omitted
    # Thus we don't know whether an user only submits on weekends, or if in multiple rounds
    df_raw = pd.read_csv('../../data/edit/df_all_samples_{}.csv'.format(str_sample))

    df = df_raw.groupby(['User Name','Sent_delta'])['Sent_weekday'].mean().reset_index()
    df.loc[df['Sent_weekday']<5.0,'Sent_weekday'] = 0.0 # Weekdays
    df.loc[df['Sent_weekday']>=5.0,'Sent_weekday'] = 1.0 # Weekends
    df = df.groupby(['User Name'])['Sent_weekday'].agg(['mean','count']).reset_index()
    
    x = [len(df), len(df[df['mean']==1.0]), len(df[(df['count']>1.0) & (df['mean']==1.0)])]
    df = pd.DataFrame(x, columns=['Number of Applicants'])
    rows = ['Total','Only Applying at Weekends','And for Multiple Times']
    cols = df.columns.tolist()
    df = df.assign(Variable=rows)
    df2tex(df, '../../model/tables/','weekends_{}.tex'.format(str_sample), "%8.2f", 0, cols, ['Variable'], cols)

    return


def LSAT_release():
    df_release = pd.read_csv('../../data/various/LSAT dates scores/LSAT_release_dates.csv')
    for item in ['cycle_starts','official','actual']:
        df_release[item]=pd.to_datetime(df_release[item], errors = 'coerce') 
        df_release['{} delta'.format(item)] = np.nan
    for index, row in df_release.iterrows():
        for item in ['official','actual']:
            df_release.loc[index,'{} delta'.format(item)] = (row['{}'.format(item)]-row['cycle_starts'])  / np.timedelta64(1,'D')
    df_release = df_release[['Year','official delta','actual delta']]
    
    df_dic = {}
    for num in [0,1,2]:
        df_dic[num] = df_release.groupby(['Year'])[['official delta','actual delta']].nth(num).reset_index()\
                      .rename(columns={'official delta':'official delta {}'.format(num+1),'actual delta':'actual delta {}'.format(num+1)})
    df = pd.concat([df_dic[0],df_dic[1].drop(['Year'],axis=1)],axis=1)
    df_release = pd.concat([df,df_dic[2].drop(['Year'],axis=1)],axis=1)
    df_release.to_csv('../../data/edit/LSAT_release_delta.csv')
    return 

def LSAT_release_df_all():
    df_release = pd.read_csv('../../data/edit/LSAT_release_delta.csv')
    
    df_c1 = pd.read_csv('../../data/edit/df_all_samples_c1.csv')
    df_c1 = df_c1[['User Name','Sent_delta','Year']]
    df_all_c1 = df_c1.merge(df_release,on=['Year'],how='left').drop_duplicates().reset_index()
    df_all_lsat_c1 = df_all_c1.groupby(['User Name','Sent_delta'])['actual delta 1','actual delta 2','actual delta 3',
                                       'official delta 1','official delta 2','official delta 3'].mean().reset_index()       
    df_all_lsat_c1.to_csv('../../data/edit/df_all_lsat_c1.csv')
    return df_all_lsat_c1

def LSAT_release_did_stats(df_in,intvl,id_list_str):
    # df_in: each row corresponds to a user*round. contains all two LSAT release dates
    # id_list_str: can be ['User Name'], or ['User Name','gp']
    dic_did_lsat={}
    dic_did_lsat_only={}
    for typ in ['actual','official']:
        for item in [1,2]:
            df_in['Diff {} LSAT {}'.format(typ,item)] = df_in['Sent_delta'] - df_in['{} delta {}'.format(typ,item)]
            
    choice_list = ['Diff actual LSAT 1','Diff actual LSAT 2','Diff official LSAT 1','Diff official LSAT 2']
    df_user_min = df_in.groupby(id_list_str)[choice_list].agg('min').reset_index()
    df_user_max = df_in.groupby(id_list_str)[choice_list].agg('max').reset_index()
    for item in choice_list:
        df_user_min = df_user_min.rename(columns={item:item + ' min'})
        df_user_max = df_user_max.rename(columns={item:item + ' max'}) 
    df_user = df_user_min.merge(df_user_max,on=id_list_str,how='left').reset_index()
    
    df_count = {}
    for item in [1,2]:
        for typ in ['actual','official']:
            # Applied Immediately After LSAT
            df_count['After {}{}'.format(typ,item)] = df_in[(df_in['Diff {} LSAT {}'.format(typ,item)]>=0.0) &
                       (df_in['Diff {} LSAT {}'.format(typ,item)]<=intvl)]
            dic_did_lsat['After {} LSAT {} release'.format(typ,item)]=df_count['After {}{}'.format(typ,item)]['User Name'].nunique()
            
            # Applied Immediately Before LSAT
            df_count['Before {}{}'.format(typ,item)] = df_in[(df_in['Diff {} LSAT {}'.format(typ,item)]>=-intvl) &
                       (df_in['Diff {} LSAT {}'.format(typ,item)]<=0.0)]
            dic_did_lsat['Before {} LSAT {} release'.format(typ,item)]=df_count['Before {}{}'.format(typ,item)]['User Name'].nunique()

            # Applied ONLY Immediately After LSAT
            df_count['Only After {}{}'.format(typ,item)] = df_user[(df_user['Diff {} LSAT {} min'.format(typ,item)]>=0.0) &
                         (df_user['Diff {} LSAT {} max'.format(typ,item)]<=intvl)]
            dic_did_lsat_only['After {} LSAT {} release'.format(typ,item)]=df_count['Only After {}{}'.format(typ,item)]['User Name'].nunique()
            
            # Applied ONLY Immediately Before LSAT
            df_count['Only Before {}{}'.format(typ,item)] = df_user[(df_user['Diff {} LSAT {} min'.format(typ,item)]>=-intvl) &
                         (df_user['Diff {} LSAT {} max'.format(typ,item)]<=0.0)]
            dic_did_lsat_only['Before {} LSAT {} release'.format(typ,item)]=df_count['Only Before {}{}'.format(typ,item)]['User Name'].nunique()
        
    for key, value in df_count.iteritems():
        df_count[key] = pd.DataFrame(value['User Name'].unique(),columns=['User Name'])
    
    for typ in ['actual','official']:
        dic_did_lsat['After Both {} LSAT release'.format(typ)] = len( df_count['After {}1'.format(typ)].merge(df_count['After {}2'.format(typ)],
                     on='User Name',how='inner')  )
        dic_did_lsat_only['After Both {} LSAT release'.format(typ)] = len( df_count['Only After {}1'.format(typ)].merge(df_count['Only After {}2'.format(typ)],
                     on='User Name',how='inner')  )
        dic_did_lsat['Total Users'] = df_user['User Name'].nunique()
        dic_did_lsat_only['Total Users'] = df_user['User Name'].nunique()

    return dic_did_lsat, dic_did_lsat_only

def LSAT_release_export_stats(dic_lsat,intvl,filename):
    typ = 'actual'
    x = np.array([[dic_lsat['Before {} LSAT 1 release'.format(typ)],dic_lsat['Before {} LSAT 2 release'.format(typ)]],
                  [dic_lsat['After {} LSAT 1 release'.format(typ)],dic_lsat['After {} LSAT 2 release'.format(typ)]],
                  [dic_lsat['Total Users'],dic_lsat['After Both {} LSAT release'.format(typ)]]])
    df = pd.DataFrame(x,columns=['LSAT(October)','LSAT(December)'])
    
    rows=['{} Days Before'.format(intvl),'{} Days After'.format(intvl),'Total \& Double-Count']
    cols = df.columns.tolist()
    df = df.assign(Variable=rows)
    df2tex(df, '../../model/tables/','{}.tex'.format(filename), "%8.2f", 0, cols, ['Variable'], cols)
    return
