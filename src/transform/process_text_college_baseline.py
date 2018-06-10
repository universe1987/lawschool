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


def usnews(key):
    school_list = pd.read_csv('../../data/entry/usnews_{}_2018.csv'.format(key), header=None)
    school_list = school_list.rename(columns={0:'name',1:'tuition',2:'enrollment'}).drop([3,4],axis=1)
    school_list = school_list[school_list['name'].notnull()]
    school_list['group'] = key
    for item in ['location','rank','public']:
        school_list[item] = ''
    school_list = school_list.reset_index(drop=True)
    for index, row in school_list.iterrows():
        if index%3 == 1:
            school_list.loc[index-1,'location'] = row['name']
        elif index%3 == 2:
            school_list.loc[index-2, 'rank'] = row['name']
    school_list = school_list[school_list['tuition'].notnull()].reset_index()
    school_list['name'] = school_list['name'].str.rstrip('1').str.replace('--',' ').str.replace('-',' ')
    school_list['public'] = (school_list['tuition'].str.contains('in-state'))
    for index, row in school_list.iterrows():
        for item in ['name','tuition','location','rank']:
            school_list.loc[index,item] = keep_ascii(school_list.loc[index,item])
            
    school_list['rank'] = school_list['rank'].str.split(' ').str[0].str.replace('#','')
    school_list['City'] = school_list['location'].str.split(',').str[0].str.lower().str.rstrip(' ')
    school_list['State_acronym'] = school_list['location'].str.split(',').str[-1].str.lower().str.lstrip(' ')
    
    df_state_list = pd.read_csv('../../data/entry/states_acronyms.csv',names=['State','State_acronym'])
    for item in ['State','State_acronym']:
        df_state_list[item] = df_state_list[item].str.lower().str.lstrip(' ')
    
    school_list = school_list.merge(df_state_list,on='State_acronym',how='left')
    school_list.to_csv('../../data/edit/usnews_{}_2018.csv'.format(key))
    return school_list
    
def usnews_build():
    df_usnews_ranks = pd.DataFrame()
    key_list = ['national_univ','national_lac','midwest_univ','north_univ','south_univ','western_univ',
                'hbcu','eng_doctorate','eng_nodoctorate','midwest_college','north_college','south_college',
                'western_college','business']
    for item in ['national_public']:
        df = usnews(item)
    for item in key_list:
        df = usnews(item)
        df_usnews_ranks = df_usnews_ranks.append(df)
    df_usnews_ranks = df_usnews_ranks.reset_index(drop=True)
    df_usnews_ranks['name'] = df_usnews_ranks['name'].str.lower()
    df_usnews_ranks.to_csv('../../data/edit/usnews_ranks.csv')
    return df_usnews_ranks
    
def college_acronym():
    html_doc = urllib2.urlopen('https://en.wikipedia.org/wiki/List_of_colloquial_names_for_universities_and_colleges_in_the_United_States')
    soup = BeautifulSoup(html_doc, 'html.parser')
    li_raws = soup.findAll('li')
    li_shorts = []
    for item in li_raws:
        if ' - ' in str(item.text):
            li_shorts.append(str(item.text))
    #print li_shorts
    series_acronym = pd.Series(li_shorts,name='all')
    df_acronym = pd.DataFrame(series_acronym).reset_index(drop=True)
    df_acronym['acronym'] = df_acronym['all'].str.split(' - ').str[0]
    df_acronym['full'] = df_acronym['all'].str.split(' - ').str[-1]
    df_sub = df_acronym[df_acronym['acronym'].str.contains(' or ')]
    df_base = df_acronym[~df_acronym['acronym'].str.contains(' or ')]
    df_sub['temp'] = df_sub['acronym'].str.split(' or ')
    df_sub['temp_ct'] = df_sub['acronym'].str.count(' or ')+1
    print 'more than two acronyms', len(df_sub[df_sub['temp_ct']>2])
    df_sub1 = df_sub2 = df_sub
    df_sub1['acronym'] = df_sub1['temp'].str[0]
    df_acronym = df_base.append(df_sub1)
    df_sub2['acronym'] = df_sub2['temp'].str[-1]
    df_acronym = df_acronym.append(df_sub2)
    df_acronym = df_acronym.reset_index(drop=True).drop(['all','temp','temp_ct'],axis=1)
    df_acronym['acronym'] = df_acronym['acronym'].str.lower()
    df_acronym.to_csv('../../data/edit/acronym.csv')
    return df_acronym

