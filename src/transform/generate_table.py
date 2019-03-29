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
from statistics import summary_statistics_applicants,summary_statistics_schools,summary_statistics_by_schools
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
from process_text_extracurricular import extract_extracurriculars, merge_back_extracurricular_classified
from process_numerical import learn_numerical
from early_advantage import admission_correlation
from application_timing import app_date_distribution
from eager_schools import offer_date_dist
from export_stata import column_names,change_col_names,output_sample_stata,output_representative_stata
from representative_app_adm import import_official_app_offer,match_official_app_names,match_all,\
                                   official_app_stat_pool,lsn_app_stat_pool,merge_official_lsn_app_adm
from representative_date import lsn_app_date
from app_patterns_weekends_lsat import apply_only_on_weekends, LSAT_release,LSAT_release_df_all,\
                                       LSAT_release_did_stats, LSAT_release_export_stats
from simulation import simulate_both
#from app_gp import simulate_stats,calculate_simu_stats,export_simu_stats
from school_adm_patterns import adm_patterns
from sample_yao_luo import extract_ec_info,extract_outcome 
from pending_apps import extract_best_worst_offer,compare_pending_best_worst_offer,export_pending_best_worst_offer
from app_type_round import group_basic_stats,export_group_stats
from law_school_char import load_school_char

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
    #======= Load Data ========#   
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
    ##learn_college_name_type() seems redundant
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
    
    #======= Gender, Years Since Graduation =====#
    #learn_numerical()
    
    #======= Extracurricular Activities========#
    #extract_extracurriculars()
    #merge_back_extracurricular_classified()
    #print ('Table Generated!')
    
    #======= Create Dummy Variables ==========#
    #gen_dummy()
    
    #======= Clean Data Format of Application Data ================#
    #df_app = pd.read_csv('../../data/edit/app_matched.csv')
    #df_app_new = clean_app_rank(df_app)
    
    #df_app_new = pd.read_csv('../../data/edit/app_new.csv')
    #df_app_date = clean_app_date(df_app_new)   
    
    #df_app_date = pd.read_csv('../../data/edit/app_date.csv')
    #df_app_clean = clean_sample(df_app_date)
    
    ###dic_count, dic_detail = stat_sample(df_app_clean)
    ###print dic_count, dic_detail
    ###'Unnamed: 0', 'Unnamed: 0.1'
    
    #======= Import Law School Characteristics ======#
    load_school_char()
    
    #======= Create Various Samples ==========#
    merge_app_details()    
    df_all_samples = gen_samples()
    output_sample_stata(df_all_samples['a2'],'a2')
    for x in ['a2','c1','d1']:
        df_all_samples['{}'.format(x)].to_csv('../../data/edit/df_all_samples_{}.csv'.format(x))
    
    #======= Divert: Representative ===========#
    #import_official_app_offer()
    #match_official_app_names()
    #match_all()
    #official_app_stat_pool()
    #lsn_app_stat_pool()
    #df_official_lsn = merge_official_lsn_app_adm()
    #output_representative_stata(df_official_lsn,'apps_adm')
    #lsn_app_date()
    
    #======= Check App Patterns: Weekends & LSAT release ===================#
    #apply_only_on_weekends('c1')
    #LSAT_release()
    #df_all_lsat_c1 = LSAT_release_df_all()
    #intvl = 7.0
    #dic_lsat_c1,dic_lsat_only_c1=LSAT_release_did_stats(df_all_lsat_c1,intvl,['User Name'])
    #LSAT_release_export_stats(dic_lsat_c1,intvl,'dic_lsat_c1')
    #LSAT_release_export_stats(dic_lsat_only_c1,intvl,'dic_lsat_only_c1')
    
    #======= Check App Patterns: Groups (gp) Submit Apps After Offers Arrive===================#
    #======= Bad Codes. Abandon ALL=====#
    ###simulate_student()
    ###df_all, df_user_gp_all, df_rounds_gp_all,df_raw_gp_all,\
    ###df_pre_offer, df_get_offer, df_post_offer,df_apps_offer_ranks = simulate_stats()
    ###df_stats_dic = calculate_simu_stats(df_user_gp_all, df_rounds_gp_all, df_all,df_raw_gp_all,df_pre_offer,df_get_offer,df_post_offer,df_apps_offer_ranks)
    ###export_simu_stats(df_stats_dic)
    ###output_sample_stata(df_all,'app_group_affil')   
    
    #======= Check App Patterns: Learn from Public Information ===================#
    simulate_both('d1')
    df_stats_dic = group_basic_stats('d1')
    export_group_stats(df_stats_dic)
    
    
    #======= Check Adm Patterns ===================#
    #adm_pattern()
    
    #======= Generate Sample Data to Yao Luo ========#
    #obs = 2000
    #df_ec_info = extract_ec_info(obs)
    #extract_outcome(obs,df_ec_info,'df_all_samples_a2')
    
    #======= Pending Apps Statistics ================#
    #df_both = extract_best_worst_offer('df_all_samples_c1')
    #dic_pending = compare_pending_best_worst_offer(df_both)
    #export_pending_best_worst_offer(dic_pending)
    
    #======= Back to Main Sample: Calculate Summary Statistics ==========#
    #df_in = pd.read_csv('../../data/edit/df_all_samples_a2.csv')
    #summary_statistics_by_schools(df_in)
    
    ss_applicants_1 = {}
    ss_applicants_2 = {}
    ss_applicants_3 = {}
    ss_applicants_4 = {}
    ss_applicants_5 = {}
    ss_applicants_6 = {}
    ss_schools_1 = {}
    ss_schools_2 = {}
    ss_schools_3 = {}
    
    for c in ['a1','a2',
              'c1','c2','c3','c4','c5','c6','c7',
              'd1','d2','d3','d4','d5','d6','d7',
              'e1','e2','e3','e4','e5','e6','e7']:
        ss_applicants_1['{}'.format(c)],ss_applicants_2['{}'.format(c)],ss_applicants_3['{}'.format(c)],ss_applicants_4['{}'.format(c)],ss_applicants_5['{}'.format(c)],ss_applicants_6['{}'.format(c)] = summary_statistics_applicants(df_all_samples['{}'.format(c)])
        ss_schools_1['{}'.format(c)],ss_schools_2['{}'.format(c)],ss_schools_3['{}'.format(c)] = summary_statistics_schools(df_all_samples['{}'.format(c)])
    
    #===== Export Summary Statistics ======#
    row_name = [
			['Summary_Statistics_Schools_I', 'Not Ranked','Not Ranked in 2010'],
			['Summary_Statistics_Schools_II', 'Rank','Rank in 2010'],
			['Summary_Statistics_Schools_III', '\# Applications Per School','\# Offers Per School','\# Rejections Per School','\# Pending Per School','\# Waitlists Per School'],
			['Summary_Statistics_Applicants_I', 'When to Apply (\# Days since Sep 1)','When to Hear Back (\# Days since sent)',
			 '\# Applications Per Capita','\# Offers Per Capita','\# Rejections Per Capita','\# Waitlists Per Capita',
			 '\# Pending Per Capita','GPA','LSAT'],
			['Summary_Statistics_Applicants_II', 'Male','White', 'Asian', 'Hispanic','Mixed',   
             'African (URM)','Mexican (URM)', 'Puerto Rican (URM)', 'Native American or Alaskan (URM)'],
            ['Summary_Statistics_Applicants_III', 'Social Sciences', 'Arts \& Humanities', 'Business \& Management', 
             'Natural Sciences', 'Engineering', 'Health Professions','Other'],
            ['Summary_Statistics_Applicants_IV','Ranked Nationally','Ranked Regionally','Described Positively',
             'Described Negatively','Described Neutrally'],
            ['Summary_Statistics_Applicants_V','In Undergrad','1-2 Years', '3-4 Years', '5-9 Years', '10+ Years'],
            ['Summary_Statistics_Applicants_VI','Listing some EC at least','Greek Society','Non-Greek Student Societies','Sports',
             'Community Service','Legal Internship','Non-legal Internship','Legal Work Experience','Non-legal Work Experience', 
             'Military','Overseas','Leadership', 'Strong Letters' ]
		 
		]
    rename_lookup = [{'mean':'Percent','count':'Obs'},{'mean':'Mean','std':'SD','count':'Obs'},{'mean':'Mean','std':'SD','count':'Obs'},
                     {'mean':'Mean','std':'SD','count':'Obs'},{'mean':'Percent','count':'Obs'},{'mean':'Percent','count':'Obs'},
                     {'mean':'Percent','count':'Obs'},{'mean':'Percent','count':'Obs'},{'mean':'Percent','count':'Obs'}]
    col_name = [['Percent','Obs'],['Mean','SD','Obs'],['Mean','SD','Obs'],
                ['Mean','SD','Obs'],['Percent','Obs'],['Percent','Obs'],
                ['Percent','Obs'],['Percent','Obs'],['Percent','Obs']]
    ss_list = ['a1','a2','c1','c2','c3','c4','c5','c6','c7','d1','d2','d3','d4','d5','d6','d7',
               'e1','e2','e3','e4','e5','e6','e7']
    for tp in ss_list:
        for index, stats in enumerate([ss_schools_1[tp],ss_schools_2[tp],ss_schools_3[tp],ss_applicants_1[tp],ss_applicants_2[tp],ss_applicants_3[tp],ss_applicants_4[tp],ss_applicants_5[tp],ss_applicants_6[tp]]):
			df = pd.DataFrame()
			for keys,values in stats.iteritems():
				df = df.append(values.transpose().assign(Variable=[keys]))
			df = df.set_index('Variable',drop=False)
			row_head = row_name[index][0]
			row_tail = row_name[index][1:]
			df = df.reindex(row_tail).rename(columns=rename_lookup[index])
			df2tex(df, '../../model/tables/','{}-{}.tex'.format(row_head,tp), "%8.2f", 0, col_name[index], ['Variable'], col_name[index])
    
    
    #======= Early Advantage ==========#
    ss_list = ['a1','a2','c1','c2','c3','c4','c5','c6','c7','d1','d2','d3','d4','d5','d6','d7',
               'e1','e2','e3','e4','e5','e6','e7']
    dic_outcomes = {}
    for tp in ss_list:
        print tp
        dic_outcomes[tp] = admission_correlation(df_all_samples[tp])
        
    #======= Export Early Advantage ==========#
    percent_list_name = ['Early_Adv_pct_1', 'Early_Adv_pct_2','Early_Adv_pct_3','Early_Adv_pct_4','Early_Adv_pct_5']
    mean_list_name = ['Early_Adv_mean_1', 'Early_Adv_mean_2','Early_Adv_mean_3' ]
    for tp in ss_list:
        for key, df_sub in dic_outcomes[tp].iteritems():
            cols = df_sub.columns.tolist()
            cols.remove('var_index_new')
            df2tex(df_sub, '../../model/tables/','{}-{}.tex'.format(key,tp), "%8.2f", 0, cols, ['var_index_new'], cols)
    
    
    
    #======= Application Timing ==========#
    ss_list = ['a1','a2','c1','c2','c3','c4','c5','c6','c7','d1','d2','d3','d4','d5','d6','d7',
               'e1','e2','e3','e4','e5','e6','e7']
    df_outcomes = {}
    for tp in ss_list:
        df_outcomes[tp] = app_date_distribution(df_all_samples[tp])
    
    #======= Export Application Timing ==========#
    ss_list = ['a1','a2','c1','c2','c3','c4','c5','c6','c7','d1','d2','d3','d4','d5','d6','d7',
               'e1','e2','e3','e4','e5','e6','e7']
    for tp in ss_list:
        cols = df_outcomes[tp].columns.tolist()
        cols.remove('stats')
        df2tex(df_outcomes[tp], '../../model/tables/','App_Timing-{}.tex'.format(tp), "%8.2f", 0, cols, ['stats'], cols)
    
    
    
    #======= Eager Schools ==========#
    ss_list = ['a1','a2','c1','c2','c3','c4','c5','c6','c7','d1','d2','d3','d4','d5','d6','d7',
               'e1','e2','e3','e4','e5','e6','e7']
    df_final = {}
    for tp in ss_list:
        df_final[tp] = offer_date_dist(df_all_samples[tp])
    
    #======= Export Eager Schools ==========#
    ss_list = ['a1','a2','c1','c2','c3','c4','c5','c6','c7','d1','d2','d3','d4','d5','d6','d7',
               'e1','e2','e3','e4','e5','e6','e7']
    for tp in ss_list:
        for key, item in df_final[tp].iteritems():
            cols = df_final[tp][key].columns.tolist()
            cols.remove('var')
            df2tex(df_final[tp][key], '../../model/tables/','Eager_Schools_{}-{}.tex'.format(key,tp), "%8.2f", 0, cols, ['var'], cols)
    
    
    
    