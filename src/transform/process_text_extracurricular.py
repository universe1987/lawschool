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
import nltk 
from autocorrect import spell
from ngram import NGram
import difflib
import urllib2
import textwrap
#from tabula import read_pdf,convert_into
from bs4 import BeautifulSoup
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from stop_words import get_stop_words
from nltk.stem.porter import PorterStemmer

import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import JSON_DIR, ENTRY_DIR
from extract.utils import remove_special_char,keep_ascii
from StopWatch import StopWatch

def display_topics(model, feature_names, no_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words - 1:-1]]))
    return

def display_topics_more(H, W, feature_names, documents, no_top_words, no_top_documents):
    for topic_idx, topic in enumerate(H):
        print "Topic %d:" % (topic_idx)
        print " ".join([feature_names[i]
                        for i in topic.argsort()[:-no_top_words - 1:-1]])
        top_doc_indices = np.argsort( W[:,topic_idx] )[::-1][0:no_top_documents]
        for doc_index in top_doc_indices:
            print documents[doc_index]
    return

def indent_wrap(string,prefix,preferred_width):
    wrapper = textwrap.TextWrapper(initial_indent=prefix, width=preferred_width,
                                   subsequent_indent=' '*len(prefix))
    message = wrapper.fill(string)
    return message

def extract_extracurriculars():

    df_details = pd.read_csv('../../data/edit/df_details_race_college_cleaned.csv')
    df_details = df_details.fillna('')
    print df_details.columns.tolist()
    print df_details['extra curricular'].head(10)
    
    # Print out for reading
    file = open('../../data/edit/read_extra_curricular.txt', 'w')
    for index, row in df_details.iterrows():
        strings = row['extra curricular']
        if strings == '':
            strings = 'N/A'
        prefixs = row['User Name'] + ' '*4
        preferred_widths = 70
        message = indent_wrap(strings,prefixs,preferred_widths) + '\n'
        divider = '=='*15
        file.write(message)
        file.write(divider+'\n')
    file.close()
    
    # Export to csv for classification
    df_classify = df_details[['User Name','extra curricular']]
    list_softs = ['Greek','Community/Volunteer','Athletic/Varsity','Student Societies',
                  'Military','Overseas','Non-legal Internship','Legal Internship',
                  'Non-Legal Work Experience','Legal Work Experience','Strong Letters','Leadership']
    for item in list_softs:
        df_classify[item] = ''
    
    df = df_classify.drop(['extra curricular'],axis=1)
    df.to_csv('../../data/edit/classify_extra_curricular.csv')
    
    # Estimate the workload / non-trivial extra-curriculars
    print 'len(df_classify)', len(df_classify)
    
    df_classify_nonempty = df_classify[df_classify['extra curricular']!='']
    print 'len(df_classify_nonempty)', len(df_classify_nonempty)
    
    df_classify['length'] = df_classify['extra curricular'].str.len()
    df_classify_long = df_classify[df_classify['length']>=30]
    print 'len(df_classify_long)', len(df_classify_long)
    
    raw_input('Done printing out!')
    return
    
    # Drop empty cells
    #print len(df_details)
    #df_details['extra curricular'] = df_details[df_details['extra curricular']!='']
    #print len(df_details)
    
