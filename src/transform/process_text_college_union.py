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


def fill_union_merge_univ():
    # report school unions: big10, pac, sisters, hcbu
    # manually clean edit/df_merge_union_univ.csv so the existing match based on location is reasonable
    # save it into entry/df_merge_union_univ_marked.csv
    # impute school names
    df = pd.read_csv('../../data/entry/df_merge_union_univ_marked.csv')
    
    df_filled = df[df['State_acronym'].notnull()] 
    print len(df_filled['College Name or Type'])
    
    df_unfilled = df[df['State_acronym'].isnull()]
    print len(df_unfilled['College Name or Type'])
    
    df_unfilled = df_unfilled.fillna('')
    
    with open('fill_union_merge_univ.json', 'rb') as file:
        union_groups = json.load(file)
    
    print df_unfilled.head()
    list_union = ['big10','sisters','pac','hbcu','public_ivy','west_ivy',
                  'little_ivy','sec','flagship']
    for item in list_union:
        df_sub = df_unfilled[df_unfilled[item]==1.0]
        print item, df_sub['College Name or Type'].nunique()
        print df_sub['College Name or Type'].unique()

    for index, row in df_unfilled.iterrows():
        if any(row['College Name or Type']==x for x in union_groups["sisters"]):
           #print row['College Name or Type'], '|',row['State'], '|',row['City_x']        
           if 'new york' in row['State']:
               df_unfilled.loc[index,'name'] = 'barnard college'
           elif 'ma' in row['State']:
               df_unfilled.loc[index,'name'] = 'wellesley college'
           else:
               df_unfilled.loc[index,'name'] = 'bryn mawr college'
        if any(row['College Name or Type']==x for x in union_groups["top_hbcu"]):
           df_unfilled.loc[index,'name'] = 'howard university'
        if any(row['College Name or Type']==x for x in union_groups["private_hbcu"]):
           if 'washington - d.c.' in row['State']:
               df_unfilled.loc[index,'name'] = 'howard university'
           elif 'virginia' in row['State']:
               df_unfilled.loc[index,'name'] = 'hampton university'
           else:
               df_unfilled.loc[index,'name'] = 'virginia union university'
        if any(row['College Name or Type']==x for x in union_groups["public_hbcu"]):
           if 'florida' in row['State']:
               df_unfilled.loc[index,'name'] = 'florida a&m university'
           if 'north carolina' in row['State']:
               df_unfilled.loc[index,'name'] = 'north carolina a&t state university'
           else:
               df_unfilled.loc[index,'name'] = 'virginia state university'
        if any(row['College Name or Type']==x for x in union_groups["regular_hbcu"]):
           if 'hampton' in row['City_x']:
               df_unfilled.loc[index,'name'] = 'hampton university'
           else:
               df_unfilled.loc[index,'name'] = 'fort valley state university'          
        if any(row['College Name or Type']==x for x in union_groups["ca_pac10"]):
           df_unfilled.loc[index,'name'] = 'university of southern california'
        if any(row['College Name or Type']==x for x in union_groups["regular_pac10"]):
           if 'tucson' in row['City_x']:
               df_unfilled.loc[index,'name'] = 'university of arizona'
           elif 'los angeles' in row['City_x']:
               df_unfilled.loc[index,'name'] = 'university of southern california'
           else:
               df_unfilled.loc[index,'name'] = 'arizona state university tempe'   
        if any(row['College Name or Type']==x for x in union_groups["regular_big10"]):
           if 'champaign' in row['City_x']:
               df_unfilled.loc[index,'name'] = 'university of illinois urbana champaign' 
           elif 'chicago' in row['City_x']:
               df_unfilled.loc[index,'name'] = 'northwestern university'
           elif 'iowa' in row['City_x']:
               df_unfilled.loc[index,'name'] = 'university of iowa'
           elif ('wisconsin' in row['City_x'])|('madison' in row['City_x']):
               df_unfilled.loc[index,'name'] = 'university of wisconsin madison'
           elif 'lafayette' in row['City_x']:
               df_unfilled.loc[index,'name'] = 'purdue university west lafayette'
           elif 'minneapolis' in row['City_x']:
               df_unfilled.loc[index,'name'] = 'university of minnesota twin cities'
           else:
               df_unfilled.loc[index,'name'] = 'ohio state university columbus'       
        if any(row['College Name or Type']==x for x in union_groups["elite_big10"]):
           df_unfilled.loc[index,'name'] = 'university of michigan ann arbor'       
        if any(row['College Name or Type']==x for x in union_groups["private_big10"]):
           df_unfilled.loc[index,'name'] = 'northwestern university'  
        if any(row['College Name or Type']==x for x in union_groups["private_big12"]):
           df_unfilled.loc[index,'name'] = 'baylor university' 
        if any(row['College Name or Type']==x for x in union_groups["regular_big12"]):
           df_unfilled.loc[index,'name'] = 'university of kansas'
        if any(row['College Name or Type']==x for x in union_groups["public_ivy"]):
           df_unfilled.loc[index,'name'] = 'university of north carolina chapel hill'
        if any(row['College Name or Type']==x for x in union_groups["west_ivy"]):
           df_unfilled.loc[index,'name'] = 'claremont mckenna college'           
        if any(row['College Name or Type']==x for x in union_groups["sec"]):
           if ('atl' in row['City_x'])|('georgia' in row['State']):
               df_unfilled.loc[index,'name'] = 'university of georgia'
           else:   
               df_unfilled.loc[index,'name'] = 'university of alabama'    
        if any(row['College Name or Type']==x for x in union_groups["flagship"]):     
           if 'colorado' in row['State']:
               df_unfilled.loc[index,'name'] = 'university of colorado boulder'
           elif 'north carolina' in row['State']:
               df_unfilled.loc[index,'name'] = 'university of north carolina chapel hill'
           elif row['State'] == 'upper midwest':
               df_unfilled.loc[index,'name'] = 'university of minnesota twin cities'
           else:
               df_unfilled.loc[index,'name'] = 'university of colorado boulder'
    
    print len(df_unfilled[df_unfilled['name']==''])
    df = df_unfilled[df_unfilled['name']=='']
    print df['College Name or Type'].nunique()
    print df['College Name or Type'].unique()
    df_unfilled[df_unfilled['name']==''].to_csv('../../data/edit/df_union_unfilled.csv')
    df_combined = df_filled.append(df_unfilled,ignore_index=True)
    df_combined = df_combined.sort_values(by=['id'])
    df_combined.to_csv('../../data/edit/df_union_combined.csv')
    return

