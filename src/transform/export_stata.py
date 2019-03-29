import re
import csv
import json
import urllib
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

def column_names(df):
    list_cols = df.columns.tolist()
    #print list_cols
    
    # Remove special characters
    for index,item in enumerate(list_cols):
        list_cols[index] = item.replace(' & ',' ') \
                               .replace(':','') \
                               .replace(',','') \
                               .replace('+','')
    
    # Replace blanks with underscores
    for index,item in enumerate(list_cols):
        list_cols[index] = item.replace(' ','_')
    
    # Numbers cannot lead var names
    for index, item in enumerate(list_cols):
        if item[0].isdigit():
           list_cols[index] = 'var_' + item
           
    # Stata does not recognize capital letters in var names
    for index, item in enumerate(list_cols):
        list_cols[index] = item.lower()
           
    #print list_cols
    return list_cols

def change_col_names(df):
    list_cols_old = df.columns.tolist()
    list_cols_new = column_names(df)
    for index,item in enumerate(list_cols_old):
        df = df.rename(columns={item:list_cols_new[index]})
    print df.columns.tolist()
    return df

def output_sample_stata(df,sample_key):
    df = change_col_names(df)
    df.to_csv('../../data/edit/sample_{}.csv'.format(sample_key))
    return
    
def output_representative_stata(df, rep_key):
    df = change_col_names(df)
    df.to_csv('../../data/edit/representative_{}.csv'.format(rep_key))
    return