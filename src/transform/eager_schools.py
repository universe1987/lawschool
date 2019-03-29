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

def date_cutoff(n_cutoff):
    len_interval = 365.0/n_cutoff
    list_interval = []
    var_interval = []
    for i in range(0, n_cutoff+1):
        x = round(len_interval*i)
        y = round(len_interval*(i+1))
        list_interval.append(x)
        var_interval.append('Days {} to {}'.format(int(x),int(y)))
    print list_interval, var_interval
    return list_interval, var_interval

def offer_date_dist(df_in):
    df_outcomes = {}
    df_outcomes_cp = {}
    df_final = {}
    n_cutoff = 15
    stat_list = ['mean','sum']
    outcome_list = ['All','Accepted','Rejected','Waitlisted','Pending']
    outcome_name_list = ['All','Offers','Rejections','Waitlists','Pending']
    
    list_intervals,all_intervals = date_cutoff(n_cutoff)
    df_in['Decision_days'] = df_in['Sent_delta'] + df_in['Decision_delta']
    
    for c in range(0,n_cutoff):
        df_in[all_intervals[c]] = np.nan
        df_in.loc[(df_in['Decision_days']>=list_intervals[c]) & (df_in['Decision_days']<list_intervals[c+1]),
                   all_intervals[c]] = 1.0
        df_in.loc[(df_in['Decision_days']<list_intervals[c]) | (df_in['Decision_days']>=list_intervals[c+1]),
                   all_intervals[c]] = 0.0
    
    df_in['All'] = 1.0
    for c, item in enumerate(outcome_list):
		#print df_in[all_intervals[0:n_cutoff]].head(10)
		df_copy = df_in.copy(deep=True)
		#print df_in[all_intervals[0:n_cutoff]].head(10)
		for x in range(0,n_cutoff):
		    df_copy.loc[df_copy[item]==0.0,all_intervals[x]] = np.nan
		df_outcomes[item] = df_copy[all_intervals[0:n_cutoff]].agg(stat_list).T
		New_Labels = ['{}: Percent'.format(outcome_name_list[c]),'{}: Obs'.format(outcome_name_list[c])]
		df_outcomes[item].columns = New_Labels
		df_outcomes[item]['{}: Percent'.format(outcome_name_list[c])] = df_outcomes[item]['{}: Percent'.format(outcome_name_list[c])]*100.0
		df_outcomes_cp[item] = {}
		for s, stat in enumerate(stat_list):
		    df_outcomes_cp[item][stat] = df_outcomes[item][[New_Labels[s]]]
        
    all_intervals.pop()
    for s, stat in enumerate(stat_list):
        df_final[stat] = df_outcomes_cp['All'][stat].join(df_outcomes_cp['Accepted'][stat]).join(df_outcomes_cp['Rejected'][stat]).join(df_outcomes_cp['Waitlisted'][stat]).join(df_outcomes_cp['Pending'][stat])
        df_final[stat]['var'] = all_intervals
        
    print df_final
    return df_final
