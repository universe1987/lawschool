import pandas as pd
import numpy as np
from Registry import Registry
from Application import Application
from School import School
import __future__
import csv
import json
from df2tex import df2tex
from datetime import datetime, timedelta,date
from export_stata import output_sample_stata


def load_data(filename):
    column_datatype = {'User Name': 'str',
                       'Law School': 'str',
                       'Sent_delta': 'float',#'int32',
                       'Decision_delta': 'float',#'int32',
                       'Waitlisted': 'bool',
                       'Accepted': 'bool',
                       'Rejected': 'bool',
                       'Pending': 'bool',
                       'rank_2010_cp':'float',
                       'unranked_2010':'float',
                       'rank_cross':'float',
                       'unranked':'float',
                       'Sent_weekday':'float',
                       'Year':'float',
                       'LSAT':'float',
                       'GPA':'float'
                       }
    df = pd.read_csv(filename)[list(column_datatype.keys())]
    print df['rank_cross'].describe()
    df = df.drop_duplicates()
    return df.astype(column_datatype)


def extract_events(df, registry):
    event_queue = []
    for idx, row in df.iterrows():
        student = registry.get_or_create_student(row['User Name'],row['LSAT'],row['GPA'])
        school = registry.get_or_create_school(row['Law School'])
        school.rank_2010 = row['rank_2010_cp']
        school.ranked_2010 = 1.0-row['unranked_2010']
        school.rank = row['rank_cross']
        school.ranked = 1.0-row['unranked']
        school.rank_ic = row['rank_cross'] if row['rank_cross']>0 else 300.0
        application_time = row['Sent_delta']
        application = registry.get_application(student, school)
        if application is None:
            application = registry.create_application(student, school, application_time)
            application.application_weekday = row['Sent_weekday']
            event_queue.append([application_time, application, 'send'])
        decision_time = application_time + row['Decision_delta']
        if row['Accepted']:
            event_queue.append([decision_time, application, Application.OFFER])
        elif row['Rejected']:
            event_queue.append([decision_time, application, Application.REJECTION])
        elif row['Waitlisted']:
            event_queue.append([decision_time, application, Application.WAITING_LIST])
    event_queue.sort(key=lambda s: s[0])
    return event_queue

'''
def aggregate_peers(df,registry,LSAT_radius,GPA_radius):
    df_user = df.groupby(['User Name','LSAT','GPA']).first().reset_index()
    df_user = df_user[['User Name','LSAT','GPA']]
    for idx1, row1 in df_user.iterrows():
        registry.get_or_create_one_peer_name(row1['User Name'],'')
        registry.get_or_create_one_peer(row1['User Name'],'')
        for idx2, row2 in df_user.head(idx1).iterrows(): #the person himself is not included
            if (abs(row1['LSAT']-row2['LSAT'])<=LSAT_radius) & \
               (abs(row1['GPA']-row2['GPA'])<=GPA_radius) :
                registry.get_or_create_one_peer_name(row1['User Name'],row2['User Name'])
                registry.get_or_create_one_peer_name(row2['User Name'],row1['User Name'])
                registry.get_or_create_one_peer(row1['User Name'],row2['User Name'])
                registry.get_or_create_one_peer(row2['User Name'],row1['User Name'])
    for idx, row in df_user.iterrows():
        student = registry.get_or_create_student(row['User Name'],0.0,0.0)
        student.peer_names = registry.get_all_peer_names(row['User Name'])
        student.peers = registry.get_all_peers(row['User Name'])
        print student.name, len(student.peer_names),len(student.peers)
    return 
'''

