import re
import csv
import json
import urllib
import difflib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict
from df2tex import df2tex

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch


def import_official_app_offer():
    df = pd.read_csv('../../data/LSAC pdf/Law.csv')
    print df.head(20)
    
    # Extract yr and lsac number
    df['yr'] = df['pdfName'].str.split('_',2).str[0]
    df['lsac number'] = df['pdfName'].str.split('_',2).str[1]
    
    # Extract lines of "totals" into a seperate dataset
    df_total = df[(df['LSAT Score']=='Total') | (df['GPA']=='Total') | (df['GPA']=='Totals')]
    df_items = df[(df['LSAT Score']!='Total') & (df['GPA']!='Total') & (df['GPA']!='Totals')]
    
    # Clean non-numerical values for bounds
    print df_items['LSAT Score'].unique()
    print df_items['GPA'].unique()
    LSAT_pairs = {'Below140':'120-140','Below145':'120-145','Below155':'120-155','Below150':'120-150',
                  '149&Below':'120-149','165&Above':'165-180','165+':'165-180','Blank':'-',
                  'Below':'-','NoLSAT':'-'}
    GPA_pairs = {'3.75+':'3.75-4.00','Below2.00':'0.00-2.00','NoGPA':'-','Below2.50':'0.00-2.50',
                 'Below2.75':'0.00-2.75','Below3.0':'0.00-3.00','2.99&Below':'0.00-2.99',
                 'Below3.00':'0.00-3.00','Below2.49':'0.00-2.49','LSATonly':'-'}
    LSAT_pairs_cutoff = {'120-140':'120-139','120-145':'120-144','120-155':'120-154','120-150':'120-149'}
    GPA_pairs_cutoff = {'0.00-2.00':'0.00-1.99','0.00-2.50':'0.00-2.49','0.00-2.75':'0.00-2.74',
                        '0.00-3.00':'0.00-2.99','3.75-4.40':'3.75-4.00','3.0-3.24':'3.00-3.24',
                        '0.10-2.49':'0.00-2.49'}
    for key, value in LSAT_pairs.items():
        df_items.loc[df_items['LSAT Score']==key,'LSAT Score'] = value
    for key, value in LSAT_pairs_cutoff.items():
        df_items.loc[df_items['LSAT Score']==key,'LSAT Score'] = value
    for key, value in GPA_pairs.items():
        df_items.loc[df_items['GPA']==key,'GPA'] = value
    for key, value in GPA_pairs_cutoff.items():
        df_items.loc[df_items['GPA']==key,'GPA'] = value
        
    # Drop Empty values
    df_items = df_items[(df_items['LSAT Score']!='-')&(df_items['GPA']!='-')]
    
    # Export
    print df_items['LSAT Score'].unique()
    print df_items['GPA'].unique()
    
    df_items.to_csv('../../data/edit/Law_items_raw.csv')
    df_total.to_csv('../../data/edit/Law_total_raw.csv')
    return

def split_by_upper_case(s):
    pos = [i for i,e in enumerate(s+'A') if e.isupper()]
    parts = [s[pos[j]:pos[j+1]] for j in xrange(len(pos)-1)]
    parts_str = ' '.join([i for i in parts])
    return parts_str

def remove_digit(s):
    result = ''.join([i for i in s if not i.isdigit()])
    return result
    
def remove_redundant(df,var1,var2):
    df[var1] = df[var2].str.replace('-','').str.replace(',','')\
                       .str.replace("'",'').str.replace("of",'').str.replace('The','')\
                       .str.replace(' the ','').str.replace('School','').str.replace('Law','')\
                       .str.replace('College','').str.replace('University','')\
                       .str.replace('(','').str.replace(')','')
    return df
    
def extract_master_names():
    df_master = pd.read_csv('../../data/edit/df_app_details.csv')    
    df_master_names = pd.DataFrame(df_master['Law School'].unique(),columns=['School Original Master'])
    
    df_master_names = remove_redundant(df_master_names,'School Master','School Original Master')
    
    for var in ['College','University']:
        df_master_names.loc[df_master_names['School Original Master'].str.contains('Boston {}'.format(var)),'School Master'] = 'Boston {}'.format(var)
        df_master_names.loc[(df_master_names['School Original Master'].str.contains('Mississippi')) & 
                            (df_master_names['School Original Master'].str.contains('{}'.format(var))),
                            'School Master' ] = 'Mississippi {}'.format(var)
        
    df_master_names['School Master'] = df_master_names['School Master'].str.lstrip()
    df_master_names.to_csv('../../data/edit/school_lsn_original.csv')
    return df_master_names

