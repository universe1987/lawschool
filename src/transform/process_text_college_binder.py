import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict, Counter
from utils import keep_ascii_file, filter_good_applicants, get_stats
from extract.utils import remove_special_char,keep_ascii
from select_tables import select_application_tables, select_search_tables, select_user_tables, select_user_tables2
from process_merge import process_app_data, process_rank_data, merge_app_rank
from process_text import learn_text, clean_state_city
from process_text_college_baseline import usnews_build
import nltk 
#nltk.download('words')
from autocorrect import spell
from ngram import NGram
import difflib
import urllib2
from bs4 import BeautifulSoup

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch

# first, merge every piece to usnews rankings: {topN, union, tallal}
# second, merge every processed piece to the very very main trunk of personal details
# {topN,union,tallal,matched,vague}
# simple statistics

def school_usnews_merge_type(stype):
    df = pd.read_csv('../../data/edit/df_{}_combined.csv'.format(stype))
    df_usnews_ranks = pd.read_csv('../../data/edit/usnews_ranks.csv')
    
    if stype == 'union':
        print df.columns.values.tolist()
        df = df.rename(columns={'City_x':'City'})
    print 'len of input {}'.format(stype), len(df)
    df = df.fillna('')
    df_miss = df[df['rank']==''] #not matched by location; school name manually imputed 
    df_non_miss = df[df['rank']!=''] #already matched up by location
    print len(df_miss)
    
    df_miss = df_miss.drop(['State_acronym','enrollment', # 'City','State',
                             'group','location','public','rank','tuition'],axis=1)
    df_miss_usnews = df_miss.merge(df_usnews_ranks,left_on='name',
                              right_on='name',how='left').reset_index()
    df_miss_usnews.to_csv('../../data/edit/try_{}.csv'.format(stype))
    df_miss_usnews = df_miss_usnews.groupby('Unnamed: 0_x').first().reset_index()
    df_miss_usnews = df_miss_usnews.rename(columns={'City_x':'City','State_x':'State'})
    # The above line keeps the City and State in df_details, not usnews
    # state_acronym is the one in usnews 
    df_miss_usnews.to_csv('../../data/edit/try2_{}.csv'.format(stype))
    df_miss_usnews = df_miss_usnews[['College Name or Type','id','name','City','State',
                                    'State_acronym','enrollment','group','location','public', 
                                    'rank','tuition']]
    df_non_miss = df_non_miss[['College Name or Type','id','name','City','State',
                              'State_acronym','enrollment','group','location','public', 
                              'rank','tuition']]
    print len(df_miss_usnews)
    
    df_non_miss.to_csv('../../data/edit/{}_non_miss.csv'.format(stype))
    df_non_miss = pd.read_csv('../../data/edit/{}_non_miss.csv'.format(stype))
    df_miss_usnews.to_csv('../../data/edit/{}_miss_usnews.csv'.format(stype))
    df_miss_usnews = pd.read_csv('../../data/edit/{}_miss_usnews.csv'.format(stype))
    
    df_merged_usnews = df_miss_usnews.append(df_non_miss,ignore_index=True)
    print len(df_merged_usnews)
    df_merged_usnews.to_csv('../../data/edit/df_{}_merged_usnews.csv'.format(stype))
    
    df_check = df_miss_usnews[df_miss_usnews['rank'].isnull()]
    df_check.to_csv('../../data/edit/df_{}_check.csv'.format(stype))
    return

def school_usnews_merge():
    for item in ['topN_univ','topN_lac','union']:
        school_usnews_merge_type(item)
    return
    
