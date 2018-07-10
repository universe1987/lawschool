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
from select_tables import select_application_tables, select_search_tables, select_user_tables, select_user_tables2
from process_merge import process_app_data, process_rank_data, merge_app_rank
import nltk 
from autocorrect import spell
from ngram import NGram
import difflib
import urllib2
from tabula import read_pdf,convert_into
from bs4 import BeautifulSoup

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

def lsac_majors_pdf2json(page_first, page_last, pdf_name):
    for pg in range(page_first,page_last+1):
        pdf = read_pdf('../../data/entry/{}.pdf'.format(pdf_name),pages=pg,output_format='json')
        with open('../../data/edit/{}_page{}.txt'.format(pdf_name,pg), 'w') as outfile:
             json.dump(pdf, outfile,indent=4, sort_keys=True)
    return

def lsac_single_tbl_json2pdf(json_name):
    with open('../../data/edit/{}.txt'.format(json_name)) as f:
        json_data = json.load(f)
    
    list_rows = {}
    df_rows = pd.DataFrame()
    for ix in range(0, len(json_data)):
        for ic,elem_ic in enumerate(json_data[ix]['data']):
            list_rows['{}'.format(ic)] = []
            kk = sum(1 for c in json_data[ix]['data'][ic][0]['text'] if c.isupper())
            if kk > 2:
               list_rows['{}'.format(ic)] = ['']
            for im,elem_im in enumerate(json_data[ix]['data'][ic]):
                list_rows['{}'.format(ic)].append(json_data[ix]['data'][ic][im]['text'])
            ll = len(list_rows['{}'.format(ic)])
            if ll == 8:
                list_rows['{}'.format(ic)].insert(0,'')
                ll = ll + 1
            if ll == 9:
                list_rows['{}'.format(ic)].insert(0,'')
            if len(list_rows['{}'.format(ic)]) == 10:
                df_rows = df_rows.append({'Major Category':list_rows['{}'.format(ic)][0], 'Major':list_rows['{}'.format(ic)][1], 'Percent of Applicants':list_rows['{}'.format(ic)][5]}, ignore_index=True)
    print df_rows
    df_rows.to_csv('../../data/edit/{}_df.csv'.format(json_name))
    return 
    

