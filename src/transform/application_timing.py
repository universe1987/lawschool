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


def app_date_distribution(df_in):    
    # Span (Latest App - Earliest App), SD (All Apps)
    stats_list = ['mean','std','count']
    stats_list_index = ['Mean','SD','Obs']
    
    df_dist = df_in.groupby(['User Name'])['Sent_delta'].agg(['max','min','std']).reset_index()
    df_dist['span'] = df_dist['max'] - df_dist['min']
    df_outcome = df_dist[['span','std']].agg(stats_list)
    
    New_Labels = ['Span of App Dates','Std of App Dates']
    df_outcome.columns = New_Labels
    df_outcome['stats'] = stats_list_index
    
    print df_outcome
    return df_outcome

def app_date_rank_distribution(df_in):
    # Span (Rank of Latest App - Rank of Earliest App), Span (Highest Rank - Lowest Rank), SD (All Ranks)
    return
     
# Need to include law school ranks as well.  