def usnews_acronym_flagship_merge():
    df_usnews_ranks = pd.read_csv('../../data/edit/usnews_ranks.csv')
    df_usnews = df_usnews_ranks.fillna('')
    
    df_usnews['cand_usnews_short'] = df_usnews_ranks['name'].str.replace('university','').str.replace('college','').tolist()

    df_flagship = pd.read_csv('../../data/entry/usnews_ranks_flagship_2018.csv')
    df_usnews_flagship = df_usnews.merge(df_flagship,on='name',how='left').reset_index(drop=True)
    df_usnews_flagship.to_csv('../../data/edit/usnews_flagship.csv')
    
    # keep only one full name for each acronym; put it in full_select
    # save the file as entry/acronym_marked.csv
    df_acronym = pd.read_csv('../../data/entry/acronym_marked.csv')
    df_acronym = df_acronym.fillna('')
    for item in ['full','full_select']:
        df_acronym[item] = df_acronym[item].str.lower().str.replace(',',' ')
    threshold = 0.9
    list_usnews = df_usnews['name'].tolist()
    for index, row in df_acronym.iterrows():
        best_match_usnews = difflib.get_close_matches(row['full_select'],list_usnews,cutoff=threshold)
        #df_acronym.loc[index, 'usnews_guess']=';'.join(str(x) for x in best_match_usnews)
        if len(best_match_usnews) > 0:
            df_acronym.loc[index,'usnews_guess'] = best_match_usnews[0]

    df_usnews_flagship_acronym = df_usnews_flagship.merge(df_acronym,left_on='name',right_on='usnews_guess',how='left').reset_index(drop=True)
    df_usnews_flagship_acronym.to_csv('../../data/edit/usnews_flagship_acronym.csv')
    return


def match_college_name_type():
    df_acronym = college_acronym()
    df_usnews_ranks = usnews_build()
    df_usnews_flagship = pd.read_csv('../../data/entry/usnews_ranks_flagship_2018.csv')

    df_details = pd.read_csv('../../data/entry/College Name or Type_unique_marked.csv') #,names=['College Name or Type']
    df_details['College Name or Type'] = df_details['College Name or Type'].fillna('').str.lower() 
    #                                     .str.replace('--',' ').str.replace('-',' ')
    
    threshold = 0.7 # Don't change the value! It affects codes downward
    list = df_details['College Name or Type'].unique()
    df_details_unique = pd.Series(list).reset_index().rename(columns={0:'College Name or Type'})
    print df_details_unique.head(10),len(df_details_unique)
    
    list_usnews = df_usnews_ranks['name'].tolist()
    list_usnews_short = df_usnews_ranks['name'].str.replace('university','').str.replace('college','').tolist()
    list_acronym = df_acronym['acronym'].tolist()
    list_flagship = df_usnews_flagship.loc[df_usnews_flagship['flagship'].notnull(),'flagship'].tolist()
     
    for index, row in df_details_unique.iterrows():
        best_match_usnews = difflib.get_close_matches(row['College Name or Type'],list_usnews,cutoff=threshold)
        df_details_unique.loc[index, 'cand_usnews']=';'.join(str(x) for x in best_match_usnews)

        best_match_usnews_short = difflib.get_close_matches(row['College Name or Type'],list_usnews_short,cutoff=threshold)
        df_details_unique.loc[index, 'cand_usnews_short']=';'.join(str(x) for x in best_match_usnews_short)        
        
        best_match_acronym = difflib.get_close_matches(row['College Name or Type'],list_acronym,cutoff=threshold)
        df_details_unique.loc[index, 'cand_acronym']=';'.join(str(x) for x in best_match_acronym)
        
        best_match_flagship = difflib.get_close_matches(row['College Name or Type'],list_flagship,cutoff=threshold)
        df_details_unique.loc[index, 'cand_flagship']=';'.join(str(x) for x in best_match_flagship)
        
    print 'cand_usnews',len(df_details_unique[df_details_unique['cand_usnews'].str.islower()])
    print 'cand_usnews_short',len(df_details_unique[df_details_unique['cand_usnews_short'].str.islower()])
    print 'cand_acronym',len(df_details_unique[df_details_unique['cand_acronym'].str.islower()])
    print 'cand_flagship',len(df_details_unique[df_details_unique['cand_flagship'].str.islower()])
    
    df_details_unique.to_csv('../../data/edit/candidates.csv')
    
    df_school_match = df_details.merge(df_details_unique, on = 'College Name or Type', how='inner')\
                      .reset_index(drop=True).fillna('')
    df_school_match.to_csv('../../data/edit/schools.csv')
    return df_school_match
    