def lsac_majors_df_cleanup(page_first,page_last):

    with open('lsac_majors_df_cleanup.json') as f:
        json_data = json.load(f)
    
    # Batch processing
    df_big = {}
    for pg in range(page_first,page_last+1):
        df_big['pg{}'.format(pg)] = pd.read_csv('../../data/edit/2015-16_applicants-major_page{}_df.csv'.format(pg))

        df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)].fillna('')
        df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)][(df_big['pg{}'.format(pg)]['Major']!='')| \
                                                              (df_big['pg{}'.format(pg)]['Major Category']!='')| \
                                                              (df_big['pg{}'.format(pg)]['Percent of Applicants']!='')]
        for item in json_data['pg_all']['delete']:
            df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)][df_big['pg{}'.format(pg)][item[0]]!=item[1]]
        
        for index, row in df_big['pg{}'.format(pg)].iterrows():
            if (row['Major']=='') & (row['Major Category']!=''):
                df_big['pg{}'.format(pg)].loc[index+1,'Major Category'] = row['Major Category']
                df_big['pg{}'.format(pg)].loc[index,'Major Category'] = 'Drop'
        df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)][df_big['pg{}'.format(pg)]['Major Category']!='Drop']
        df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)].reset_index()
        
        for index, row in df_big['pg{}'.format(pg)].iterrows():
            if (index>0):
                if (row['Percent of Applicants']!='') & (row['Major']=='') & (df_big['pg{}'.format(pg)].loc[index-1,'Major']!='') :
                    df_big['pg{}'.format(pg)].loc[index-1,'Percent of Applicants'] = row['Percent of Applicants']
                    df_big['pg{}'.format(pg)].loc[index,'Percent of Applicants'] = 'Drop'
        df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)][df_big['pg{}'.format(pg)]['Percent of Applicants']!='Drop']
        df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)].reset_index()
        
        for index, row in df_big['pg{}'.format(pg)].iterrows():
            if (index>0):
                 if (row['Percent of Applicants']!='') & (row['Major']!='') & (row['Major Category']!='') & \
                    (df_big['pg{}'.format(pg)].loc[index-1,'Percent of Applicants'] == '') & \
                    ((df_big['pg{}'.format(pg)].loc[index-1,'Major'] != '') | \
                     (df_big['pg{}'.format(pg)].loc[index-1,'Major Category'] != '')):
                     df_big['pg{}'.format(pg)].loc[index,'Major'] = df_big['pg{}'.format(pg)].loc[index-1,'Major'] +' '+ df_big['pg{}'.format(pg)].loc[index,'Major']
                     df_big['pg{}'.format(pg)].loc[index,'Major Category'] = df_big['pg{}'.format(pg)].loc[index-1,'Major Category'] +' '+ df_big['pg{}'.format(pg)].loc[index,'Major Category']
                     df_big['pg{}'.format(pg)].loc[index-1,'Major'] = 'Drop'
        df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)][df_big['pg{}'.format(pg)]['Major']!='Drop']

        for item in json_data['pg_all']['replace']:
            df_big['pg{}'.format(pg)].loc[df_big['pg{}'.format(pg)][item[0]]==item[1],item[2]]=item[3]
            
        df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)][['Major Category','Major','Percent of Applicants']]        
    
    # Single-file processing        
    for pg in range(page_first,page_last+1):
        for item in json_data['pg{}'.format(pg)]['replace']:
            df_big['pg{}'.format(pg)].loc[df_big['pg{}'.format(pg)][item[0]]==item[1],item[2]]=item[3]
        for item in json_data['pg{}'.format(pg)]['append']:
            df_big['pg{}'.format(pg)]=df_big['pg{}'.format(pg)].append({'Major Category':item[0],'Major':item[1],'Percent of Applicants':item[2]},ignore_index=True)
        for var in ['Major Category','Major','Percent of Applicants']:
            df_big['pg{}'.format(pg)] = df_big['pg{}'.format(pg)][df_big['pg{}'.format(pg)][var]!='']
 
    # Append all these single files
    df_append = pd.DataFrame()
    for pg in range(page_first, page_last+1):
        df_append = df_append.append(df_big['pg{}'.format(pg)],ignore_index=True)
    print 'df_append',df_append
    
    # Sort the pooled files
    df_append['Major Category'] = df_append['Major Category'].str.lstrip()
    for item in json_data['pg_all_conclude']['replace']:
        df_append.loc[df_append[item[0]]==item[1],item[2]]=item[3]
    for var in ['Major','Major Category']:
        df_append[var] = df_append[var].str.lower()
    df_append['Major'] = df_append['Major'].str.split(',').str[0]
    df_append['% Applicants'] = df_append['Percent of Applicants'].str.replace('%','').astype(float)
    print df_append['% Applicants'].sum()
    df_append.to_csv('../../data/edit/major_vs_category_lsac.csv')
    
    df_major_category = df_append.groupby(['Major Category'])['% Applicants'].sum().reset_index()\
                        .sort_values(by=['% Applicants'],ascending=False)
    print df_major_category.head(10)
    df_major_category.to_csv('../../data/edit/df_major_category_percent.csv')
   
    df_major_category_unique = df_append.groupby(['Major Category'])['Major'].unique().reset_index()
    print df_major_category_unique
    json_major_category = {}
    for index, row in df_major_category_unique.iterrows():
        json_major_category[row['Major Category']] = ",".join([str(x) for x in row['Major']])
    
    with open('../../data/edit/major_category_composition.json', 'w') as outfile:
        json.dump(json_major_category, outfile,indent=4)
    return

def lsac_majors():
    #lsac_majors_pdf2json(2,16,'2015-16_applicants-major')
    
    page_first = 2
    page_last = 16
    
    for pg in range(page_first,page_last+1):
        print '====== page', pg
        #lsac_single_tbl_json2pdf('2015-16_applicants-major_page{}'.format(pg))
    
    lsac_majors_df_cleanup(page_first,page_last)
    return

