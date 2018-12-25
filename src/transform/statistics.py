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

def summary_statistics_schools(df):
    dic_detail_1 = {}
    dic_detail_2 = {}
    dic_detail_3 = {}
    
    action_list = ['unranked','unranked_2010']
    name_list = ['Not Ranked','Not Ranked in 2010']
    for index, act in enumerate(action_list):
        dic_detail_1['{}'.format(name_list[index])]=pd.DataFrame(df[['{}'.format(act)]].agg(['mean','count']))
    
    action_list = ['rank_cross','rank_2010_cp'] 
    name_list = ['Rank','Rank in 2010'] 
    for index, act in enumerate(action_list):
        dic_detail_2['{}'.format(name_list[index])]=pd.DataFrame(df[['{}'.format(act)]].agg(['mean','std','count']))
    
    df['Sent_c'] = 1.0*(df['Sent_delta']>=0.0)   
    action_list = ['Sent_c','Accepted','Rejected','Pending','Waitlisted']
    name_list = ['Applications','Offers','Rejections','Pending','Waitlists'] #,'Number of Grants'
    for index, act in enumerate(action_list):
        df_act = df.groupby(['Law School'])['{}'.format(act)].sum().reset_index()
        dic_detail_3['\# {} Per School'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
        
        
    '''
    df_school = df.groupby(['Law School'])['User Name'].count().reset_index()
    dic_detail['\# Law Schools'] = pd.DataFrame(df_school['Law School'].agg(['nunique']))
    dic_detail['\# Law Schools with Over 100 Apps in Data'] = pd.DataFrame(df_school.loc[df_school['User Name']>=100,'Law School'].agg(['nunique']))
    '''
    
    return dic_detail_1,dic_detail_2,dic_detail_3

def summary_statistics_applicants(df):
    # [mean, sd, 75, 25, count]
    # app dates, # sent, # offer, # rejects, # waiting list, # pending, # decision dates
    # personal characteristics: GPA, LSAT
	dic_detail_1 = {}
	dic_detail_2 = {}
	dic_detail_3 = {}
	dic_detail_4 = {}
	dic_detail_5 = {}
	dic_detail_6 = {}
	dic_detail_1['When to Apply (\# Days since Sep 1)']=pd.DataFrame(df['Sent_delta'].agg(['mean','std','count']))
	#print dic_detail['Time to Apply (Days since Sep 1)'].iloc[:,0]
	dic_detail_1['When to Hear Back (\# Days since sent)']=pd.DataFrame(df[['Decision_delta']].agg(['mean','std','count']))
	
	action_list = ['Sent'] #,'grant yes'
	name_list = ['Applications'] #,'Number of Grants'
	for index, act in enumerate(action_list):
		df_act = df.groupby(['User Name'])['{}'.format(act)].count().reset_index()
		dic_detail_1['\# {} Per Capita'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
	
	action_list = ['Accepted','Rejected','Pending','Waitlisted'] #,'grant yes'
	name_list = ['Offers','Rejections','Pending','Waitlists'] #,'Number of Grants'
	for index, act in enumerate(action_list):
		df_act = df.groupby(['User Name'])['{}'.format(act)].sum().reset_index()
		dic_detail_1['\# {} Per Capita'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))

	action_list = ['GPA','LSAT'] 
	name_list = ['GPA','LSAT'] 
	for index, act in enumerate(action_list):
		df_act = df.groupby(['User Name'])['{}'.format(act)].max().reset_index()
		dic_detail_1['{}'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
	
	action_list = ['Gender','white', 'asian and pacific islander', 'african', 
	               'Mixed, probably not urm', 'hispanic', 'mexican', 
	               'puerto rican', 'Native American or alaskan']
	name_list = ['Male','White', 'Asian', 'African (URM)', 
                 'Mixed', 'Hispanic', 'Mexican (URM)', 
                 'Puerto Rican (URM)', 'Native American or Alaskan (URM)']
	for index, act in enumerate(action_list):
		df_act = df.groupby(['User Name'])['{}'.format(act)].max().multiply(100.0).reset_index()
		dic_detail_2['{}'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','count']))
	
	action_list = ['social sciences', 'arts & humanities', 'business & management', 'natural sciences', 'engineering', 'health professions','other']
	name_list = ['Social Sciences', 'Arts \& Humanities', 'Business \& Management', 'Natural Sciences', 'Engineering', 'Health Professions','Other']
	for index, act in enumerate(action_list):
		df_act = df.groupby(['User Name'])['{}'.format(act)].max().multiply(100.0).reset_index()
		dic_detail_3['{}'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','count']))
	
	action_list = ['Ranked Nationally','Ranked Regionally','Described Positively','Described Negatively','Described Neutrally']
	name_list = action_list
	for index, act in enumerate(action_list):
		df_act = df.groupby(['User Name'])['{}'.format(act)].max().multiply(100.0).reset_index()
		dic_detail_4['{}'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','count']))
	
	action_list = ['1-2 Years', '3-4 Years', 'In Undergrad', '5-9 Years', '10+ Years']
	name_list = action_list
	for index, act in enumerate(action_list):
	    df[act] = pd.to_numeric(df[act], errors='coerce')
	    df_act = df.groupby(['User Name'])['{}'.format(act)].max().multiply(100.0).reset_index()
	    dic_detail_5['{}'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','count']))
	
	action_list = ['EC at all','Athletic/Varsity', 'Community/Volunteer', 'Greek', 'Leadership', 
                   'Legal Work Experience', 'Military','Non-legal Internship', 'Legal Internship',
                   'Non-legal Work Experience', 'Overseas', 'Strong Letters', 'Student Societies']
	
	name_list = ['Listing some EC at least','Sports','Community Service','Greek Society','Leadership',
                 'Legal Work Experience', 'Military','Non-legal Internship', 'Legal Internship',
                 'Non-legal Work Experience', 'Overseas', 'Strong Letters', 'Non-Greek Student Societies']
	for index, act in enumerate(action_list):
	    df[act] = pd.to_numeric(df[act], errors='coerce')
	    df_act = df.groupby(['User Name'])['{}'.format(act)].max().multiply(100.0).reset_index()
	    dic_detail_6['{}'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','count']))
    
    
	'''
	action_list = ['grant']
	name_list = ['Size of Grants']
	for index, act in enumerate(action_list):
		df_act = df.groupby(['User Name'])['{}'.format(act)].mean().reset_index()
		dic_detail['{} Per Capita'.format(name_list[index])]=pd.DataFrame(df_act[['{}'.format(act)]].agg(['mean','std','count']))
	'''
	return dic_detail_1,dic_detail_2,dic_detail_3,dic_detail_4,dic_detail_5,dic_detail_6
	# Need to include law school ranks as well

''' # derelict codes
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
        print 'year=',yr,dic_detail[yr-2003]
    return dic_count, dic_detail
'''    