def school_usnews_details_merge():
    # quick detour:
    df_univ = pd.read_csv('../../data/entry/df_merge_univ_marked.csv')
    df_lac = pd.read_csv('../../data/entry/df_merge_lac_marked.csv')
    df_topN_details = pd.read_csv('../../data/edit/df_topN_details.csv')
    df_topN_school_place = pd.read_csv('../../data/edit/df_topN_school_place.csv')
    print 'brutal-force',len(df_univ),len(df_lac),len(df_topN_details),len(df_topN_school_place)
    # Well, let's just merge them brutal-forcely!
    
    #formal start:
    df_details = clean_state_city()
    print 'df_details',len(df_details),df_details['College Name or Type'].nunique()
    for item in ['topN_univ','topN_lac','union']:
        df_merged_usnews = pd.read_csv('../../data/edit/df_{}_merged_usnews.csv'.format(item))
        df_merged_usnews = df_merged_usnews.fillna('')
        df_merged_usnews = df_merged_usnews[df_merged_usnews['College Name or Type']!='']
        df_merged_usnews_squeeze = df_merged_usnews.groupby(['College Name or Type','State','City']).first().reset_index()
        df_merged_usnews_squeeze.to_csv('../../data/edit/df_{}_squeeze.csv'.format(item))
        print item+'_squeeze',len(df_merged_usnews_squeeze),df_merged_usnews_squeeze['College Name or Type'].nunique()

        df_usnews_details = df_merged_usnews_squeeze.merge(df_details,on=['College Name or Type','State','City'],how='inner').reset_index()
        print item, len(df_usnews_details),df_usnews_details['College Name or Type'].nunique()
        df_usnews_details.to_csv('../../data/edit/df_usnews_details_{}.csv'.format(item))
    return
    
def vague_details_merge():
    df_details = clean_state_city()
    df_vague = pd.read_csv('../../data/edit/df_vague.csv')
    df_vague = df_vague.fillna('')
    df_vague = df_vague[df_vague['College Name or Type']!='']
    df_vague = df_vague[df_vague['groups']!='tallal'] 
    # added entry/Copy of college_name_05_07_tallal.csv
    print 'vague_pre',len(df_vague),df_vague['College Name or Type'].nunique()
    df_vague_details = df_vague.merge(df_details,on='College Name or Type',how='inner').reset_index()
    print 'vague', len(df_vague_details),df_vague_details['College Name or Type'].nunique()
    df_vague_details.to_csv('../../data/edit/df_usnews_details_vague.csv')
    return
    

def tallal_usnews_details_merge():
    df_details = clean_state_city()
    df_usnews_ranks = usnews_build()
    df_tallal = pd.read_csv('../../data/edit/tallal_usnews.csv')
    df_tallal = df_tallal.fillna('')
    
    df_tallal_usnews = df_tallal.merge(df_usnews_ranks,left_on='usnews_guess',right_on='name',how='left').reset_index(drop=True)
    df_tallal_usnews_details = df_tallal_usnews.merge(df_details,on='College Name or Type',how='inner').reset_index(drop=True)
    df_tallal_usnews_details = df_tallal_usnews_details[df_tallal_usnews_details['College Name or Type']!='']
    df_tallal_usnews_details = df_tallal_usnews_details.groupby(['Unnamed: 0_y']).first().reset_index()
    
    df_tallal_usnews_details['groups'] = ''
    for item in ['positive','neutral','bad','foreign','bad_school']:
        df_tallal_usnews_details.loc[df_tallal_usnews_details['name_rev']==item,'groups']=item
    df_tallal_usnews_details.loc[(df_tallal_usnews_details['groups']=='')&(df_tallal_usnews_details['usnews_guess']==''),'groups']='bad_school'
    
    print 'tallal',len(df_tallal_usnews_details),df_tallal_usnews_details['College Name or Type'].nunique()
    df_tallal_usnews_details = df_tallal_usnews_details.rename(columns={'State_y':'State','City_y':'City'})
    df_tallal_usnews_details.to_csv('../../data/edit/df_usnews_details_tallal.csv')
    return
    
    
def exact_usnews_merge():
    df_exact = pd.read_csv('../../data/entry/College Name or Type_unique_marked2.csv')
    df_ranks = pd.read_csv('../../data/edit/usnews_flagship_acronym.csv')
    
    df_exact = df_exact.fillna('')
    df_exact = df_exact[(df_exact['name']==1)&(df_exact['name_rev1_flag']=='')&(df_exact['guess']=='')]
    
    list_cand = ['usnews','usnews_short','acronym','flagship']
    list_right_on = ['name','cand_usnews_short','usnews_guess','flagship']
    list_var = ['College Name or Type','name','City','State','State_acronym','enrollment',
                'group','location','public','rank','tuition']
    
    df_match_cand_all = pd.DataFrame()
    for counter, cand in enumerate(list_cand):
        df_exact_cand = df_exact[df_exact['cand_'+cand]!='']
        print 'cand',len(df_exact_cand)
        df_match_cand = df_exact_cand.merge(df_ranks,left_on='cand_'+cand, right_on=list_right_on[counter],how='left').reset_index(drop=True)
        df_match_cand = df_match_cand.groupby(['index']).first().reset_index()
        print 'cand matched',len(df_match_cand)
        df_match_cand = df_match_cand.rename(columns={'name_y':'name'})
        df_match_cand = df_match_cand[list_var]
        df_match_cand_all = df_match_cand_all.append(df_match_cand)
        df_match_cand.to_csv('../../data/edit/df_match_{}.csv'.format(cand))
    df_match_cand_all.to_csv('../../data/edit/df_match_cand_all.csv')
    return 

    