def breakdown_majors():
    df_details = pd.read_csv('../../data/edit/df_details_race_college_cleaned.csv')
    df_details = df_details.fillna('')
    print df_details['User Name'].nunique(),len(df_details)
    
    for item in [ 'additional info' ,'extra curricular' ]:
        df_details[item] = df_details['Major'].apply(lambda x: keep_ascii(x))
    
    df_details['Major'] = df_details['Major'].str.replace("  "," ").str.replace("   "," ")
    df_details['Major'] = df_details['Major'].apply(lambda x: ''.join([i if (ord(i)==32)|(ord(i)==39)|(64 < ord(i) < 91)|(96<ord(i)<123) else "$" for i in x]))
    df_details['Major'] = df_details['Major'].str.lower().str.replace('and',"$")
    
    df_details['Major list'] = df_details['Major'].str.split("$").apply(lambda x:filter(None,x))
    df_details['Major list len'] = df_details['Major list'].apply(lambda x: len(x))
    len_m = df_details['Major list len'].max()
    print len_m
    
    for ix in range(1,len_m+1):
        df_details['Major element {}'.format(ix)] = ''
    print df_details.columns.tolist()
    
    for index, row in df_details.iterrows():
        if row['Major list len']>0:
            for ix in range(1, row['Major list len']+1):
                df_details.loc[index,'Major element {}'.format(ix)] = row['Major list'][ix-1]
    for ix in range(1,len_m+1):
        df_details['Major element {}'.format(ix)] = df_details['Major element {}'.format(ix)].str.lstrip().str.rstrip()
    df_details = df_details.fillna('')
    print df_details.columns.tolist()
    
    df_details.to_csv('../../data/edit/df_details_major_elements_broken_down.csv')
    
    # Generate a list of unique values
    list_major = []
    for index, row in df_details.iterrows():
        for ix in range(1,row['Major list len']+1):
            list_major.append(row['Major element {}'.format(ix)])
    
    df = pd.DataFrame(list_major,columns=['Major element'])
    list_major_elements = df['Major element'].unique()
    df_major_elements_unique = pd.DataFrame(list_major_elements,columns=['Major element'])
    print df['Major element'].nunique(),len(df_major_elements_unique)
    
    df_major_elements_unique.to_csv('../../data/edit/df_major_elements_unique.csv')    
    return
    
def merge_majors_lsac_lsn():
    df_lsn = pd.read_csv('../../data/edit/df_major_elements_unique.csv')
    df_lsn = df_lsn.fillna('')
    df_lsn['major guess'] = ''
    
    with open('../../data/edit/major_category_composition.json', 'rb') as infile:
        json_lsac = json.load(infile)
    
    list_lsac = []
    for keys, values in json_lsac.iteritems():
        list_lsac.extend(json_lsac[keys].split(','))
    
    threshold = 0.9
    for index, row in df_lsn.iterrows():
        best_match_lsac = difflib.get_close_matches(row['Major element'],list_lsac,cutoff=threshold)
        #df_lsn.loc[index,'major_guess'] = ";".join([str(x) for x in best_match_lsac])
        if len(best_match_lsac) > 0:
            df_lsn.loc[index,'major guess'] = best_match_lsac[0]
    print len(df_lsn), len(df_lsn[df_lsn['major guess']!=''])
    
    df_lsn.to_csv('../../data/edit/df_major_guess_lsn.csv')
    df_lsn_matched = df_lsn[df_lsn['major guess']!='']
    df_lsn_matched.to_csv('../../data/edit/df_major_guess_lsn_matched.csv')
    
    # The list of majors is divided into two parts: df_lsn_matched, df_tallal
    # I use lsac_pdf to assign a major category to the df_lsn_matched
    # I ask tallal to manually assign a major category to the df_tallal
    # Lastly, I am going to merge these back to the df_details through major_clean_binder()
    return
    
def tallal_majors_lsac_lsn():
    # Ask tallal to determine the unmatched major category manually
    df_tallal = pd.read_csv('../../data/edit/df_major_guess_lsn.csv')
    df_tallal = df_tallal.fillna('')
    df_tallal = df_tallal[df_tallal['major guess']=='']
    
    list_major_category = ['social sciences','arts & humanities','business & management',
                           'natural sciences','engineering','health professions','other']
    for var in list_major_category:
        df_tallal[var] = ''
    df_tallal = df_tallal[['Major element','major guess']+list_major_category]
    df_tallal = df_tallal.reset_index(drop=True)
    
    df_tallal.loc[df_tallal['Major element']=='poli sci','major guess'] = 'political science'
    df_tallal.loc[df_tallal['Major element']=='poli sci','social sciences'] = '1'

    df_tallal.loc[df_tallal['Major element']=='psych','major guess'] = 'psychology'
    df_tallal.loc[df_tallal['Major element']=='psych','social sciences'] = '1'
   
    df_tallal.loc[df_tallal['Major element']=='math','major guess'] = 'mathematics'
    df_tallal.loc[df_tallal['Major element']=='math','natural sciences'] = '1'    
    
    df_tallal.to_csv('../../data/edit/tallal_major_classification.csv')
    return
    