def extract_official_app_names():
    df_items = pd.read_csv('../../data/edit/Law_items_raw.csv')
    df_total = pd.read_csv('../../data/edit/Law_total_raw.csv')
    
    # Extract unique values of school names
    df_original = pd.DataFrame(df_items['School'].unique(),columns=['School Original'])
    print df_original
    
    # Extract lsac numbers
    df_lsac_no = df_items.groupby(['School'])['lsac number'].mean().reset_index()
    df_lsac_no = df_lsac_no.rename(columns={'School':'School Original'})

    # Merge school names to lsac numbers
    df_original = df_original.merge(df_lsac_no,on='School Original',how='left').reset_index()
    
    # Clean school names
    df_original['School'] = df_original['School Original'].apply(lambda x: remove_digit(x))
    df_original = remove_redundant(df_original,'School','School')
    
    # Split names by upper cases
    df_original['School'] = df_original['School'].apply(lambda x: split_by_upper_case(x))
    df_original['School'] = df_original['School'].str.replace('S U N Y','SUNY').str.replace('U C L A','UCLA')\
                            .str.replace('S M U','SMU')
    
    for var in ['College','University']:
        df_original.loc[df_original['School Original'].str.contains('Boston{}'.format(var)),'School'] = 'Boston {}'.format(var)
        df_original.loc[(df_original['School Original'].str.contains('Mississippi')) & 
                        (df_original['School Original'].str.contains('{}'.format(var))),
                         'School' ] = 'Mississippi {}'.format(var)
    df_original.to_csv('../../data/edit/school_aba_original.csv')
    return df_original

def match_official_app_names():
    # Extract unique values of school names from main data
    df_master_names = extract_master_names()
    
    # Extract unique values of school names from official App
    df_original = extract_official_app_names()
    
    # Adjusting school names (actually based on fuzzy matching)
    dic_adjust = {'LouisD.BrandeisSchoolofLawattheUniversityofLouisville':'Louisville Brandeis', 
                  'Buffalo':'Buffalo SUNY',
                  'William&MaryLawSchool':'William and Mary Marshall Wythe',
                  'UniversityofNorthCarolinaSchoolofLaw':'North Carolina Chapel Hill',
                  'SMUDedmanSchoolofLaw':'Southern Methodist  Dedman',
                  'UniversityofHoustonLawCenter':'Houston',
                  'TheUniversityofTexasSchoolofLaw':'Texas Austin'}
    for key, value in dic_adjust.items():
        df_original.loc[df_original['School Original'].str.contains(key),'School'] = value
    
    # Fuzzy Matching
    threshold = 0.6
    list_master = df_master_names['School Master'].tolist()
    for index, row in df_original.iterrows():
        best_match = difflib.get_close_matches(row['School'],list_master,cutoff=threshold)
        #df_original.loc[index, 'guess']=';'.join(str(x) for x in best_match)
        if len(best_match) > 0:
            df_original.loc[index,'guess'] = best_match[0]
    df_original.to_csv('../../data/edit/match_school_aba_original.csv')
    
    # Creata a table for school names
    # One lsac number may corresponds to multiple school names
    df_table = df_original.merge(df_master_names,left_on='guess',right_on='School Master',how='left').reset_index()
    df_table_s = df_table[['School Original','School Original Master','lsac number']].rename(columns={'School Original':'School','School Original Master':'Law School'})
    df_table_s.to_csv('../../data/edit/match_school_table_s.csv')
    
    # Remove redundant values in School
    df_table_concise = df_table_s.groupby(['lsac number'])['School','Law School'].first().reset_index()
    df_table_concise.to_csv('../../data/edit/match_school_table_concise.csv')
    return
    
def match_all():
    df_items = pd.read_csv('../../data/edit/Law_items_raw.csv')
    df_total = pd.read_csv('../../data/edit/Law_total_raw.csv')
    df_table = pd.read_csv('../../data/edit/match_school_table_concise.csv')
    
    print df_items.columns.tolist()
    list_both = ['School', 'GPA', 'LSAT Score', 'Apps', 'Adm', 'yr','lsac number']
    
    df_items_all = df_items[list_both].merge(df_table,on=['School','lsac number'],how='left').reset_index()
    df_total_all = df_total[list_both].merge(df_table,on=['School','lsac number'],how='left').reset_index()
    
    df_items_all.to_csv('../../data/edit/Law_items_edit.csv')
    df_total_all.to_csv('../../data/edit/Law_total_edit.csv')
    return

