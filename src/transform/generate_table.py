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
from clean import clean_app_rank, clean_app_date, clean_sample
from statistics import stat_sample
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


# sample files in json folder
# user_crackedegg_additional_info_&_updates.json
# user_crackedegg_applicant_information.json
# user_crackedegg_application.json
# user_crackedegg_demographic_information.json
# user_crackedegg_extra_curricular_information.json



if __name__ == '__main__':    
    #process_app_data()
    #process_rank_data()
    #merge_app_rank()
    
    #learn_text()
    #======= Race ========#
    #clean_race_ethnicity()
    
    #======= State & City ========#
    #clean_state_city()
    
    #======= College Name or Type ========#
    #usnews_acronym_flagship_merge()
    #learn_college_name_type()
    #prune_college_name_type()
    #tallal_college_name_type()
    #match_tallal_college_name_type()
    #topN_college_name_type()
    #match_topN_college_name_type_location()
    #fill_topN_merge_univ()
    #fill_topN_merge_lac()
    #match_union_college_name_type_location()
    #fill_union_merge_univ()
    #fill_vague_merge_univ()
    #school_usnews_merge()
    #school_usnews_details_merge()
    #vague_details_merge()
    #tallal_usnews_details_merge()
    #exact_usnews_merge()
    #exact_usnews_details_merge()
    #college_name_conclude()
    
    #======= Major ========#
    #lsac_majors()
    #breakdown_majors()
    #merge_majors_lsac_lsn()
    #tallal_majors_lsac_lsn()
    #major_clean_binder()
    
    #======= Extracurricular Activities========#
    #extract_extracurriculars()
    
    raw_input('lalalalala')
    
    
    df_app = pd.read_csv('../../data/edit/app_matched.csv')
    df_app_new = clean_app_rank(df_app)
    
    df_app_new = pd.read_csv('../../data/edit/app_new.csv')
    df_app_date = clean_app_date(df_app_new)   
    
    df_app_date = pd.read_csv('../../data/edit/app_date.csv')
    df_app_clean = clean_sample(df_app_date)
    dic_count, dic_detail = stat_sample(df_app_clean)
    
    #===== Export Regression Results ======#
    # Go to Stata, sadly
    #===== Export Summary Statistics ======#
    row_name = [
			['Summary_Statistics_I', 'Number of Schools','Number of Schools with Over 100 Apps in Data',
			 'Number of Schools with ED Tracks','Number of Schools with SP Tracks','Number of Applicants',
			 'Number of Applicants with ED Apps','Number of Applicants with SP Apps',
			 'Number of Applicants Reporting Enrollment Decisions'],
			['Summary_Statistics_II', 'Time to Apply (Days since Sep 1)','Time to Hear Back (Days since sent)',
			 'Applications Per Capita','Admissions Per Capita','Rejections Per Capita','Waitlists Per Capita',
			 'Pending Per Capita','Number of Grants Per Capita','Size of Grants Per Capita'],
		]
    rename_lookup = [{'nunique':'Obs'},{'mean':'Mean','std':'SD','count':'Obs'}]
    col_name = [['Obs'],['Mean','SD','Obs']]
    for yr in range(2006,2016):
        for index, stats in enumerate([dic_count[yr-2003],dic_detail[yr-2003]]):
			df = pd.DataFrame()
			for keys,values in stats.iteritems():
				df = df.append(values.transpose().assign(Variable=[keys]))
			df = df.set_index('Variable',drop=False)
			row_head = row_name[index][0]
			row_tail = row_name[index][1:]
			df = df.reindex(row_tail).rename(columns=rename_lookup[index])
			df2tex(df, '../../model/tables/','{}_{}.tex'.format(row_head,yr), "%8.2f", 0, col_name[index], ['Variable'], col_name[index])
    