def exact_usnews_details_merge():
    df_details = clean_state_city()
    df_match_cand_all = pd.read_csv('../../data/edit/df_match_cand_all.csv')
    df_match_cand_all = df_match_cand_all.fillna('')
    df_exact_usnews_details = df_match_cand_all.merge(df_details,on='College Name or Type',how='inner').reset_index()
    df_exact_usnews_details = df_exact_usnews_details.groupby(['User Name']).first().reset_index()
    print 'exact',len(df_exact_usnews_details),df_exact_usnews_details['College Name or Type'].nunique()
    print 'exact_user',df_exact_usnews_details['User Name'].nunique(),len(df_exact_usnews_details[df_exact_usnews_details['User Name']!=''])
    
    df_exact_usnews_details = df_exact_usnews_details.rename(columns={'State_y':'State','City_y':'City'})
    df_exact_usnews_details.to_csv('../../data/edit/df_usnews_details_exact.csv')
    return
    
def college_name_conclude():
    df_details = clean_state_city()
    #print df_details.columns.tolist()
    list_var = ['User Name','College Name or Type','Major','Degree GPA','LSAT 2','LSAT 3',
                'LSAT 1','LSDAS GPA','Class Rank','LSAT','Race','Gender','State', 'Race2',
                'City','Years out of Undergrad','extra curricular','additional info'] 
    list_usnews  = ['name','State_acronym','enrollment','group','location','public','rank',
                 'tuition']

    list_cat = ['exact','topN_univ','topN_lac','union','tallal','vague']
    df_details_clean = pd.DataFrame()
    for item in list_cat:
        df = pd.read_csv('../../data/edit/df_usnews_details_{}.csv'.format(item))
        df = df.fillna('')
        
        if item == 'vague':
            for x in ['name','State_acronym','enrollment','group','location','public','rank','tuition']:
                df[x] = ''
        if (item != 'vague') & (item != 'tallal'):
            df['groups'] = ''
            
        df = df[list_var+list_usnews+['groups']]
        df = df[df['College Name or Type']!='']
        df_details_clean = df_details_clean.append(df,ignore_index=True)
        print item,'/', df['User Name'].nunique(),df['College Name or Type'].nunique() #len(df[df['User Name']!='']),len(df)
    
    df_details_clean = df_details_clean.groupby(['User Name']).first().reset_index()
    print 'df_details_clean','/',df_details_clean['User Name'].nunique(),df_details_clean['College Name or Type'].nunique()
    print 'df_details_clean','||',len(df_details_clean),len(df_details_clean[df_details_clean['User Name']!=''])    
    df_details_clean.to_csv('../../data/edit/df_details_college_name_cleaned.csv')
    
    df_details = df_details[list_var]
    print 'df_details','/',df_details['User Name'].nunique(),df_details['College Name or Type'].nunique()
    print 'df_details','||',len(df_details),len(df_details[df_details['User Name']!=''])
    
    df_user_list = df_details[['User Name']]
    df_details_college = df_user_list.merge(df_details_clean,on=['User Name'],how='left').reset_index()
    print 'df_details_college','/',df_details_college['User Name'].nunique(),df_details_college['College Name or Type'].nunique()
    print 'df_details_college','||',len(df_details_college),len(df_details_college[df_details_college['User Name']!=''])
    
    print df_details_college['User Name'].nunique(),len(df_details_college)
    df_noname = df_details_college[df_details_college['User Name']=='']
    df_noname.to_csv('../../data/edit/df_noname.csv')
    
    df_details_college = df_details_college[df_details_college['User Name']!='']
    print len(df_details_college), df_details_college['User Name'].nunique()
    
    df_details_college.to_csv('../../data/edit/df_details_race_college_cleaned.csv')
    # Key college variable: name, rank, group, groups
    # groups:['positive','neutral','bad','bad_school','foreign']
    
    return