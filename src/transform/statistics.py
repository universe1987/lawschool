import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict
from utils import keep_ascii_file, filter_good_applicants, get_stats
from select_tables import select_application_tables, select_search_tables, select_user_tables, select_user_tables2
from process_merge import process_app_data, process_rank_data, merge_app_rank
from clean import clean_app_rank, clean_app_date, clean_sample

import scipy
import statsmodels.api as sm
import statsmodels.formula.api as smf

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch

def stat_sample(df_app):
    dic_count = {}
    dic_detail = {}
    for yr in range(2003,2016):
        df_yr = df_app[df_app['Year'] == yr]
        
        dic_count[yr-2003] = {}
        dic_count[yr-2003]['Number of Applicants'] = pd.DataFrame(df_yr['User Name'].agg(['nunique']))
        dic_count[yr-2003]['Number of Applicants Reporting Enrollment Decisions'] = pd.DataFrame(df_yr.loc[df_yr['Attend']==1,'User Name'].agg(['nunique']))
        type_list = ['ED','SP']
        for tp in type_list:
            dic_count[yr-2003]['Number of Applicants with {} Apps'.format(tp)] = pd.DataFrame(df_yr.loc[df_yr[tp]==1,'User Name'].agg(['nunique']))
        
        df_school = df_yr.groupby(['Law School'])['User Name'].count().reset_index()
        dic_count[yr-2003]['Number of Schools'] = pd.DataFrame(df_school['Law School'].agg(['nunique']))
        dic_count[yr-2003]['Number of Schools with Over 100 Apps in Data'] = pd.DataFrame(df_school.loc[df_school['User Name']>=100,'Law School'].agg(['nunique']))
        for tp in type_list:
            dic_count[yr-2003]['Number of Schools with {} Tracks'.format(tp)] = pd.DataFrame(df_yr.loc[df_yr['{}_school'.format(tp)]==1,'Law School'].agg(['nunique']))
        #print 'year=',yr, dic_count[yr-2003]

        dic_detail[yr-2003] = {}
        dic_detail[yr-2003]['Time to Apply (Days since Sep 1)']=pd.DataFrame(df_yr['Sent_delta'].agg(['mean','std','count']))
        #print dic_detail[yr-2003]['Time to Apply (Days since Sep 1)'].iloc[:,0]
        dic_detail[yr-2003]['Time to Hear Back (Days since sent)']=pd.DataFrame(df_yr[['Decision_delta']].agg(['mean','std','count']))
        action_list = ['Sent','grant yes']
        name_list = ['Applications','Number of Grants']
        for index, act in enumerate(action_list):
            df_act = df_yr.groupby(['User Name'])['{}'.format(act)].count().reset_index()
            dic_detail[yr-2003]['{} Per Capita'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
        action_list = ['Accepted','Rejected','Pending','Waitlisted','grant yes']
        name_list = ['Admissions','Rejections','Pending','Waitlists','Number of Grants']
        for index, act in enumerate(action_list):
            df_act = df_yr.groupby(['User Name'])['{}'.format(act)].sum().reset_index()
            dic_detail[yr-2003]['{} Per Capita'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
        action_list = ['grant']
        name_list = ['Size of Grants']
        for index, act in enumerate(action_list):
            df_act = df_yr.groupby(['User Name'])['{}'.format(act)].mean().reset_index()
            dic_detail[yr-2003]['{} Per Capita'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
        #dic_gpa_lsat = 
        #print 'year=',yr,dic_detail[yr-2003]
    return dic_count, dic_detail
    
