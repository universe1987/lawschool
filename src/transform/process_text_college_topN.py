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
#nltk.download('words')
from autocorrect import spell
from ngram import NGram
import difflib
import urllib2
from bs4 import BeautifulSoup

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch

def fill_topN_merge_lac():
    # manually clean edit/df_merge_lac.csv so the existing match based on location is reasonable
    # save it into entry/df_merge_lac_marked.csv
    df = pd.read_csv('../../data/entry/df_merge_lac_marked.csv')
    df_filled = df[df['State_acronym'].notnull()] 
    print len(df_filled['College Name or Type'])
    
    df_unfilled = df[df['State_acronym'].isnull()]
    print len(df_unfilled['College Name or Type'])
    
    df_unfilled = df_unfilled.fillna('')

    with open('fill_topN_merge_lac.json', 'rb') as file:
        topN_groups = json.load(file)
    
    for index, row in df_unfilled.iterrows():
        if any(row['College Name or Type']==x for x in topN_groups["ivy"]):
            df_unfilled.loc[index,'name'] = 'dartmouth college'
        if any(row['College Name or Type']==x for x in topN_groups["top5"]):
            if ("1" in row['College Name or Type'])|("2" in row['College Name or Type']):
                df_unfilled.loc[index,'name'] = 'amherst college'
            else:
                df_unfilled.loc[index,'name'] = 'swarthmore college'
        if any(row['College Name or Type']==x for x in topN_groups["top10"]):
            if 'hellacious' in row['College Name or Type']:
                df_unfilled.loc[index,'name'] = 'georgia institute of technology'
            else:
                df_unfilled.loc[index,'name'] = 'pomona college'
        if any(row['College Name or Type']==x for x in topN_groups["top20"]):
            df_unfilled.loc[index,'name'] = 'hamilton college'
        if any(row['College Name or Type']==x for x in topN_groups["top30"]):
            df_unfilled.loc[index,'name'] = 'macalester college'
        if any(row['College Name or Type']==x for x in topN_groups["top40"]):
            df_unfilled.loc[index,'name'] = 'lafayette college'
        if any(row['College Name or Type']==x for x in topN_groups["top50"]):
            df_unfilled.loc[index,'name'] = 'connecticut college'
        if any(row['College Name or Type']==x for x in topN_groups["top75"]):
            df_unfilled.loc[index,'name'] = 'wabash college'
        if any(row['College Name or Type']==x for x in topN_groups["top100"]):
            df_unfilled.loc[index,'name'] = 'allegheny college'
            
    print len(df_unfilled[df_unfilled['name']==''])
    df = df_unfilled[df_unfilled['name']=='']
    print df['College Name or Type'].nunique()
    print df['College Name or Type'].unique()
    df_unfilled[df_unfilled['name']==''].to_csv('../../data/edit/df_topN_lac_unfilled.csv')
    df_combined = df_filled.append(df_unfilled,ignore_index=True)
    df_combined = df_combined.sort_values(by=['id'])
    df_combined.to_csv('../../data/edit/df_topN_lac_combined.csv')
    return


