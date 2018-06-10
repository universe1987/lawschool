import re
import csv
import json
import urllib
from datetime import datetime, timedelta,date
import numpy as np
import pandas as pd
from glob import glob
from collections import defaultdict

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii

def keep_ascii_file(file1, file2):
    f2 = open(file2, 'w') 
    with open(file1, 'rb') as f1:
        for row in f1.read().split('\n'):
            row = keep_ascii(row)
            f2.write(row+'\n') 
        f2.close()


def filter_good_applicants(df, col, threshold):
    return df[df[col] > threshold]
    
def get_stats(group):
    return {'Mean': group.mean(),'SD':group.std()} #, ,'count': group.count()}
