import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict, Counter
from utils import keep_ascii_file, filter_good_applicants, get_stats
from extract.utils import remove_special_char,keep_ascii
import difflib
import urllib2

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch


#pdfminer 
#pypdf2
#tabula/tabulapdf

def learn_numerical():
    df_details = pd.read_csv('../../data/edit/df_details_race_college_major_cleaned.csv')
    df_details = df_details.fillna('')
    print df_details['User Name'].nunique(),len(df_details)
    print df_details.columns.tolist()
    for var in ['Gender','Years out of Undergrad']:
        print df_details[var].unique()
    df_details = df_details.drop(['Unnamed: 0'],axis=1)
    df_details.to_csv('../../data/edit/df_details_race_college_major_numeric_cleaned.csv')
    return

