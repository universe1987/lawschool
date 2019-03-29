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