'''
def simulate_student():
    registry = Registry()
    df = load_data('../../data/edit/df_all_samples_d1.csv') #qpig_dynamic_sample.csv
    print df.columns.tolist()
    print 'Minimum Time Between Application and Decision',df['Decision_delta'].describe()
    result = [['User Name', 'Law School','rank','ranked', #'rank_2010_cp','ranked_2010',
               'Application Time','Application Weekday',
               'Number of Offers', 'Number of Waitlists', 'Number of Rejections',
               'Best Offer','Worst Rejection','Best Waitlist','Worst Waitlist',
               'Median App']]
    for event in extract_events(df, registry):
        time, application, operation = event
        if operation == 'send':
            application.send_application()
            student = application.student
            list_app_rank = [i.school.rank for i in student.applications]
            list_offer_rank = [i.school.rank for i in student.offers.values()]
            list_reject_rank = [i.school.rank for i in student.rejections.values()]
            list_waitlist_rank = [i.school.rank for i in student.waiting_list.values()]
            result.append([student.name, application.school.name,application.school.rank,application.school.ranked,
                           time, application.application_weekday,len(student.offers), len(student.waiting_list), len(student.rejections),
                           np.nanmin(list_offer_rank) if list_offer_rank else None,
                           np.nanmax(list_reject_rank) if list_reject_rank else None,
                           np.nanmin(list_waitlist_rank) if list_waitlist_rank else None,
                           np.nanmax(list_waitlist_rank) if list_waitlist_rank else None,
                           np.nanmedian(list_app_rank) if list_app_rank else None])
        else:
            application.send_decision(operation, time)
    with open('../../data/edit/simulate_outputs.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in result:
            writer.writerow(row)
    return


def choice_set_outcomes(): #useless
    df = load_data('../../data/edit/df_all_samples_d1.csv')
    dic_choice = {}
    for v in df['User Name'].unique():
        dic_choice[v] = {}
    for c, row in df.iterrows():
        dic_choice[row['User Name']][row['Law School']] = row['Sent_delta']
    
    result = [['User Name','Law School','Sent_delta','Apply']]
    for key, value in dic_choice.iteritems(): # Key=User Name,value={Law School: Sent_delta}
        for k, v in value.iteritems(): #k=Law School,v=Sent_delta
            k_list = [ x for x in set(value.values()) if x <= v]
            for z in k_list:
                result.append([key,k,z,1.0*(z==v)])
                
    with open('../../data/edit/choice_set_outcomes.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in result:
            writer.writerow(row)
    return
'''