def fill_topN_merge_univ():
    # manually clean edit/df_merge_univ.csv so the existing match based on location is reasonable
    # save it into entry/df_merge_univ_marked.csv
    df = pd.read_csv('../../data/entry/df_merge_univ_marked.csv')
    df_filled = df[df['State_acronym'].notnull()] 
    print len(df_filled['College Name or Type'])
    
    df_unfilled = df[df['State_acronym'].isnull()]
    print len(df_unfilled['College Name or Type'])
    
    df_unfilled = df_unfilled.fillna('')

    with open('fill_topN_merge_univ.json', 'rb') as file:
        topN_groups = json.load(file)
    
    for index, row in df_unfilled.iterrows():
        if any(row['College Name or Type']==x for x in topN_groups["ivy"]):
            #print row['College Name or Type'],'|',row['State'],'|',row['City']
            if (row['State'] == 'pennsylvania') | (row['City'] == 'philadelphia'):
                df_unfilled.loc[index,'name'] = 'university of pennsylvania'
            elif (row['State'] == 'massachusetts') | (row['City'] == 'boston') | (row['College Name or Type']=='best ivy'):
                df_unfilled.loc[index,'name'] = 'harvard university'
            elif (row['State'] == 'connecticut') | (row['City'] == 'new haven') | (row['College Name or Type']=='top 3 ivy'):
                df_unfilled.loc[index,'name'] = 'yale university'
            elif (row['State'] == 'new jersey') | (row['City'] == 'princeton')| (row['College Name or Type']=='ivy ( hyp)'):
                df_unfilled.loc[index,'name'] = 'princeton university' 
            elif (row['State'] == 'rhode island') | (row['City'] == 'providence'):
                df_unfilled.loc[index,'name'] = 'brown university'
            elif (row['State'] == 'new hampshire'):
                df_unfilled.loc[index,'name'] = 'dartmouth college'
            elif ('ithaca' in row['City']):
                df_unfilled.loc[index,'name'] = 'cornell university'
            else:
                df_unfilled.loc[index,'name'] = 'columbia university'
        elif any(row['College Name or Type']==x for x in topN_groups["top10"]):
            if (row['State'] == 'pennsylvania') | (row['City'] == 'philadelphia'):
                df_unfilled.loc[index,'name'] = 'university of pennsylvania'
            elif (row['State'] == 'massachusetts') | (row['City'] == 'boston')\
                 | (row['City'] == 'cambridge'):
                df_unfilled.loc[index,'name'] = 'harvard university'
            elif (row['State'] == 'connecticut') | (row['City'] == 'new haven') | ('3' in row['College Name or Type'])\
                 | ('2' in row['College Name or Type']):
                df_unfilled.loc[index,'name'] = 'yale university'
            elif (row['State'] == 'new jersey') | (row['City'] == 'princeton'):
                df_unfilled.loc[index,'name'] = 'princeton university' 
            elif (row['State'] == 'rhode island') | (row['City'] == 'providence'):
                df_unfilled.loc[index,'name'] = 'brown university'
            elif (row['State'] == 'new hampshire'):
                df_unfilled.loc[index,'name'] = 'dartmouth college'
            elif ('ithaca' in row['City']):
                df_unfilled.loc[index,'name'] = 'cornell university'
            elif (row['State'] == 'illinois')|(row['City']=='chicago'):
                df_unfilled.loc[index,'name'] = 'university of chicago'
            elif (row['State'] == 'california')|(row['City']=='stanford'):
                df_unfilled.loc[index,'name'] = 'stanford university'
            elif (row['State'] == 'north carolina')|(row['City']=='durham')|('non ivy' in row['College Name or Type'])\
                 | ('non-ivy' in row['College Name or Type']):
                df_unfilled.loc[index,'name'] = 'duke university'
            elif (row['State'] == 'missourri') | (row['City'] == 'st louis'):
                df_unfilled.loc[index,'name'] = 'washington university in st. louis'
            else:
                df_unfilled.loc[index,'name'] = 'columbia university'
        elif any(row['College Name or Type']==x for x in topN_groups["top20"]):
            if (row['State'] == 'maryland') | (row['City'] == 'baltimore'):
                df_unfilled.loc[index,'name'] = 'johns hopkins university'
            elif (row['State'] == 'illinois') | (row['City'] == 'chicago') | (row['City']=='evanston'):
                df_unfilled.loc[index,'name'] = 'northwestern university'    
            elif (row['State'] == 'rhode island') | (row['City'] == 'providence'):
                df_unfilled.loc[index,'name'] = 'brown university'
            elif (row['State'] == 'new hampshire'):
                df_unfilled.loc[index,'name'] = 'dartmouth college' 
            elif ('ithaca' in row['City']):
                df_unfilled.loc[index,'name'] = 'cornell university' 
            elif (row['State'] == 'texas') | (row['City'] == 'houston'):
                df_unfilled.loc[index,'name'] = 'rice university'    
            elif (row['State'] == 'tennessee') | (row['City'] == 'nashville'):
                df_unfilled.loc[index,'name'] = 'vanderbilt university'  
            elif (row['State'] == 'indiana') | (row['City'] == 'notre dame'):
                df_unfilled.loc[index,'name'] = 'university of notre dame' 
            elif (row['State'] == 'missourri') | (row['City'] == 'st louis'):
                df_unfilled.loc[index,'name'] = 'washington university in st. louis' 
            elif (row['State'] == 'dc') | (row['City'] == 'dc'):
                df_unfilled.loc[index,'name'] = 'georgetown university'
            elif (row['State'] == 'georgia') | (row['City'] == 'atlanta'):
                df_unfilled.loc[index,'name'] = 'emory university' 
            elif (row['State'] == 'california') | (row['City'] == 'berkeley'):
                df_unfilled.loc[index,'name'] = 'university of california berkeley'   
            elif (row['City'] == 'los angeles'):
                df_unfilled.loc[index,'name'] = 'university of california los angeles'  
            elif (row['State'] == 'pennsylvania') | (row['City'] == 'pittsburgh'):
                df_unfilled.loc[index,'name'] = 'carnegie mellon university'      
            elif (row['State'] == 'virginia') | (row['City'] == 'charlottesville'):
                df_unfilled.loc[index,'name'] = 'university of virginia'
            else:
                df_unfilled.loc[index,'name'] = 'vanderbilt university'                                          
        elif any(row['College Name or Type']==x for x in topN_groups["top30"]):
            if (row['State'] == 'california') | (row['City'] == 'los angeles'):
                df_unfilled.loc[index,'name'] = 'university of california los angeles'                 
            elif (row['State'] == 'pennsylvania') | (row['City'] == 'pittsburgh'):
                df_unfilled.loc[index,'name'] = 'carnegie mellon university' 
            elif ('winston' in row['City']):
                df_unfilled.loc[index,'name'] = 'wake forest university'   
            elif (row['State'] == 'michigan') | (row['City'] == 'ann arbor'):
                df_unfilled.loc[index,'name'] = 'university of michigan ann arbor'  
            elif (row['State'] == 'massachusetts') | (row['City'] == 'medford'):
                df_unfilled.loc[index,'name'] = 'tufts university'
            elif (row['State'] == 'new york') | (row['City'] == 'new york'):
                df_unfilled.loc[index,'name'] = 'new york university'          
            elif (row['State'] == 'north carolina') | (row['City'] == 'chapel hill'):
                df_unfilled.loc[index,'name'] = 'university of north carolina chapel hill'
            elif (row['State'] == 'virginia') | (row['City'] == 'williamsburg'):
                df_unfilled.loc[index,'name'] = 'college of william and mary'
            elif (row['State'] == 'massachusetts') | (row['City'] == 'waltham'):
                df_unfilled.loc[index,'name'] = 'brandeis university'
            elif (row['State'] == 'georgia') | (row['City'] == 'atlanta'):
                df_unfilled.loc[index,'name'] = 'georgia institute of technology'
            elif (row['State'] == 'new york') | (row['City'] == 'rochester'):
                df_unfilled.loc[index,'name'] = 'university of rochester'
            elif (row['State'] == 'massachusetts') | (row['City'] == 'boston'):
                df_unfilled.loc[index,'name'] = 'boston university'    
            else:    
                df_unfilled.loc[index,'name'] = 'carnegie mellon university' 
        elif any(row['College Name or Type']==x for x in topN_groups["top40"]):
            if 'georgia' in row['State']:
                df_unfilled.loc[index,'name'] = 'georgia institute of technology'
            elif 'new york' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of rochester'
            elif 'california' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of california san diego'
            elif 'illinois' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of illinois urbana champaign'
            elif 'ohio' in row['State']:
                df_unfilled.loc[index,'name'] = 'case western reserve university'
            elif 'massachusetts' in row['State']:
                df_unfilled.loc[index,'name'] = 'boston university'
            elif 'florida' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of miami'
            elif 'penn' in row['State']:
                df_unfilled.loc[index,'name'] = 'lehigh university'
            else:
                df_unfilled.loc[index,'name'] = 'university of california san diego' 
        elif any(row['College Name or Type']==x for x in topN_groups["top50"]):
            df_unfilled.loc[index,'name'] = 'pennsylvania state university university park' 
        elif any(row['College Name or Type']==x for x in topN_groups["top75"]):
            df_unfilled.loc[index,'name'] = 'university of pittsburgh' 
        elif any(row['College Name or Type']==x for x in topN_groups["top100"]):
            df_unfilled.loc[index,'name'] = 'university of colorado boulder' 
        elif any(row['College Name or Type']==x for x in topN_groups["top_nation_public_20"]):
            if 'california' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of california berkeley'
            elif 'texas' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of texas austin'
            elif 'south carolina' in row['State']:
                df_unfilled.loc[index,'name'] = 'clemson university'
            else:
                df_unfilled.loc[index,'name'] = 'university of california berkeley' 
        elif any(row['College Name or Type']==x for x in topN_groups["top_nation_public_30"]):
            if 'state college' in row['City']:
                df_unfilled.loc[index,'name'] = 'pennsylvania state university university park'
            elif 'illinois' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of illinois urbana champaign'
            else:
                df_unfilled.loc[index,'name'] = 'university of california santa barbara'
        elif any(row['College Name or Type']==x for x in topN_groups["top_nation_public_40"]):
            if 'california' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of california irvine'
            elif 'cincinnati' in row['City']:
                df_unfilled.loc[index,'name'] = 'university of cincinnati'
            elif 'indiana' in row['State']:
                df_unfilled.loc[index,'name'] = 'indiana university bloomington'
            else:
                df_unfilled.loc[index,'name'] = 'university of delaware' 
        elif any(row['College Name or Type']==x for x in topN_groups["top_nation_public_50"]):
            df_unfilled.loc[index,'name'] = 'university of alabama' 
        elif any(row['College Name or Type']==x for x in topN_groups["top_nation_public_100"]):
            df_unfilled.loc[index,'name'] = 'north carolina state university raleigh' 
        elif any(row['College Name or Type']==x for x in topN_groups["top_public_5"]):
            if 'california' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of california los angeles'
            elif 'north carolina' in row['City']:
                df_unfilled.loc[index,'name'] = 'university of north carolina chapel hill'
            elif 'michigan' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of michigan ann arbor'
            else:
                df_unfilled.loc[index,'name'] = 'university of virginia'
        elif any(row['College Name or Type']==x for x in topN_groups["top_public_10"]):
            if 'california' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of california san diego'
            elif 'michigan' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of michigan ann arbor'
            elif 'florida'  in row['State']:
                df_unfilled.loc[index,'name'] = 'university of florida'
            elif 'wisconsin' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of wisconsin madison'
            else:
                df_unfilled.loc[index,'name'] = 'georgia institute of technology'
        elif any(row['College Name or Type']==x for x in topN_groups["top_public_20"]):
            if 'california' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of california davis'
            elif 'pennsylvania' in row['State']:
                df_unfilled.loc[index,'name'] = 'pennsylvania state university university park'
            elif 'georgia'  in row['State']:
                df_unfilled.loc[index,'name'] = 'university of georgia'
            elif 'texas' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of texas austin'
            elif 'maryland' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of maryland college park'
            elif 'south carolina' in row['State']:
                df_unfilled.loc[index,'name'] = 'clemson university'
            else:
                df_unfilled.loc[index,'name'] = 'ohio state university columbus'
        elif any(row['College Name or Type']==x for x in topN_groups["top_public_30"]):
            if 'charlottesville' in row['City']:
                df_unfilled.loc[index,'name'] = 'university of virginia'
            elif 'tempe' in row['City']:
                df_unfilled.loc[index,'name'] = 'arizona state university tempe'
            elif 'san diego' in row['City']:
                df_unfilled.loc[index,'name'] = 'university of california san diego'
            elif 'wisconsin' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of wisconsin madison'
            else:
                df_unfilled.loc[index,'name'] = 'rutgers university new brunswick'
        elif any(row['College Name or Type']==x for x in topN_groups["top_public_40"]):
            df_unfilled.loc[index,'name'] = 'university of california santa cruz'
        elif any(row['College Name or Type']==x for x in topN_groups["top_public_50"]):
            if 'arizona' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of arizona'
            elif 'alabama' in row['State']:
                df_unfilled.loc[index,'name'] = 'university of alabama'
            else:
                df_unfilled.loc[index,'name'] = 'temple university'
        elif any(row['College Name or Type']==x for x in topN_groups["top_public_100"]):
            df_unfilled.loc[index,'name'] = 'university at albany suny'
        elif any(row['College Name or Type']==x for x in topN_groups["top_regional"]):
            if row['College Name or Type'] == 'top 10 state school':
                df_unfilled.loc[index,'name'] = 'university of florida'
            elif row['College Name or Type'] == 'top 20 state school':
                df_unfilled.loc[index,'name'] = 'university of minnesota twin cities'
            elif row['College Name or Type'] == 't5  state':
                df_unfilled.loc[index,'name'] = 'university of virginia'
            elif row['College Name or Type'] == '#1 regional':
                df_unfilled.loc[index,'name'] = 'elon university'
            elif row['College Name or Type'] == 'top 10 regional ne':
                df_unfilled.loc[index,'name'] = "st. joseph's university"
            elif row['College Name or Type'] == 'top 10 midwest regional univer':
                df_unfilled.loc[index,'name'] = 'bethel university'
            elif row['College Name or Type'] == 'top 5 regional':
                df_unfilled.loc[index,'name'] = 'chapman university'
            elif row['College Name or Type'] == 't50 regional':
                df_unfilled.loc[index,'name'] = 'niagara university'
            elif row['College Name or Type'] == 'top 50 regional':
                df_unfilled.loc[index,'name'] = 'niagara university'
            elif row['College Name or Type'] == 'top 15 regional':
                df_unfilled.loc[index,'name'] = 'rockhurst university'
            elif row['College Name or Type'] == '#1 regional small pr':
                df_unfilled.loc[index,'name'] = 'elon university'
            elif row['College Name or Type'] == 'private - top 10 regional':
                df_unfilled.loc[index,'name'] = 'marist college'
            elif row['College Name or Type'] == 'top 10 regional - midwest - pr':
                df_unfilled.loc[index,'name'] = 'drake university'
            elif row['College Name or Type'] == '#1 regional private':
                df_unfilled.loc[index,'name'] = 'creighton university'
            elif row['College Name or Type'] == 'top 3 regional college':
                df_unfilled.loc[index,'name'] = 'drake university'
            elif row['College Name or Type'] == 't10 regional':
                df_unfilled.loc[index,'name'] = 'north central college'
            elif row['College Name or Type'] == 'top  20 regional':
                df_unfilled.loc[index,'name'] = 'cuny baruch college'
        elif any(row['College Name or Type']==x for x in topN_groups["top10_lac"]):
            if "penn" in row['State']:
                df_unfilled.loc[index,'name'] = 'swarthmore college'
            elif "amherst" in row['City']:
                df_unfilled.loc[index,'name'] = 'amherst college'
            else:
                df_unfilled.loc[index,'name'] = 'middlebury college'
        elif any(row['College Name or Type']==x for x in topN_groups["top20_lac"]):
            df_unfilled.loc[index,'name'] = 'hamilton college'
        elif any(row['College Name or Type']==x for x in topN_groups["top30_lac"]):
            df_unfilled.loc[index,'name'] = 'macalester college'
        elif any(row['College Name or Type']==x for x in topN_groups["top40_lac"]):
            df_unfilled.loc[index,'name'] = 'union college'
        elif any(row['College Name or Type']==x for x in topN_groups["top50_lac"]):
            df_unfilled.loc[index,'name'] = 'gettysburg college'
        elif any(row['College Name or Type']==x for x in topN_groups["top75_lac"]):
            df_unfilled.loc[index,'name'] = 'wabash college'   
        elif any(row['College Name or Type']==x for x in topN_groups["top100_lac"]):
            df_unfilled.loc[index,'name'] = 'millsaps college'                         
        elif any(row['College Name or Type']==x for x in topN_groups["top5_eng"]):
            if 'midwest' in row['City']:
                df_unfilled.loc[index,'name'] = 'university of illinois urbana champaign'
            elif 'massachusetts' in row['State']:
                df_unfilled.loc[index,'name'] = 'massachusetts institute of technology'
            else:
                df_unfilled.loc[index,'name'] = 'georgia institute of technology'
        elif any(row['College Name or Type']==x for x in topN_groups["top10_eng"]):
            df_unfilled.loc[index,'name'] = 'carnegie mellon university'
        elif any(row['College Name or Type']==x for x in topN_groups["top20_eng"]):
            df_unfilled.loc[index,'name'] = 'university of wisconsin madison'
        elif any(row['College Name or Type']==x for x in topN_groups["top30_eng"]):
            df_unfilled.loc[index,'name'] = 'university of maryland college park'
        elif any(row['College Name or Type']==x for x in topN_groups["top50_eng"]):
            df_unfilled.loc[index,'name'] = 'lehigh university'
        elif any(row['College Name or Type']==x for x in topN_groups["top5_business"]):
            df_unfilled.loc[index,'name'] = 'northwestern university'
        elif any(row['College Name or Type']==x for x in topN_groups["top10_business"]):
            df_unfilled.loc[index,'name'] = 'university of virginia'
        elif any(row['College Name or Type']==x for x in topN_groups["top25_business"]):
            df_unfilled.loc[index,'name'] = 'university of texas austin'        
        elif any(row['College Name or Type']==x for x in topN_groups["special"]):
            if 'top 3 hbcu' in row['College Name or Type']:
                df_unfilled.loc[index,'name'] = 'howard university'
            elif 'go blue' in row['College Name or Type']:
                df_unfilled.loc[index,'name'] = 'university of michigan ann arbor'
            elif ('public' in row['College Name or Type'])|('ivy' in row['College Name or Type']):
                df_unfilled.loc[index,'name'] = 'university of north carolina chapel hill'
            elif 'public (military college)' in row['College Name or Type']:
                df_unfilled.loc[index,'name'] = 'the citadel'
            elif 'top 3 cal state' in row['College Name or Type']:
                df_unfilled.loc[index,'name'] = 'university of california berkeley'
            elif 'top 26, women' in row['College Name or Type']:
                df_unfilled.loc[index,'name'] = 'bryn mawr college'
            elif ('best' in row['College Name or Type'])|('west' in row['College Name or Type']):
                df_unfilled.loc[index,'name'] = 'stanford university'
            elif 'number 1 ranked la s' in row['College Name or Type']:
                df_unfilled.loc[index,'name'] = 'williams college'
            elif 'large public in northern va' in row['College Name or Type']:
                df_unfilled.loc[index,'name'] = 'university of virginia'
            elif ('public' in row['College Name or Type'])|('uc' in row['College Name or Type']):
                df_unfilled.loc[index,'name'] = 'university of california san diego'    
            elif 'private r1' in row['College Name or Type']:
                df_unfilled.loc[index,'name'] = 'northwestern university'                                                                                                           
        elif any(row['College Name or Type']==x for x in topN_groups["top150"]):
            print ''#row['College Name or Type'],'|',row['State'],'|',row['City']
        elif any(row['College Name or Type']==x for x in topN_groups["top150_beyond"]):
            print ''#row['College Name or Type'],'|',row['State'],'|',row['City']           
                                                                                        
    print len(df_unfilled[df_unfilled['name']==''])
    df = df_unfilled[df_unfilled['name']=='']
    print df['College Name or Type'].nunique()
    print df['College Name or Type'].unique()
    df_unfilled[df_unfilled['name']==''].to_csv('../../data/edit/df_topN_univ_unfilled.csv')
    df_combined = df_filled.append(df_unfilled,ignore_index=True)
    df_combined = df_combined.sort_values(by=['id'])
    df_combined.to_csv('../../data/edit/df_topN_univ_combined.csv')
    return
    
