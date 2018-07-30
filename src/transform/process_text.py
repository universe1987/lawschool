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

def learn_text():
    df_details = pd.read_csv('../../data/edit/df_details.csv')
    print df_details.columns
    
    short_var_list = ['College Name or Type', 'Major', 'City','State','Race','Gender', 'Class Rank', 'Years out of Undergrad']
    long_var_list = ['extra curricular', 'additional info']
    
    for index, item in enumerate(short_var_list):
        print item, df_details[item].nunique(), df_details[item].unique()
        df = pd.Series(df_details[item].unique())
        df.to_csv('../../data/edit/{}_unique.csv'.format(item))
    return

def clean_state_city():
    df_details = pd.read_csv('../../data/edit/df_details.csv')
    for item in ['College Name or Type','State','City']:
        df_details[item] = df_details[item].fillna('').str.lower() # May transfer to learn_text
    df_details.to_csv('../../data/edit/df_details_sc.csv')
    #print len(df_details),df_details['College Name or Type'].nunique()
    return df_details

