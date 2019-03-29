import pandas as pd
import numpy as np
from Registry import Registry
from Application import Application
from School import School
import __future__
import csv
from df2tex import df2tex
from datetime import datetime, timedelta,date


def load_school_char():
    df = pd.read_csv('../../data/raw/school_dates/list_law_schools2.csv')
    df = df[df['Law School'].notnull()]
    
    dic_replace = {'Sep1':'1-Sep','September':'1-Sep','Sep 1':'1-Sep',
                   'Sep 5':'5-Sep','Program Closed':'1-Sep',
                   'Sep 4':'4-Sep','Sep-1':'1-Sep','Oct1':'1-Oct',
                   'Nov-1':'1-Nov','Nov 29':'29-Nov','Oct 15':'15-Oct',
                   'Sep 15':'15-Sep','Oct-15':'15-Oct','Oct 1':'1-Oct'}
    for key,value in dic_replace.iteritems():
        df.loc[df['opening dates']==key,'opening dates']=value
    df.loc[df['opening dates'].isnull(),'opening dates']='1-Sep'
    
    df['opening dates']=pd.to_datetime(df['opening dates'].apply(lambda x: x+'-2018'), errors = 'coerce') 
    df['opening dates baseline'] = pd.to_datetime('1-Sep-2018') 
    df['opening dates delta'] = (df['opening dates'] - df['opening dates baseline']) / np.timedelta64(1,'D')
    print df['opening dates delta'].unique()
    print df['opening dates delta'].value_counts()
    
    df_select = df[['Law School','opening dates delta']]
    df_select.to_csv('../../data/edit/school_char.csv')
    return df_select

if __name__ == '__main__':
    df_select = load_school_char()
    
    
