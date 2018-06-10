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

#step 1: extract the vague name data
#step 2: identify the foreign name, marked as group "foreign"
#step 3: in the produced csv, mark "enthusiastic",'positive','neutral','bad'
def fill_vague_merge_univ():
    # contains almost no identifying information about colleges
    # mostly some vagues descriptive words
    
    df = pd.read_csv('../../data/entry/College Name or Type_unique_marked2.csv')
    df = df.fillna('').astype(str)
    
    df_vague = df[df['name']+df['guess']+df['big10']+df['pac']+df['hbcu']+df['sisters']\
                  + df['public_ivy'] + df['west_ivy'] + df['new_ivy'] \
                  + df['little_ivy'] + df['sec'] + df['flagship']=='']
    print len(df_vague['College Name or Type'])
    print df_vague['College Name or Type'].nunique()
    df_vague.to_csv('../../data/edit/df_vague_raw.csv')
    df_vague['groups'] = ''
    
    with open('fill_vague_merge.json', 'rb') as file:
        vague_groups = json.load(file)
    
    for index, row in df_vague.iterrows():
        if any(x in row['College Name or Type'] for x in vague_groups["foreign_contain"]):
            df_vague.loc[index,'groups'] = 'foreign'
        elif any(x in row['College Name or Type'] for x in vague_groups["foreign_equal"]):
            df_vague.loc[index,'groups'] = 'foreign'        
        elif any(x in row['College Name or Type'] for x in vague_groups["bad"]):
            df_vague.loc[index,'groups'] = 'bad'
        elif any(x in row['College Name or Type'] for x in vague_groups["positive"]):
            df_vague.loc[index,'groups'] = 'positive'
        elif any(row['College Name or Type'] ==x for x in vague_groups["tallal"]):
            df_vague.loc[index,'groups'] = 'tallal'
        else:
            df_vague.loc[index,'groups'] = 'neutral'
   
    #df_vague = df_vague[df_vague['groups']=='']
    df_vague = df_vague[['College Name or Type','groups']]
    print df_vague['College Name or Type'].nunique()
    df_vague.to_csv('../../data/edit/df_vague.csv')   
        
    '''
    list_unmatched = df_vague['College Name or Type'].tolist()
    string_unmatched = ' '.join(str(x) for x in list_unmatched).replace(',',' ').replace(';',' ')\
                       .replace('(',' ').replace(')',' ').replace('\\',' ').replace('/',' ')
    
    list_break = string_unmatched.split(' ')
    #print list_break
    
    c = Counter(list_break)
    df_freq = pd.DataFrame({'values':c.values(),'keys':c.keys()}).sort_values(ascending=False,by=['values'])
    df_freq.to_csv('../../data/edit/df_freq.csv')
    '''

    return