def simulate_both(sample_str):
    
    df = load_data('../../data/edit/df_all_samples_{}.csv'.format(sample_str)) #qpig_dynamic_sample.csv
    print df.columns.tolist()
    print 'Minimum Time Between Application and Decision',df['Decision_delta'].describe()
    result_student_head = ['User Name','LSAT','GPA','Number of Peers','Year', #'rank_2010_cp','ranked_2010',
                           'Application Time','Law School','rank','ranked',
                           'Application Weekday', 'Round Number',
                           'Number of Offers', 'Number of Waitlists', 'Number of Rejections',
                           'Number of Peer Offers', 'Number of Peer Rejections', 'Number of Peer Waitlists',
                           'Best Offer','Median Offer','Best Rejection','Median Rejection',
                           'Best Waitlist','Median Waitlist','Best Offer ic', 'Best Rejection ic',
                           'Best Peer Offer','Best Peer Rejection',
                           'Best Peer Offer ic','Best Peer Rejection ic',
                           'Median Peer Offer','Median Peer Rejection',
                           'Round Type','Round Peer Type',
                           'Number of Apps Per Round','Number of Ranked Apps Per Round',
                           'Best App Per Round','Worst App Per Round','Range of Apps Per Round',
                           'Median App Per Round','Avg App Per Round','Ranked App Per Round',
                           'Best App Per Round ic','Worst App Per Round ic',
                           'Offer Rate Per Round','Best Offer Per Round','Worst Offer Per Round',
                           'Total Rounds','Applicant Type','Applicant Peer Type','Ranked Only','Total Apps','Total Offers',
                           'Total Rejections','Total Waitlists',
                           'Best Offer Newly Received','Best Rejection Newly Received',
                           'Median Offer Newly Received','Median Rejection Newly Received',
                           'Best Peer Offer Newly Received','Best Peer Rejection Newly Received',
                           'Median Peer Offer Newly Received','Median Peer Rejection Newly Received',
                           'Gap Left','Gap Right']
    result_school_head =  ['Law School','User Name', 'Year','rank','ranked','Time',
                           'Number of Apps Received','Number of Offers Made', 
                           'Number of Waitlists Made', 'Number of Rejections Made',
                           'Number of Apps Received per Day','Number of Offers Made per Day', 
                           'Number of Waitlists Made per Day', 'Number of Rejections Made per Day',
                           'Number of Apps Received by Day','Number of Offers Made by Day', 
                           'Number of Waitlists Made by Day', 'Number of Rejections Made by Day']
    
    with open('../../data/edit/simulate_outputs_student_{}.csv'.format(sample_str), 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(result_student_head)
                
    with open('../../data/edit/simulate_outputs_school_{}.csv'.format(sample_str), 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(result_school_head)
    
    for yr in range(2006,2013):
        registry = Registry()
        result_student = [result_student_head]
        result_school = [result_school_head]
        events = extract_events(df[df['Year']==yr], registry)
        for event in events:
            time, application, operation = event
            if operation == 'send':
                application.send_application()
                student = application.student
                student.peer_offers = [j for i in student.peers for j in i.offers.values() ]
                student.peer_rejections = [i.rejections.values() for i in student.peers]
                student.peer_waiting_list = [i.waiting_list.values() for i in student.peers]
                list_offer_rank = [i.school.rank for i in student.offers.values()]
                list_reject_rank = [i.school.rank for i in student.rejections.values()]
                list_waitlist_rank = [i.school.rank for i in student.waiting_list.values()]
                list_offer_rank_ic = [i.school.rank_ic for i in student.offers.values()]
                list_reject_rank_ic = [i.school.rank_ic for i in student.rejections.values()]
                list_waitlist_rank_ic = [i.school.rank_ic for i in student.waiting_list.values()]
                x = 1.0*(len(student.offers)+len(student.rejections)+len(student.waiting_list)>0)
                list_peer_offer_rank = [j.school.rank for i in student.peers for j in i.offers.values()]
                list_peer_reject_rank = [j.school.rank for i in student.peers for j in i.rejections.values()]
                list_peer_offer_rank_ic = [j.school.rank_ic for i in student.peers for j in i.offers.values()]
                list_peer_reject_rank_ic = [j.school.rank_ic for i in student.peers for j in i.rejections.values()]
                x_peer = 1.0*(len(student.peer_offers)+len(student.peer_rejections)+len(student.peer_waiting_list)>0)
                result_student.append([student.name, student.LSAT, student.GPA,len(student.peers),yr,
                               time, application.school.name,application.school.rank,application.school.ranked,
                               application.application_weekday,application.round,
                               len(student.offers), len(student.waiting_list), len(student.rejections),
                               len(student.peer_offers),len(student.peer_rejections),len(student.peer_waiting_list),
                               np.nanmin(list_offer_rank) if list_offer_rank else None,
                               np.nanmedian(list_offer_rank) if list_offer_rank else None,
                               np.nanmin(list_reject_rank) if list_reject_rank else  None,
                               np.nanmedian(list_reject_rank) if list_reject_rank else None,
                               np.nanmin(list_waitlist_rank) if list_waitlist_rank else None,
                               np.nanmedian(list_waitlist_rank) if list_waitlist_rank else None,
                               np.nanmin(list_offer_rank_ic) if list_offer_rank_ic else None,
                               np.nanmin(list_reject_rank_ic) if list_reject_rank_ic else None,
                               np.nanmin(list_peer_offer_rank) if list_peer_offer_rank else None,
                               np.nanmin(list_peer_reject_rank) if list_peer_reject_rank else None,
                               np.nanmin(list_peer_offer_rank_ic) if list_peer_offer_rank_ic else None,
                               np.nanmin(list_peer_reject_rank_ic) if list_peer_reject_rank_ic else None,
                               np.nanmedian(list_peer_offer_rank) if list_peer_offer_rank else None,
                               np.nanmedian(list_peer_reject_rank) if list_peer_reject_rank else None,
                               x,x_peer])
            else:
                application.send_decision(operation, time)
            
            school = application.school
            result_school.append([school.name, application.student.name,yr,school.rank,school.ranked,
                               time, len(school.applications), len(school.offers),
                               len(school.waiting_list),len(school.rejections)])
        
        for row in result_student[1:]:
            student = registry.get_or_create_student(row[0],0.0,0.0)
            time = int(row[5])
            list_app_ranked_per_day = [i.school.ranked for i in student.applications_per_day[time]]
            list_app_rank_per_day = [i.school.rank for i in student.applications_per_day[time]]
            list_app_rank_ic_per_day = [i.school.rank_ic for i in student.applications_per_day[time]]
            list_offer_rank_per_day = [i.school.rank for i in student.offers_per_day[time].values()]
            list_offer_received_rank_per_day = [i.school.rank for i in student.offers_received_per_day[time].values()]
            list_rejection_received_rank_per_day = [i.school.rank for i in student.rejections_received_per_day[time].values()]   
            x = np.nanmin(list_app_rank_per_day) if list_app_rank_per_day else None
            y = np.nanmax(list_app_rank_per_day) if list_app_rank_per_day else None
            z = len(student.applications_per_day[time])
            m = np.nanmin(list_app_rank_ic_per_day) if list_app_rank_ic_per_day else None
            n = np.nanmax(list_app_rank_ic_per_day) if list_app_rank_ic_per_day else None
            row.extend([z,np.nansum(list_app_ranked_per_day),
                        x,y,y-x,np.nanmedian(list_app_rank_per_day) if list_app_rank_per_day else None,
                        np.nanmean(list_app_rank_per_day) if list_app_rank_per_day else None,
                        np.nanmean(list_app_ranked_per_day) if list_app_ranked_per_day else None,
                        m,n,len(student.offers_per_day[time])/float(z),
                        np.nanmin(list_offer_rank_per_day) if list_offer_rank_per_day else None,
                        np.nanmax(list_offer_rank_per_day) if list_offer_rank_per_day else None,
                        student.total_rounds,student.applicant_type,student.applicant_peer_type,student.ranked_only,
                        len(student.applications),len(student.offers),
                        len(student.rejections),len(student.waiting_list)])
        
        for row in result_student[1:]:
            student = registry.get_or_create_student(row[0],0.0,0.0)
            for day in range(student.ALL_DAY+1):
                student.peer_offers_received_per_day[day] = [j for i in student.peers for j in i.offers_received_per_day[day].values() ]
                student.peer_rejections_received_per_day[day] = [j for i in student.peers for j in i.rejections_received_per_day[day].values() ]

                
        for row in result_student[1:]:
            student = registry.get_or_create_student(row[0],0.0,0.0)
            day = int(row[5])
            if day in student.round_dates:
                x = student.round_dates.index(day)
                if x > 0 :
                    y=student.round_dates[x-1]
                else:
                    y=0
                list_offers_per_gap = [i for d in range(y,day) for i in student.offers_received_per_day[d].values()]
                list_rejections_per_gap = [i for d in range(y,day) for i in student.rejections_received_per_day[d].values()]
                list_peer_offers_per_gap = [i for d in range(y,day) for i in student.peer_offers_received_per_day[d]]
                list_peer_rejections_per_gap = [i for d in range(y,day) for i in student.peer_rejections_received_per_day[d]]

                list_offers_rank_per_gap = [i.school.rank for i in list_offers_per_gap]
                list_rejections_rank_per_gap = [i.school.rank for i in list_rejections_per_gap]
                list_peer_offers_rank_per_gap = [i.school.rank for i in list_peer_offers_per_gap]
                list_peer_rejections_rank_per_gap = [i.school.rank for i in list_peer_rejections_per_gap]
                row.extend([np.nanmin(list_offers_rank_per_gap) if list_offers_rank_per_gap else None,
                            np.nanmin(list_rejections_rank_per_gap) if list_rejections_rank_per_gap else None,
                            np.nanmedian(list_offers_rank_per_gap) if list_offers_rank_per_gap else None,
                            np.nanmedian(list_rejections_rank_per_gap) if list_rejections_rank_per_gap else None,
                            np.nanmin(list_peer_offers_rank_per_gap) if list_peer_offers_rank_per_gap else None,
                            np.nanmin(list_peer_rejections_rank_per_gap) if list_peer_rejections_rank_per_gap else None,
                            np.nanmedian(list_peer_offers_rank_per_gap) if list_peer_offers_rank_per_gap else None,
                            np.nanmedian(list_peer_rejections_rank_per_gap) if list_peer_rejections_rank_per_gap else None,
                            y, day])
            else:
                row.extend([None,None,None,None,None,None,None,None,None,None])

        for row in result_school[1:]:
            school = registry.get_or_create_school(row[0])
            time = int(row[5])
            row.extend([len(school.applications_per_day[time]),len(school.offers_per_day[time]),
                        len(school.waiting_list_per_day[time]),len(school.rejections_per_day[time]),
                        len(school.applications_by_day[time]),len(school.offers_by_day[time]),
                        len(school.waiting_list_by_day[time]),len(school.rejections_by_day[time])])
    
        with open('../../data/edit/simulate_outputs_student_{}.csv'.format(sample_str), 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in result_student[1:]:
                writer.writerow(row)
                
        with open('../../data/edit/simulate_outputs_school_{}.csv'.format(sample_str), 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in result_school[1:]:
                writer.writerow(row)
                    
    return


if __name__ == '__main__':
    #simulate_student()
    #choice_set_outcomes()
    
    '''
    registry = Registry()
    df = load_data('../../data/edit/df_all_samples_d1.csv')
    events = extract_events(df[df['Year']==2006], registry)
    
    LSAT_radius = 2.0
    GPA_radius = 0.2
    df = pd.read_csv('../../data/edit/df_all_samples_d1.csv')
    aggregate_peers(df[df['Year']==2006],registry,LSAT_radius,GPA_radius)
    '''
    
    simulate_both('d1')
    df = pd.read_csv('../../data/edit/simulate_outputs_student_{}.csv'.format('d1'))
    output_sample_stata(df,'simulate_outputs_student_{}'.format('d1'))
    