def merge_back_extracurricular_classified():    
    # Read the background data
    df_details = pd.read_csv('../../data/edit/df_details_race_college_major_numeric_cleaned.csv')
    df_details = df_details.fillna('')
    df_details = df_details.drop(['extra curricular'],axis=1)
    
    # Read the mother data of ECs
    df_mom = pd.read_csv('../../data/edit/df_details_race_college_cleaned.csv')
    df_mom = df_mom.fillna('')
    df_mom = df_mom[['User Name','extra curricular']]
    print df_mom.columns.tolist()
    print df_mom['extra curricular'].head(10)
    print df_mom['User Name'].nunique(),len(df_mom['User Name'])
    
    # Merge mom to the background
    df_mother = df_details.merge(df_mom,on=['User Name'],how='left').reset_index()
    df_mother = df_mother.drop(['level_0'],axis=1)
    print df_mother.columns.tolist()
    
    # Read Children data of ECs
    df_children = pd.read_csv('../../data/entry/lara_extra_curricular/classified/(Demerji) classify_extra_curricular.csv')
    print df_children['User Name'].nunique(),len(df_children['User Name'])
    
    df_demerji = pd.read_csv('../../data/entry/lara_extra_curricular/classified/(Demerji) classify_extra_curricular.csv')
    df_demerji = df_demerji[df_demerji['Unnamed: 0']<=11783]
    df_demerji = df_demerji.rename(columns={'Non-Legal Work Experience':'Non-legal Work Experience'})
    print df_demerji['User Name'].nunique(),len(df_demerji['User Name'])
    print df_demerji['Community/Volunteer'].unique()
    
    
    df_kouzela = pd.read_csv('../../data/entry/lara_extra_curricular/classified/(Kouzela) classify_extra_curricular.csv')
    df_kouzela = df_kouzela[df_kouzela['User Name'].notnull()] # Remove blank user names
    df_kouzela = df_kouzela[(df_kouzela['Unnamed: 0']>=11784)&(df_kouzela['Unnamed: 0']<=20000)|
                            (df_kouzela['Unnamed: 0']>=28194)&(df_kouzela['Unnamed: 0']<=30000)|
                            (df_kouzela['Unnamed: 0']>=40001)&(df_kouzela['Unnamed: 0']<=53393)]
    print df_kouzela['User Name'].nunique(),len(df_kouzela['User Name'])
    print df_kouzela['Community/Volunteer'].unique()
    print df_kouzela.columns.tolist()
    
    df_kroone = pd.read_csv('../../data/entry/lara_extra_curricular/classified/(Kroone) classify_extra_curricular.csv')
    df_kroone = df_kroone[df_kroone['Unnamed: 0']>=53394]
    print df_kroone['User Name'].nunique(),len(df_kroone['User Name'])
    print df_kroone['Community/Volunteer'].unique()
    print df_kroone.columns.tolist()
    
    df_locke = pd.read_csv('../../data/entry/lara_extra_curricular/classified/(Locke) classify_extra_curricular.csv')
    df_locke = df_locke[(df_locke['Unnamed: 0']>=30001)&(df_locke['Unnamed: 0']<=40000)]
    print df_locke['User Name'].nunique(),len(df_locke['User Name'])
    print df_locke['Community/Volunteer'].unique()
    print df_locke.columns.tolist()
    
    df_brown = pd.read_csv('../../data/entry/lara_extra_curricular/classified/(Brown) classify_extra_curricular.csv')
    df_brown = df_brown[(df_brown['Unnamed: 0']>=20001)&(df_brown['Unnamed: 0']<=28193)]
    print df_brown['User Name'].nunique(),len(df_brown['User Name'])
    print df_brown['Community/Volunteer'].unique()
    print df_brown.columns.tolist()
    
    list_kids = [df_demerji,df_kouzela,df_kroone,df_locke,df_brown]
    df_kids = pd.concat(list_kids).drop(['Unnamed: 0'],axis=1)
    
    # Merge Mother and Kids
    df_home = df_mother.merge(df_kids,on='User Name',how='left').reset_index()
    print df_home['User Name'].nunique()
    
    # Disentangle non-reporting from non-useful-activities
    print df_kids.columns.tolist()
    softs = ['Athletic/Varsity', 'Community/Volunteer', 'Greek', 'Leadership', 'Legal Internship',
             'Legal Work Experience', 'Military', 'Non-legal Internship', 
             'Non-legal Work Experience', 'Overseas', 'Strong Letters', 'Student Societies']
    for index,item in enumerate(softs):
        df_home[item] = df_home[item].fillna('').astype(str)
        #print df_home[item].unique()
        df_home.loc[(df_home[item]=='1.0')|(df_home[item]=='2.0')|(df_home[item]=='1')|(df_home[item]=='q'),item] = '1.0'
        df_home.loc[df_home[item]!='1.0',item]='0.0'
        df_home.loc[df_home['extra curricular'] == '',item] = ''
        df_home[item] = pd.to_numeric(df_home[item],errors='coerce')
        print df_home[item].unique(),df_home[item].mean()
    
    df_home['EC at all'] = df_home[softs].sum(axis=1)
    df_home.loc[df_home['EC at all']>0,'EC at all'] = 1.0
    print df_home['EC at all'].mean(),df_home['EC at all'].unique()
    print df_home[softs+['EC at all','User Name','extra curricular']].head(5)
    
    # Export to csv
    print df_home.columns.tolist()
    df_home.to_csv('../../data/edit/df_details_race_college_major_numeric_EC_cleaned.csv')
    
    return

def topic_modelling_yujia():
    # Keep valid characters only
    df_details['extra curricular'] = df_details['extra curricular'].apply(lambda x: ''.join([i if (ord(i)==32)|(ord(i)==39)|(64 < ord(i) < 91)|(96<ord(i)<123) else " " for i in x]))

    #Tokenization
    tokenizer = RegexpTokenizer(r'\w+')
    df_details['extra curricular']=df_details['extra curricular'].str.lower() 
    df_details['token']=df_details['extra curricular'].apply(lambda x: tokenizer.tokenize(x))
    print df_details['token'].head(10)
    
    #Stop words
    en_stop = get_stop_words('en')
    df_details['stopped_tokens']=df_details['token'].apply(lambda x: [i for i in x if not i in en_stop])
    print df_details['stopped_tokens'].head(10)
    
    #Stemming
    p_stemmer = PorterStemmer()
    df_details['texts_cleaned']=df_details['stopped_tokens'].apply( lambda x:[p_stemmer.stem(i) for i in x] )
    print df_details['texts_cleaned'].head(10)
    
    #converting back to strings#convert 
    df_details['text_str']=df_details['texts_cleaned'].apply(lambda x: ' '.join(x))
    print df_details['text_str'].head(10)
    
    # topic modeling: LDA and NMF
    no_features = 1000
    documents=df_details['text_str']
    number_topics = 20
    
    # NMF is able to use tf-idf
    tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
    tfidf = tfidf_vectorizer.fit_transform(documents)
    tfidf_feature_names = tfidf_vectorizer.get_feature_names()

    # LDA can only use raw term counts for LDA because it is a probabilistic graphical model
    tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=no_features, stop_words='english')
    tf = tf_vectorizer.fit_transform(documents)
    tf_feature_names = tf_vectorizer.get_feature_names()
    
    # Run NMF# Run NM 
    nmf_model = NMF(n_components=number_topics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
    nmf_W = nmf_model.transform(tfidf)
    nmf_H = nmf_model.components_
    
    # Run LDA# Run LD 
    lda_model = LatentDirichletAllocation(n_topics=number_topics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
    lda_W = lda_model.transform(tf)
    lda_H = lda_model.components_
    
    # Display results (Concise)
    number_top_words = 12
    display_topics(nmf_model, tfidf_feature_names, number_top_words)
    display_topics(lda_model, tf_feature_names, number_top_words)
    
    # Display results (Details)
    no_top_words = 12
    no_top_documents = 10
    display_topics_more(nmf_H, nmf_W, tfidf_feature_names, documents, no_top_words, no_top_documents)
    display_topics_more(lda_H, lda_W, tf_feature_names, documents, no_top_words, no_top_documents)
    
    return
    
