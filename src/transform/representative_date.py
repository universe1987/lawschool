import re
import csv
import ast
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


def import_official_date():
    f = open('../../data/various/official timing of applications/qpig numbers.txt','r')
    f_str = f.read()
    app_raw = ast.literal_eval(f_str)
    print app_raw
    
    date_raw = []
    for index, item in enumerate(app_raw):
        date_raw.append(index*7)
        date_raw[index] = date_raw[index] 
    print date_raw
    return app_raw, date_raw

def convert_to_sep1():
    # Import official data
    app_raw, date_raw = import_official_date()
    
    # Calculate difference between opening dates
    delta = date(2010,9,1) - date(2010,8,13)
    delta_d = delta.days
    
    # Initialize opening dates in lsn data
    date_edit = []
    for index, item in enumerate(date_raw):
        date_edit.append(date_raw[index]+delta_d)
    date_edit = [float(i) for i in date_edit]
    print date_edit
    
    # Find matches in official data
    for index, item in enumerate(date_raw):
        dif = date_edit[0] - item
        if (dif>=0) & (dif<date_raw[1]-date_raw[0]):
            break
    index_dif = index
    day_dif = dif
    
    # Convert the apps data with starting date as Sep 1
    app_edit = []
    len_edit = len(app_raw)-index_dif-1
    for index, item in enumerate(app_raw[0:len_edit]):
        index_shift = index + index_dif
        val_shift = app_raw[index_shift] + float(day_dif)/(date_raw[1]-date_raw[0])*(app_raw[index_shift+1]-app_raw[index_shift])
        app_edit.append(val_shift)
    app_edit = [float(i) for i in app_edit]
    print app_edit
    
    return app_edit, date_edit
    
    
def lsn_app_date():
    df = pd.read_csv('../../data/edit/sample_c1_py.csv')
    df_first = df.groupby(['User Name'])['Sent_delta'].min().reset_index()
    print len(df_first),df_first['User Name'].nunique()
    
    app_edit, date_edit = convert_to_sep1()
    len_effective = len(date_edit)-4
    
    dic_lsn_date = {}
    for item in date_edit[0:len_effective]:
        dic_lsn_date[item] = []
    
    total = 0.0
    total_o = 0.0
    print df_first['Sent_delta'].max(),df_first['Sent_delta'].min()
    for index, row in df_first.iterrows():
        total_o  = total_o + 1.0
        for index_d,item_d in enumerate(date_edit[0:len_effective-1]):
            #print 'd',item_d
            if (row['Sent_delta']+19.0>=item_d) & (row['Sent_delta']+19.0<date_edit[index_d+1]):
                dic_lsn_date[item_d].append(row['Sent_delta'])
                total = total + 1.0
                continue
        #raw_input('signn')
    print total, total_o
    
    app_lsn = []
    for index,item in enumerate(date_edit[0:len_effective]):
        app_lsn.append(float(len(dic_lsn_date[item]))/total*100.0)   
    print 'sum',sum(app_lsn)
    
    # Convert to CDF
    app_lsn_cdf = []
    for index in range(1,len(app_lsn)-2):
        app_lsn_cdf[index] = app_lsn_cdf[index-1]+app_lsn[index]
    
    df1 = pd.Series(app_lsn_cdf[0:len_effective],name='lsn').reset_index()
    df2 = pd.Series(app_edit[0:len_effective],name='official').reset_index()
    df = pd.concat([df1, df2], axis=1)
    print df.head()
    df.to_csv('../../data/edit/representative_app_date.csv')
    return
