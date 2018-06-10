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
 

def clean_race_ethnicity():
    df_details = pd.read_csv('../../data/edit/df_details.csv')
    df_details['Race'] = df_details['Race'].fillna('').str.lower() # May transfer to learn_text
    df_details['Race2'] = df_details['Race']
    
    with open('text_race.json', 'rb') as file:
        race_groups = json.load(file)
    
    # The orders below cannot be swamped! Keep the order!

    for index, item in enumerate(race_groups["contains"]['white']):
        df_details.loc[df_details['Race'].str.contains(item),'Race2'] = 'white'
    for index, item in enumerate(race_groups["equal_to"]['white']):
        df_details.loc[df_details['Race'] == item,'Race2'] = 'white'
    for index, item in enumerate(race_groups["contains"]['asian and pacific islander']):
        df_details.loc[df_details['Race'].str.contains(item),'Race2'] = 'asian and pacific islander'
    for index, item in enumerate(race_groups["equal_to"]['asian and pacific islander']):
        df_details.loc[df_details['Race'] == item,'Race2'] = 'asian and pacific islander'
    for index, item in enumerate(race_groups["contains"]['hispanic']):
        df_details.loc[df_details['Race'].str.contains(item),'Race2'] = 'hispanic'
    for index, item in enumerate(race_groups["equal_to"]['hispanic']):
        df_details.loc[df_details['Race'] == item,'Race2'] = 'hispanic'
    for index, item in enumerate(race_groups["contains"]['mexican']):
        df_details.loc[df_details['Race'].str.contains(item),'Race2'] = 'mexican'
    for index, item in enumerate(['not mexican']):
        df_details.loc[df_details['Race'] == item,'Race2'] = 'hispanic'
    for index, item in enumerate(race_groups["contains"]['puerto rican']):
        df_details.loc[df_details['Race'].str.contains(item),'Race2'] = 'puerto rican'
    for index, item in enumerate(race_groups["contains"]['african']):
        df_details.loc[df_details['Race'].str.contains(item),'Race2'] = 'african'
    for index, item in enumerate(race_groups["equal_to"]['african']):
        df_details.loc[df_details['Race'] == item,'Race2'] = 'african'
    for index, item in enumerate(race_groups["equal_to"]['']+['<a href=\\"http://www']):
        df_details.loc[df_details['Race'] == item,'Race2'] = ''
    for index, item in enumerate(race_groups["equal_to"]['Mixed, probably not urm']):
        df_details.loc[df_details['Race'] == item,'Race2'] = 'Mixed, probably not urm'
    for index, item in enumerate(race_groups["equal_to"]['Native American or alaskan']):
        df_details.loc[df_details['Race'] == item,'Race2'] = 'Native American or alaskan'
                
    print 'Race2', df_details['Race2'].nunique(), df_details['Race2'].unique()
    print 'Race2', len(df_details[df_details['Race2']!=''])
    df = pd.Series(df_details['Race2'].unique())
    df.to_csv('../../data/edit/Race2_unique.csv')
    df_details.to_csv('../../data/edit/df_details.csv')
    return