def app_adm_stat_long(df_pool):
    list_identifier1 = ['Law School','lsac number']
    list_identifier2 = ['GPA', 'LSAT Score']
    
    df_sum = df_pool.groupby(list_identifier1)['Apps','Adm'].sum().reset_index().rename(columns={'Apps':'Apps_sum','Adm':'Adm_sum'})
    df_pool = df_pool.merge(df_sum,on=list_identifier1,how='left').reset_index()
    
    df_pool['app_pct'] = df_pool['Apps']/df_pool['Apps_sum']
    df_pool['adm1_pct'] = df_pool['Adm']/df_pool['Apps_sum']
    df_pool['adm2_pct'] = df_pool['Adm']/df_pool['Adm_sum']
    df_pool['select_pct'] = df_pool['Adm']/(df_pool['Apps']+0.00001)
    return df_pool

def official_app_stat_pool():
    df = pd.read_csv('../../data/edit/Law_items_edit.csv')
    
    list_identifier1 = ['Law School','lsac number']
    list_identifier2 = ['GPA', 'LSAT Score']
    
    # Pool all the years
    df_pool = df.groupby(list_identifier1 + list_identifier2)['Apps','Adm'].sum().reset_index()
    
    # Calculate statistics in LONG format (Conducting t-tests)
    df_pool_long = app_adm_stat_long(df_pool)
    df_pool_long.to_csv('../../data/edit/df_pool_long.csv')
    
    # Reshape statistics to WIDE format (Presenting results)
    list_stat = ['app_pct','adm1_pct','adm2_pct','select_pct']
    df_pool_long['LSAT str'] = 'LSAT ' + df_pool_long['LSAT Score'].astype(str)
    list_lsac_no = df_pool_long['lsac number'].unique().tolist()
    
    df_pool_sqr = pd.DataFrame()
    for item in list_stat: 
        for num in list_lsac_no:
            df = df_pool_long[df_pool_long['lsac number'] == num]
            df_sgl = df.pivot(index='GPA',columns='LSAT str',values='{}'.format(item))
            df_sgl['lsac number'] = num
            df_pool_sqr = df_pool_sqr.append(df_sgl)
        df_pool_sqr.to_csv('../../data/edit/df_pool_sqr_{}.csv'.format(item))
    return