def prune_college_name_type():
    #match_college_name_type()
    df_school_prune = pd.read_csv('../../data/edit/schools.csv')

    for col in ['name','guess','hbcu','big10','pac','sisters']:
        df_school_prune[col] = df_school_prune[col].fillna('').astype(str)
    
    list_col = ['cand_usnews','cand_usnews_short','cand_acronym','cand_flagship']
    df_school_prune.loc[df_school_prune['name']=='', list_col] = ''
    df_school_prune.loc[df_school_prune['guess']!='', list_col] = ''
    
    for col in list_col: # select the best matched name
        df_school_prune[col] = df_school_prune[col].fillna(';').str.split(';').str[0]
    
    df_school_prune.to_csv('../../data/edit/schools_name.csv')
    # Then: hand cleaning => entry/College Name or Type_unique_marked2.csv
    #       clean matched names, so one school is matched at most to one out of the
    #       four candidate names
    # Divided into five parts based on the completeness of information
    # Part 1: one of the "cand_" is filled --> exactly matched
    # Part 2: name_rev1_guess = 1 --> full school name can be manually recovered --> tallal
    # Part 3: guess = 1 --> school ranks are reported --> topN
    # Part 4: big10, pac, sisters, hcbu --> school unions are reported --> union
    # Part 5: name = blank --> very vague info is reported --> vague
    # Conclude: Combine all five parts together, merge back to the original file
    return
    
def tallal_college_name_type():
    # The unmatched school names/types with some information of school names
    # entry/College Name or Type_unique_marked2.csv: name_rev1_flag = 1
    # Given to Tallal to manually add a revised name
    # Then I am going to match it again with the four candidate names until fully
    # matched
    df = pd.read_csv('../../data/entry/College Name or Type_unique_marked2.csv')
    df_tallal = df[df['name_rev1_flag']==1.0] 
    print df_tallal.head()
    print len(df_tallal['College Name or Type'])
    
    df_details = clean_state_city()
    print df_details.head()
    
    df_tallal_school_place = df_tallal.merge(df_details,on='College Name or Type',how='left')
    df_tallal_school_place = df_tallal_school_place[['College Name or Type','State','City']]
    print df_tallal_school_place.head()
    print len(df_tallal_school_place['College Name or Type'])
    
    df_tallal_school_place.to_csv('../../data/edit/df_tallal_school_place.csv')
    return df_tallal_school_place
    
def topN_college_name_type():
    # The unmatched school names/types featured "top N"
    # entry/College Name or Type_unique_marked2.csv: name_rev1_flag = '', guess = 1
    # Paired with state/city information
    df = pd.read_csv('../../data/entry/College Name or Type_unique_marked2.csv')
    df_topN = df[(df['name_rev1_flag'].isnull())&(df['guess']==1.0)] 
    print df_topN.head()
    print len(df_topN['College Name or Type'])
    
    df_details = clean_state_city()
    print df_details.head()
    
    df_topN_school_place = df_topN.merge(df_details,on='College Name or Type',how='left')
    df_topN_details = df_topN_school_place
    df_topN_school_place = df_topN_school_place[['College Name or Type','State','City']]
    print df_topN_school_place.head()
    print len(df_topN_school_place['College Name or Type'])
    
    df_topN_details.to_csv('../../data/edit/df_topN_details.csv')
    df_topN_school_place.to_csv('../../data/edit/df_topN_school_place.csv')
    return df_topN_school_place
    
