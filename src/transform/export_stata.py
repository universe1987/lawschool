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

from utils import keep_ascii_file, filter_good_applicants, get_stats
from select_tables import select_application_tables, select_search_tables, select_user_tables, select_user_tables2
from select_tables_details import select_applicant_information_tables, select_demographic_information_tables,\
                                  select_extra_curricular_information_tables,select_additional_info_updates_tables
from process_merge import process_app_data, process_rank_data, merge_app_rank
from clean import gen_dummy, merge_app_details,gen_samples,clean_app_rank, clean_app_date, clean_sample
from statistics import summary_statistics_applicants,summary_statistics_schools
from process_text import learn_text,clean_state_city
                         
from process_text_race import clean_race_ethnicity
from process_text_college_baseline import match_college_name_type,prune_college_name_type, tallal_college_name_type,\
                                          topN_college_name_type,match_topN_college_name_type_location,\
                                          match_union_college_name_type_location,usnews_acronym_flagship_merge,\
                                          match_tallal_college_name_type
from process_text_college_topN import fill_topN_merge_univ, fill_topN_merge_lac
from process_text_college_union import fill_union_merge_univ
from process_text_college_vague import fill_vague_merge_univ
from process_text_college_binder import school_usnews_merge, school_usnews_details_merge,vague_details_merge,\
                                        exact_usnews_merge,exact_usnews_details_merge,tallal_usnews_details_merge,\
                                        college_name_conclude
from process_text_major import lsac_majors,breakdown_majors,merge_majors_lsac_lsn,tallal_majors_lsac_lsn,\
                               major_clean_binder
from process_text_extracurricular import extract_extracurriculars
from process_numerical import learn_numerical

import scipy
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn import linear_model

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

def output_stata(df,sample_key):
    df = change_col_names(df)
    df.to_csv('../../data/edit/sample_{}.csv'.format(sample_key))
    return