def lsn_app_stat_pool():
    df = pd.read_csv('../../data/edit/sample_c1_py.csv')
    df_table = pd.read_csv('../../data/edit/match_school_table_concise.csv')
    
    # Select schools with official data
    df = df.merge(df_table, on='Law School',how='right').reset_index()
    print df.columns.tolist()
    
    # Count total apps and adm by school
    print df['Sent_delta'].unique()
    print df['Accepted'].unique()
    df_apps_sum = df.groupby(['lsac number'])['Sent_delta'].count().reset_index()
    df_adm_sum = df.groupby(['lsac number'])['Accepted'].sum().reset_index()
    df_apps_sum['lsac number'] = df_apps_sum['lsac number'].astype(str)
    df_adm_sum['lsac number'] = df_adm_sum['lsac number'].astype(str)
    
    # Attach cells/grids to the LSN data
    df = df[['lsac number','GPA','LSAT','Sent_delta','Accepted','User Name']]
    df_cbn = df.merge(df_table,on='lsac number',how='left').reset_index()
    df_cbn.to_csv('../../data/edit/df_cbn.csv')
    
    # Extract bounds of cells
    df_long = pd.read_csv('../../data/edit/df_pool_long.csv')
    list_lsac_number = df_cbn['lsac number'].unique().tolist()
    dic_bounds = {}
    for item in list_lsac_number:
        dic_bounds[item] = []
        df_sub = df_long[df_long['lsac number']==item]
        gpa_cell = df_sub['GPA'].unique().tolist()
        lsat_cell = df_sub['LSAT Score'].unique().tolist()
        for item_g in gpa_cell:
            for item_l in lsat_cell:
                dic_bounds[item].append(item_g.split('-',1)+item_l.split('-',1))
                
    # Calculate statistics by school and cells
    df_lsn_pool_long = pd.DataFrame()
    for item in list_lsac_number:
        df_cbn_sgl = df_cbn[df_cbn['lsac number']==item]
        dic_cbn = {}
        for bd in dic_bounds[item]:    
            bd = [float(i) for i in bd]
            dic_cbn['{}_{}_{}_{}_sent'.format(bd[0],bd[1],bd[2],bd[3])] = []  
            dic_cbn['{}_{}_{}_{}_accepted'.format(bd[0],bd[1],bd[2],bd[3])] = []  
            for index, row in df_cbn_sgl.iterrows(): 
                if (row['LSAT']>=bd[2]) & (row['LSAT']<=bd[3]) & (row['GPA']>=bd[0]) & (row['GPA']<=bd[1]):
                    dic_cbn['{}_{}_{}_{}_sent'.format(bd[0],bd[1],bd[2],bd[3])].append(row['Sent_delta'])
                    dic_cbn['{}_{}_{}_{}_accepted'.format(bd[0],bd[1],bd[2],bd[3])].append(row['Accepted'])
                    continue
            list_value = ['{}'.format(item),'{}'.format(bd[0]),'{}'.format(bd[1]),'{}'.format(bd[2]),'{}'.format(bd[3]),
                        len(dic_cbn['{}_{}_{}_{}_sent'.format(bd[0],bd[1],bd[2],bd[3])]),
                        sum(dic_cbn['{}_{}_{}_{}_accepted'.format(bd[0],bd[1],bd[2],bd[3])])]
            list_var = ['lsac number','GPA left','GPA right','LSAT Score left','LSAT Score right',
                        'Apps','Adm']
            df_tmp = pd.Series(list_value, index = list_var)
            df_lsn_pool_long = df_lsn_pool_long.append(df_tmp,ignore_index=True)
    
    # Merge back with totals by schools
    df_lsn_pool_long = df_lsn_pool_long.merge(df_apps_sum,on='lsac number',how='left').reset_index().rename(columns={'Sent_delta':'Apps_sum'})
    df_lsn_pool_long = df_lsn_pool_long.merge(df_adm_sum,on='lsac number',how='left').reset_index().rename(columns={'Accepted':'Adm_sum'})
    
    # Calculate Statistics in each cell
    df_lsn_pool_long['app_pct'] = df_lsn_pool_long['Apps']/df_lsn_pool_long['Apps_sum']
    df_lsn_pool_long['adm1_pct'] = df_lsn_pool_long['Adm']/df_lsn_pool_long['Apps_sum']
    df_lsn_pool_long['adm2_pct'] = df_lsn_pool_long['Adm']/df_lsn_pool_long['Adm_sum']
    df_lsn_pool_long['select_pct'] = df_lsn_pool_long['Adm']/(df_lsn_pool_long['Apps']+0.00001)
    
    # Write dic into a LONG data frame               
    df_lsn_pool_long.to_csv('../../data/edit/df_lsn_pool_long.csv') 
    
    # Reshape statistics to WIDE format (Presenting results)
    list_stat = ['app_pct','adm1_pct','adm2_pct','select_pct']
    df_lsn_pool_long['LSAT str'] = 'LSAT ' + df_lsn_pool_long['LSAT Score left'].astype(str) +\
                                    '-' + df_lsn_pool_long['LSAT Score right'].astype(str)
    df_lsn_pool_long['GPA'] = df_lsn_pool_long['GPA left'].astype(str)+'-' + df_lsn_pool_long['GPA right'].astype(str)
    list_lsac_no = df_lsn_pool_long['lsac number'].unique().tolist()
    
    df_lsn_pool_sqr = pd.DataFrame()
    for item in list_stat: 
        for num in list_lsac_no:
            df = df_lsn_pool_long[df_lsn_pool_long['lsac number'] == num]
            df_sgl = df.pivot(index='GPA',columns='LSAT str',values='{}'.format(item))
            df_sgl['lsac number'] = num
            df_lsn_pool_sqr = df_lsn_pool_sqr.append(df_sgl)
        df_lsn_pool_sqr.to_csv('../../data/edit/df_lsn_pool_sqr_{}.csv'.format(item))
    
    return
    
def merge_official_lsn_app_adm():
    df_official = pd.read_csv('../../data/edit/df_pool_long.csv')
    df_lsn = pd.read_csv('../../data/edit/df_lsn_pool_long.csv')
    list_identifier = ['lsac number','GPA left','GPA right','LSAT Score left','LSAT Score right']
    list_compare = ['app_pct','adm1_pct','adm2_pct','select_pct']
    list_official = ['GPA','LSAT Score']
    
    for item in ['GPA', 'LSAT Score']:
        df_official['{} left'.format(item)] = pd.to_numeric(df_official['{}'.format(item)].str.split('-',1).str[0])
        df_official['{} right'.format(item)] = pd.to_numeric(df_official['{}'.format(item)].str.split('-',1).str[1])
    
    df_official = df_official[list_identifier + list_compare + list_official]
    df_lsn = df_lsn[list_identifier + list_compare]
    for item in list_compare:
        df_lsn = df_lsn.rename(columns={'{}'.format(item):'{}_lsn'.format(item)})
    df_official_lsn = df_official.merge(df_lsn,on=list_identifier,how='inner').reset_index()
    df_official_lsn.to_csv('../../data/edit/df_official_lsn.csv')
    
    print df_official_lsn['lsac number'].nunique()
    return df_official_lsn

if __name__ == '__main__':
    #import_official_app_offer()
    #match_official_app_names()
    #match_all()
    #official_app_stat_pool()
    #lsn_app_stat_pool()
    df_official_lsn = merge_official_lsn_app_adm()