def union_college_name_type():
    # The unmatched school names/types featured "union"
    # entry/College Name or Type_unique_marked2.csv: one of the unions is 1
    # Paired with state/city information
    df = pd.read_csv('../../data/entry/College Name or Type_unique_marked2.csv')
    
    # big10 also contains big12. However, as big12 are southern schools, big10 are
    # midwest schools, they don't overlap with each other. So I can safely group
    # them into one group.
    df_union = df[(df['big10']==1.0) | (df['sisters']==1.0) | (df['pac']==1.0) | (df['hbcu']==1.0) \
                  | (df['public_ivy']==1.0) | (df['west_ivy']==1.0) | (df['new_ivy'] ==1.0) \
                  | (df['little_ivy']==1.0) | (df['sec']==1.0) | (df['flagship']==1.0)] 
    print df_union.head()
    print len(df_union['College Name or Type'])
    
    df_details = clean_state_city()
    print df_details.head()
    
    df_union_school_place = df_union.merge(df_details,on='College Name or Type',how='left')
    df_union_school_place = df_union_school_place[['College Name or Type','State','City','big10',
                            'sisters','pac','hbcu','public_ivy','west_ivy',
                            'little_ivy','sec','flagship']]
    print df_union_school_place.head()
    print len(df_union_school_place['College Name or Type'])
    
    df_union_school_place.to_csv('../../data/edit/df_union_school_place.csv')
    return df_union_school_place

def match_topN_college_name_type_location():
    df_usnews_ranks = usnews_build()
    df_usnews_ranks.loc[~df_usnews_ranks['rank'].str.isdigit(),'rank']=''
    df_usnews_ranks['rank'] = pd.to_numeric(df_usnews_ranks['rank'])
    df_usnews_ranks = df_usnews_ranks[df_usnews_ranks['rank']<=100]
    
    df_topN_school_place = topN_college_name_type()
    df_topN_school_place = df_topN_school_place.reset_index()
    df_topN_school_place['id'] = df_topN_school_place['index']+1
    
    df_topN_lac = df_topN_school_place[df_topN_school_place['College Name or Type'].str.contains('lac|liberal|lac') ]
    df_lac_ranks = df_usnews_ranks[df_usnews_ranks['group']=='national_lac']
    df_lac_ranks.to_csv('../../data/edit/df_lac_ranks.csv')
    df_merge_lac = df_topN_lac.merge(df_lac_ranks,on=['State','City'],how='left')
    df_merge_lac.to_csv('../../data/edit/df_merge_lac.csv')
    
    df_topN_univ = df_topN_school_place[~df_topN_school_place['College Name or Type'].str.contains('lac|liberal|lac') ]
    df_univ_ranks = df_usnews_ranks[df_usnews_ranks['group']=='national_univ']
    df_merge_univ = df_topN_univ.merge(df_univ_ranks,on=['State','City'],how='left')
    df_merge_univ.to_csv('../../data/edit/df_merge_univ.csv')
    return
    
