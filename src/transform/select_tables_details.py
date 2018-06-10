import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch


def select_applicant_information_tables():
    user_applications = glob(os.path.join(JSON_DIR, 'user_*_applicant_information.json'))
    folder_len = len(JSON_DIR)
    user_names = ['_'.join(s[folder_len:].split('_')[1:-2]) for s in user_applications]
    sw = StopWatch()
    print len(user_applications)
    
    lists = []
    for i, filename in enumerate(user_applications):
        if (i + 1) % 10000 == 0:
            print i
        with open(filename, 'rb') as fp:
            table = json.load(fp)
            line = [user_names[i], table['College Name or Type'], table['Major'],table['Degree GPA'],
                    table['LSAT 2'], table['LSAT 3'], table['LSAT 1'], table['LSDAS GPA'],
                    table['Class Rank'], table['LSAT']]
            lists.append(line)
    df=pd.DataFrame(lists,columns=['User Name','College Name or Type', 'Major', 'Degree GPA', 'LSAT 2',
                                  'LSAT 3','LSAT 1','LSDAS GPA','Class Rank','LSAT'])
    sw.tic('generating applicant information')
    return df
       
def select_extra_curricular_information_tables():
    user_applications = glob(os.path.join(JSON_DIR, 'user_*_extra_curricular_information.json'))
    folder_len = len(JSON_DIR)
    user_names = ['_'.join(s[folder_len:].split('_')[1:-3]) for s in user_applications]
    sw = StopWatch()
    print len(user_applications)
    
    lists = []
    for i, filename in enumerate(user_applications):
        if (i + 1) % 10000 == 0:
            print i
        with open(filename, 'rb') as fp:
            table = json.load(fp)
            line = [user_names[i], table['text']]
            lists.append(line)
    df=pd.DataFrame(lists,columns=['User Name','text'])
    df = df.rename(columns={'text': 'extra curricular'})
    sw.tic('generating extra curricular information')
    return df
    
def select_additional_info_updates_tables():
    user_applications = glob(os.path.join(JSON_DIR, 'user_*_updates.json'))
    folder_len = len(JSON_DIR)
    user_names = ['_'.join(s[folder_len:].split('_')[1:-4]) for s in user_applications]
    sw = StopWatch()
    print len(user_applications)
    
    lists = []
    for i, filename in enumerate(user_applications):
        if (i + 1) % 10000 == 0:
            print i
        with open(filename, 'rb') as fp:
            table = json.load(fp)
            line = [user_names[i], table['text']]
            lists.append(line)
    df=pd.DataFrame(lists,columns=['User Name','text'])
    df = df.rename(columns={'text': 'additional info'})
    sw.tic('generating additional info updates information')
    return df
    
def select_demographic_information_tables():
    user_applications = glob(os.path.join(JSON_DIR, 'user_*_demographic_information.json'))
    folder_len = len(JSON_DIR)
    user_names = ['_'.join(s[folder_len:].split('_')[1:-2]) for s in user_applications]
    sw = StopWatch()
    print len(user_applications)
    
    lists = []
    for i, filename in enumerate(user_applications):
        if (i + 1) % 10000 == 0:
            print i
        with open(filename, 'rb') as fp:
            table = json.load(fp)
            line = [user_names[i], table['City'], table['State'],table['Race'],
                    table['Years out of Undergrad'],table['Gender']]
            lists.append(line)
    df=pd.DataFrame(lists,columns=['User Name','City','State','Race',
                                   'Years out of Undergrad','Gender'])
    sw.tic('generating demographic information')
    return df
    

