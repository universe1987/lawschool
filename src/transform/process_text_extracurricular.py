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
import textwrap
from tabula import read_pdf,convert_into
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
                  'Work Experience','Strong Letters','Leadership']
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
    