def match_union_college_name_type_location():
    # entry/usnews_union_2018.csv is created by hand!
    df_union_usnews_ranks = pd.read_csv('../../data/entry/usnews_union_2018.csv')
    df_union_usnews_ranks['rank'] = df_union_usnews_ranks['rank'].str.split(' ').str[0].str.replace('#','')
    df_union_usnews_ranks['City'] = df_union_usnews_ranks['location'].str.split(',').str[0].str.lower().str.rstrip(' ')
    df_union_usnews_ranks['State_acronym'] = df_union_usnews_ranks['location'].str.split(',').str[-1].str.lower().str.lstrip(' ')

    df_state_list = pd.read_csv('../../data/entry/states_acronyms.csv',names=['State','State_acronym'],index_col=None)
    for item in ['State','State_acronym']:
        df_state_list[item] = df_state_list[item].str.lower().str.lstrip(' ')
    
    df_union_usnews_ranks = df_union_usnews_ranks.merge(df_state_list,on='State_acronym',how='left')
    df_union_usnews_ranks.drop(['Unnamed: 0'],axis=1)
    df_union_usnews_ranks.to_csv('../../data/edit/usnews_union_pre_2018.csv')

    df_union_usnews_ranks = pd.read_csv('../../data/edit/usnews_union_pre_2018.csv')
    df_hbcu_usnews_ranks = pd.read_csv('../../data/edit/usnews_hbcu_2018.csv')
    df_union_usnews_ranks = df_union_usnews_ranks.append(df_hbcu_usnews_ranks)
    df_union_usnews_ranks = df_union_usnews_ranks[df_union_usnews_ranks['name'].notnull()]
    df_union_usnews_ranks.loc[df_union_usnews_ranks['union'].isnull(),'union'] = 'hbcu'
    df_union_usnews_ranks.to_csv('../../data/edit/usnews_union_2018.csv')
    
    df_union_usnews_ranks['rank'] = df_union_usnews_ranks['rank'].astype(str)
    df_union_usnews_ranks['rank'] = df_union_usnews_ranks['rank'].str.replace('.0','')
    df_union_usnews_ranks.loc[~df_union_usnews_ranks['rank'].str.isdigit(),'rank']=''
    df_union_usnews_ranks['rank'] = pd.to_numeric(df_union_usnews_ranks['rank'])
    df_union_usnews_ranks = df_union_usnews_ranks[df_union_usnews_ranks['rank']<=200]
    
    df_union_school_place = union_college_name_type()
    df_union_school_place = df_union_school_place.reset_index()
    df_union_school_place['id'] = df_union_school_place['index']+1
    
    list_union = ['big10','sisters','pac','hbcu','public_ivy','west_ivy',
                  'little_ivy','sec','flagship']
    df_merge_union_univ = pd.DataFrame()
    for item in list_union:
        df1 = df_union_usnews_ranks[df_union_usnews_ranks['union']==item]
        df2 = df_union_school_place[df_union_school_place[item]==1.0]
        df3 = df2.merge(df1,on=['State'],how='left')
        df_merge_union_univ = df_merge_union_univ.append(df3)
    df_merge_union_univ = df_merge_union_univ.sort_values(by=['union','College Name or Type','State','City_x'])
    df_merge_union_univ.to_csv('../../data/edit/df_merge_union_univ.csv')
    return
    
def match_tallal_college_name_type():
    df_usnews_ranks = usnews_build()
    df_tallal = pd.read_csv('../../data/entry/Copy of college_name_05_07_tallal_marked.csv')
    df_tallal = df_tallal.fillna('')
    df_tallal['name_rev'] = df_tallal['name_rev'].str.lower().replace(',',' ')
    
    threshold = 0.9
    list_usnews = df_usnews_ranks['name'].tolist()
    for index, row in df_tallal.iterrows():
        best_match_usnews = difflib.get_close_matches(row['name_rev'],list_usnews,cutoff=threshold)
        #df_tallal.loc[index, 'usnews_guess']=';'.join(str(x) for x in best_match_usnews)
        if len(best_match_usnews) > 0:
            df_tallal.loc[index,'usnews_guess'] = best_match_usnews[0]
    df_tallal = df_tallal.fillna('')
    #df_tallal = df_tallal[(df_tallal['name_rev']!='') & (df_tallal['usnews_guess']=='')]
    df_tallal.to_csv('../../data/edit/tallal_usnews.csv')
    return
    
'''
def learn_college_name_type():
    df_details_unique = match_college_name_type()
    df_details_unique['matched'] = df_details_unique['cand_usnews'] + df_details_unique['cand_usnews_short'] \
                                   + df_details_unique['cand_acronym']
    df_details_unmatched = df_details_unique[~df_details_unique['matched'].str.islower()]
    
    list_unmatched = df_details_unmatched['College Name or Type'].tolist()
    string_unmatched = ' '.join(str(x) for x in list_unmatched).replace(',',' ').replace(';',' ')\
                       .replace('(',' ').replace(')',' ').replace('\\',' ').replace('/',' ')
    
    list_break = string_unmatched.split(' ')
    #print list_break
    
    c = Counter(list_break)
    df_freq = pd.DataFrame({'values':c.values(),'keys':c.keys()}).sort_values(ascending=False,by=['values'])
    df_freq.to_csv('../../data/edit/df_freq.csv')
    
    raw_input('hhhhhhhhhhhhhh')
    return 
'''
