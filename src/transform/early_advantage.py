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

def index_construct(df_in,var_index,cutoff_thresholds):
    df_index = df_in[var_index].astype(float).groupby(pd.cut(df_in[var_index], np.percentile(df_in[var_index], cutoff_thresholds), include_lowest=True)).agg(['min','max'])
    df_index['var_index_new'] = 'Days ' + df_index['min'].astype(int).astype(str) + ' to ' + df_index['max'].astype(int).astype(str)
    df_index = df_index[['var_index_new']]
    return df_index
    

def admission_correlation(df_in):    
    var_index = 'Sent_delta'
    cutoff_thresholds = [0, 20, 40, 60, 80, 100]
    df_index = index_construct(df_in,'Sent_delta',cutoff_thresholds)
    
    percent_list = [['Accepted','Rejected','Waitlisted','Pending'],
                 ['Gender','white','asian and pacific islander','hispanic','Mixed, probably not urm',
                  'minority'], 
                 ['social sciences','arts & humanities','business & management', 'stem & others'],
                 ['Ranked Nationally','Ranked Regionally','Described Positively','Described Negatively',
                  'Described Neutrally'],
                 ['unranked','unranked_2010'],
                 ['In Undergrad', '1-2 Years', '3-4 Years', '5-9 Years', '10+ Years'],
                 ['EC at all','Greek', 'Student Societies','Athletic/Varsity', 'Community/Volunteer'], 
                 ['Legal Internship','Non-legal Internship', 'Legal Work Experience', 'Non-legal Work Experience'],
                 ['Military','Overseas','Leadership','Strong Letters']]
    percent_list_new = [['Offers','Rejections','Waitlists','Pending'],
                 ['Male','White','Asian','Hispanic','Mixed',
                  'URM'], 
                 ['Social Sciences','Arts/Humanities','Business/Management', 'STEM/Others'],
                 ['Ranked Nationally','$\sim$ Regionally','Described Positively','$\sim$ Negatively',
                  '$\sim$ Neutrally'],
                 ['Not Ranked','Not Ranked in 2010'],
                 ['In Undergrad', '1-2 Years', '3-4 Years', '5-9 Years', '10+ Years'],
                 ['Listing some EC at least','Greek Society','Non-Greek Student Societies','Sports','Community Service'],
                 ['Legal Internship', 'Non-legal Internship', 'Legal Work Experience', 'Non-legal Work Experience'],
                 ['Military','Overseas','Leadership', 'Strong Letters'] ]
    percent_list_name = ['Early_Adv_pct_1', 'Early_Adv_pct_2','Early_Adv_pct_3','Early_Adv_pct_4','Early_Adv_pct_5','Early_Adv_pct_6','Early_Adv_pct_7','Early_Adv_pct_8','Early_Adv_pct_9']
    
    mean_list = [['Decision_delta'],['LSAT','GPA'],['rank_cross','rank_2010_cp']]
    mean_list_new = [['When to Hear Back (\# Days since sent)'],['LSAT','GPA'],['Rank','Rank in 2010']]
    mean_list_name = ['Early_Adv_mean_1', 'Early_Adv_mean_2','Early_Adv_mean_3' ]
    
    dic_outcomes = {}
    for index, sublist in enumerate(percent_list):
        dic_outcomes[percent_list_name[index]] = df_in[sublist].astype(float).groupby(pd.cut(df_in[var_index], np.percentile(df_in[var_index], cutoff_thresholds), include_lowest=True)).mean()*100.0
        New_Labels = percent_list_new[index]
        dic_outcomes[percent_list_name[index]].columns = New_Labels
        
    for index, sublist in enumerate(mean_list):
        dic_outcomes[mean_list_name[index]] = df_in[sublist].astype(float).groupby(pd.cut(df_in[var_index], np.percentile(df_in[var_index], cutoff_thresholds), include_lowest=True)).mean()
        New_Labels = mean_list_new[index]
        dic_outcomes[mean_list_name[index]].columns = New_Labels    
    
    for key, value in dic_outcomes.iteritems():
        dic_outcomes[key] = dic_outcomes[key].join(df_index).set_index('var_index_new',drop=False)
        print dic_outcomes[key]
        
    return dic_outcomes
     
# Need to include law school ranks as well.  