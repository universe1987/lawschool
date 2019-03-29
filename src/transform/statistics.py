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
    
def summary_statistics_by_schools(df):
    f = lambda x: mode(x, axis=None)[0]
    print df.columns.tolist()
    df['days to issue'] = df['Sent_delta'] + df['Decision_delta']
    df_schl = df[df['Law top 15-50']==1].groupby(['Law School'])['days to issue'].apply(f) #[df['Law top 15-50']==1]
    df_schl.to_csv('../../data/edit/school_mode.csv')
    
    list_law_rank = ['Law unranked','Law top 14','Law top 15-50','Law below 51']
    for law_rank in list_law_rank:
        df_school = df[df['{}'.format(law_rank)]==1].groupby('Sent_delta')['LSAT','GPA'].mean().reset_index()
        print df_school.columns.tolist()
        print df_school.head(7)
        df_school.plot(x='Sent_delta',y='LSAT',kind='scatter')
        plt.savefig('../../data/edit/try_{}_LSAT.png'.format(law_rank))
        print df_school['GPA'].describe()
        df_school.plot(x='Sent_delta',y='GPA',kind='scatter')
        plt.savefig('../../data/edit/try_{}_GPA.png'.format(law_rank))
    # Conclusion: all worse off over time!
    return

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

if __name__ == '__main__':
    df_in = pd.read_csv('../../data/edit/df_all_samples_a2.csv')
    summary_statistics_by_schools(df_in)