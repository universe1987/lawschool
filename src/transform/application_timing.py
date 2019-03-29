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


def app_date_distribution(df_in):    
    # Span (Latest App - Earliest App), SD (All Apps)
    stats_list = ['mean','std','count']
    stats_list_index = ['Mean','SD','Obs']
    
    df_dist = df_in.groupby(['User Name'])['Sent_delta'].agg(['max','min','std']).reset_index()
    df_dist['span'] = df_dist['max'] - df_dist['min'] +1.0
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