def major_clean_binder():

    # Get rid of redundant rows in data scraped out of PDF
    df_major_vs_category_lsac = pd.read_csv('../../data/edit/major_vs_category_lsac.csv')
    df_major_vs_category_lsac = df_major_vs_category_lsac[['Major','Major Category','% Applicants']]
    print len(df_major_vs_category_lsac), df_major_vs_category_lsac['Major'].nunique()
    print df_major_vs_category_lsac['Major'].value_counts()
    list_redundant = ['physics','any area not listed - other','biology','physical therapy']
    print df_major_vs_category_lsac.loc[df_major_vs_category_lsac['Major'].isin(list_redundant)]
    list_redundant2 = [0.02,1.34,0.53,0.02]
    for index, item in enumerate(list_redundant):
        df_major_vs_category_lsac = df_major_vs_category_lsac.drop(df_major_vs_category_lsac[(df_major_vs_category_lsac['Major'] == list_redundant[index]) & (df_major_vs_category_lsac['% Applicants'] == list_redundant2[index])].index)
    print df_major_vs_category_lsac['Major'].value_counts()

    
    # merge machine_guessed_majors to pdf
    df_lsn_matched = pd.read_csv('../../data/edit/df_major_guess_lsn_matched.csv')
    df_part1 = df_lsn_matched.merge(df_major_vs_category_lsac, left_on='major guess',right_on='Major',how='left').reset_index()
    
    # reshape
    list_major_category = ['social sciences','arts & humanities','business & management',
                           'natural sciences','engineering','health professions','other']
    for var in list_major_category:
        df_part1[var] = ''
    for index, row in df_part1.iterrows():
        for var in list_major_category:
            if row['Major Category'] == var:
                df_part1.loc[index,var] = 1
    
    # merge tallal_guessed_majors to pdf
    df_part1 = df_part1[['Major element','major guess']+list_major_category]
    df_part2 = pd.read_csv('../../data/entry/tallal_major_classification_revised_myself.csv')
    df_part2 = df_part2[['Major element','major guess']+list_major_category]
    
    df_both = df_part1.append(df_part2)
    print df_both['Major element'].nunique(),df_part1['Major element'].nunique(),df_part2['Major element'].nunique()
    df_both.to_csv('../../data/edit/df_both.csv')
    
    # merge back to the main user data
    df_details = pd.read_csv('../../data/edit/df_details_major_elements_broken_down.csv')
    print df_details.columns.tolist()
    df_details = df_details.drop(['Unnamed: 0', 'Unnamed: 0.1'],axis=1)
    print df_details['User Name'].nunique(), len(df_details)

    len_m = 6
    df = df_details
    for ix in range(1,len_m+1):
        df = df.merge(df_both,left_on='Major element {}'.format(ix),right_on='Major element',how='left').reset_index(drop=True)
        for item in list_major_category:
            df['{} {}'.format(item,ix)] = df['{}'.format(item)].fillna('').astype(str)
        df = df.drop(list_major_category+['major guess','Major element'],axis=1)    
    df.to_csv('../../data/edit/df_major_elements.csv')
    print df['User Name'].nunique(), len(df)
    
    # reshape the main user data
    for item in list_major_category:
        df['{}'.format(item)] = df[['{} 1'.format(item),'{} 2'.format(item),'{} 3'.format(item),
                                    '{} 4'.format(item),'{} 5'.format(item),'{} 6'.format(item)]].max(axis=1)
        for ix in range(1,len_m+1):
            df = df.drop(['{} {}'.format(item, ix)],axis=1)
    df.to_csv('../../data/edit/df_details_race_college_major_cleaned.csv')
    return