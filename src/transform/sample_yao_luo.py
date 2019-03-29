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
from scipy.stats.mstats import mode
import matplotlib.pyplot as plt

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

def extract_ec_info(obs):
    df = pd.read_csv('../../data/edit/df_details_race_college_cleaned.csv')
    df = df[['User Name','extra curricular',	'additional info']]
    df = df.head(obs)
    df.to_csv('../../data/edit/sample_ec_info.csv')
    return df

def extract_outcome(obs,df_ec_info,df_str):
    df_ec_info = extract_ec_info(obs)
    df = pd.read_csv('../../data/edit/{}.csv'.format(df_str)) 
    df = df[['User Name','Sent_delta','Decision_delta','Waitlisted','Accepted','Pending',
             'Rejected','LSAT','GPA','rank_cross','unranked','Attend','Attend Reported']]
    df_all = df_ec_info[['User Name']].merge(df,on='User Name',how='left').reset_index()
    df_all.to_csv('../../data/edit/sample_ec_info_results.csv')
    return

if __name__ == '__main__':
    obs = 2000
    df_ec_info = extract_ec_info(obs)
    extract_outcome(obs,df_ec_info,'df_all_samples_a2')