import pandas as pd
import numpy as np
import __future__
import csv
from df2tex import df2tex, df2tex_hline
from datetime import datetime, timedelta,date


def headcounts_by_group_peer(df):
    df_headct = df.groupby(['User Name','Applicant Peer Type'])['Total Rounds'].agg(['count','mean']).reset_index()
    df1 = df_headct['Applicant Peer Type'].value_counts().rename_axis('Applicant Peer Type').reset_index(name='\# of Users')
    df2 = df_headct.groupby(['Applicant Peer Type'])[['count','mean']].sum().reset_index().rename(columns={'count':'\# of Rounds','mean':'\# of Apps'})
    df0 = df1.merge(df2,on=['Applicant Peer Type'],how='left').reset_index()
    for var in ['Users','Rounds','Apps']:
        x = df0['\# of {}'.format(var)].sum()
        df0['\% of {}'.format(var)] = df0['\# of {}'.format(var)]*100.0/x
    return df0.sort_values(['Applicant Peer Type'])

def law_school_ranks_by_group_peer(df):
    df0 = df.groupby(['Applicant Peer Type'])[['rank','ranked']].mean().reset_index().rename(columns={'rank':'Avg Ranks','ranked':'Pct Ranked'})
    return df0.sort_values(['Applicant Peer Type'])

def application_time_by_group_peer(df):
    df1 = df.groupby(['User Name','Applicant Peer Type'])['Total Rounds'].mean().reset_index()
    df2 = df.groupby(['User Name','Applicant Peer Type'])['Application Time'].agg(['min','max']).reset_index()
    df2['Span'] = df2['max'] - df2['min'] + 1
    df3 = df.groupby(['User Name','Applicant Peer Type'])['Law School'].count().reset_index()
    df0 = df1.merge(df2,on=['User Name','Applicant Peer Type'],how='left').reset_index()
    df0 = df0.merge(df3,on=['User Name','Applicant Peer Type'],how='left').reset_index()
    df0 = df0.groupby(['Applicant Peer Type'])[['Total Rounds','min','Span','Law School']].mean().rename(columns={'Total Rounds':'Avg \# of Rounds',
                     'Span':'Avg Length of Span','min':'Avg Days till 1st App','Law School':'Avg \# of Apps'})
    return df0.sort_values(['Applicant Peer Type'])

def range_applications_by_group_peer(df):
    lst = ['Best App Per Round','Worst App Per Round','Range of Apps Per Round','Ranked App Per Round',
           'Best Offer Per Round','Offer Rate Per Round','Median App Per Round','Avg App Per Round']
    df_r = df.groupby(['User Name','Applicant Peer Type','Round Number'])[lst].mean()\
           .sort_values(['Applicant Peer Type','User Name','Round Number']).reset_index()
    df_r['Ranked App Per Round'] = df_r['Ranked App Per Round']*100.0
    df_r_head = df_r.groupby(['Applicant Peer Type','User Name']).first()
    df_r_tail = df_r.groupby(['Applicant Peer Type','User Name']).last()
    df1 = df_r_head.groupby(['Applicant Peer Type'])[lst].mean().reset_index().rename(columns={'Ranked App Per Round':'Pct Apps Ranked Per Round'})
    df2 = df_r_tail.groupby(['Applicant Peer Type'])[lst].mean().reset_index().rename(columns={'Ranked App Per Round':'Pct Apps Ranked Per Round'})
    return df1.sort_values(['Applicant Peer Type']), df2.sort_values(['Applicant Peer Type'])

def applicant_char_by_group_peer(df,sample_str):
    lst_char = ['GPA','LSAT']
    df_user = pd.read_csv('../../data/edit/df_all_samples_{}.csv'.format(sample_str))
    df_user = df_user.groupby(['User Name'])[lst_char].mean().reset_index()
    df_head = df.drop(lst_char,axis=1).groupby(['User Name','Applicant Peer Type']).first().reset_index()
    df_user = df_user.merge(df_head,on=['User Name'],how='right').reset_index()
    df0 = df_user.groupby(['Applicant Peer Type'])[lst_char].mean().reset_index()
    return df0.sort_values(['Applicant Peer Type'])

def timing_outcomes_arrival_peer(df,sample_str):
    df_user_type = df.groupby(['User Name','Applicant Peer Type']).first().reset_index()
    df_user_type = df_user_type[['User Name','Applicant Peer Type']]
    df_info = pd.read_csv('../../data/edit/df_all_samples_{}.csv'.format(sample_str))
    
    lst = ['Accepted','Rejected','Waitlisted','Sent_delta','Decision_delta','User Name']
    df_outcomes = df_info[lst].merge(df_user_type,on=['User Name'],how='right').reset_index()
    df_outcomes['tm'] = df_outcomes['Sent_delta'] + df_outcomes['Decision_delta']
    
    df0 = pd.DataFrame()
    lst_outcomes = ['Accepted','Rejected','Waitlisted']
    lst_outcomes_label = ['Offer','Rejection','Waitlist']
    for c, item in enumerate(lst_outcomes):
        df_sub = df_outcomes[df_outcomes[item]==1]
        df_sub = df_sub.groupby(['User Name','Applicant Peer Type'])['tm'].min().reset_index()
        df_sub = df_sub.groupby(['Applicant Peer Type'])['tm'].agg(['mean','count']).reset_index()\
                 .rename(columns={'mean':'Date of Arrival','count':'Obs'})
        df_sub['Outcomes'] = 'First {}'.format(lst_outcomes_label[c])
        df0 = df0.append(df_sub)
    return df0

def bounded_by_results_peer(df):
    lst_bound = ['Best Peer Offer ic','Best Peer Rejection ic','Best App Per Round ic',
                 'Worst App Per Round ic']
    dics={}
    df_r = df[df['Applicant Peer Type']=='Group 3']
    df_r = df_r.groupby(['User Name','Applicant Peer Type','Round Number'])[lst_bound].mean().reset_index()
    dics['Total'] = [1,len(df_r),np.nan]
    
    df_l = df_r[df_r['Best Peer Offer ic'].notnull()]    
    x = len(df_l)
    y = len(df_l[df_l['Worst App Per Round ic']<df_l['Best Peer Offer ic']])
    z = len(df_l[df_l['Worst App Per Round ic']==df_l['Best Peer Offer ic']])
    q = len(df_l[df_l['Worst App Per Round ic']>df_l['Best Peer Offer ic']])
    dics['Peers Having Offers at Hand'] = [2,x,100.00]
    dics['Worst App Strictly Better than Best Peer Offer at Hand'] = [3,y,y*100.0/x]
    dics['Worst App Equaling to Best Peer Offer at Hand'] = [4,z,z*100.0/x]
    dics['Worst App Strictly Worse than Best Peer Offer at Hand'] = [5,q,q*100.0/x]
    
    df_m = df_r[df_r['Best Peer Rejection ic'].notnull()]
    x = len(df_m)
    y = len(df_m[df_m['Best App Per Round ic']<df_m['Best Peer Rejection ic']])
    z = len(df_m[df_m['Best App Per Round ic']==df_m['Best Peer Rejection ic']])
    q = len(df_m[df_m['Best App Per Round ic']>df_m['Best Peer Rejection ic']])
    dics['Peers Having Rejections at Hand'] = [6,x,100.00]
    dics['Best App Strictly Better than Best Peer Rejection at Hand'] = [7,y,y*100.0/x]
    dics['Best App Equaling to Best Peer Rejection at Hand'] = [8,z,z*100.0/x]
    dics['Best App Strictly Worse than Best Peer Rejection at Hand'] = [9,q,q*100.0/x]
    
    df0 = pd.DataFrame.from_dict(dics,orient='index',columns=['Order','\# of Rounds','Pct of Rounds'])\
            .sort_values(['Order'])                                                                                              
    return df0[['\# of Rounds','Pct of Rounds']] 
                
def timing_action_outcomes_peer(df):
    df_gp3 = df[df['Applicant Peer Type']=='Group 3']
    df_dic = {}
    df_out_dic = {}
    
    df_2check = df_gp3.groupby(['User Name','Round Number'])['Number of Offers'].mean().reset_index()
    df_2check = df_2check.groupby(['User Name'])['Round Number'].count().reset_index()
    print 'Double Check Data Consistency: Avg Number of Rounds',df_2check[['Round Number']].mean()
    
    lst_timing = ['Before','After']
    for timing_ct, timing in enumerate(lst_timing):
        print 'Application {} Arrival of Outcomes'.format(timing)
        df0 = df_gp3[df_gp3['Round Peer Type']==timing_ct]
        
        df0_ct = df0.groupby(['User Name','Round Number'])['Round Peer Type'].count().reset_index()\
                 .rename(columns={'Round Peer Type':'Number of Apps Per Round'})
        df0_rd = df0_ct.groupby(['User Name'])['Round Number'].nunique().reset_index()
        df_dic['\# Rounds'] = [1] + df0_rd['Round Number'].agg(['mean','std']).tolist()
        df0_app = df0_ct.groupby(['User Name'])['Number of Apps Per Round'].sum().reset_index()
        df_dic['\# Apps'] = [2] + df0_app['Number of Apps Per Round'].agg(['mean','std']).tolist()
    
        df0_day = df0.groupby(['User Name'])['Application Time'].agg(['min','max']).reset_index()
        df_dic['First Day of App'] = [3] + df0_day['min'].agg(['mean','std']).tolist()
        df_dic['Last Day of App'] = [4] + df0_day['max'].agg(['mean','std']).tolist()
    
        lst = ['Number of Peer Offers','Number of Peer Rejections','Number of Peer Waitlists']
        lst_short = ['Peer Offers','Peer Rejections','Peer Waitlists']
        df0_info = df0.groupby(['User Name','Round Number'])[lst].mean().reset_index()
        df0_info = df0_info.sort_values(['User Name','Round Number']).groupby(['User Name']).first().reset_index()
        for c, x in enumerate(lst_short):
            df_dic['\# {} at First Round'.format(x)] = [5+c] + df0_info['Number of {}'.format(x)].agg(['mean','std']).tolist()
        
        df_out_dic['App_{}_Arrival_of_Outcomes'.format(timing)] = pd.DataFrame.from_dict(df_dic,orient='index',columns=['order','mean','std'])\
                 .rename(columns={'mean':'Mean','std':'SD'}).sort_values(['order'])
    
    return df_out_dic['App_Before_Arrival_of_Outcomes'].head(4),df_out_dic['App_After_Arrival_of_Outcomes']

def rounds_char_dynamic_peer(df):
    group_num = [2,3]
    df_gp_dic = {}
    for gp in group_num:
        df_type = df[df['Applicant Peer Type']=='Group {}'.format(gp)]
        print 'rounds_char_dynamic: Group {}'.format(gp),df_type['User Name'].nunique()
        round_max = 6
        lst = ['Best App Per Round','Worst App Per Round','Range of Apps Per Round']
        df_out_dic = {}
        for it in range(2,round_max+1):
            df_it = df_type[df_type['Total Rounds']==it]
            user_ct = df_it['User Name'].nunique()
            for im in range(1,it+1):
                df_im = df_it[df_it['Round Number']==im].groupby(['User Name'])[lst].mean().reset_index()
                df_out_dic['Total Round {}, Round {}'.format(it,im)] = [im,it,user_ct]+df_im[lst].mean().tolist()
        df_out = pd.DataFrame.from_dict(df_out_dic,orient='index',columns=['Round Number','Total Rounds','\# Applicant','Avg Best App','Avg Worst App','Avg Range'])    
        df_gp_dic['{}'.format(gp)] = df_out.sort_values(['Total Rounds','Round Number'])
    return df_gp_dic['2'],df_gp_dic['3']

def group_basic_stats_peer(sample_str):
    df = pd.read_csv('../../data/edit/simulate_outputs_student_{}.csv'.format(sample_str))
    print df.columns.tolist()
    df_stats_dic = {}
    
    # Extract those who apply to ranked schools only. 
    df_ranked_only = df[df['Ranked Only']==1]
    df0 = df_ranked_only.groupby(['User Name','Applicant Peer Type'])['Ranked Only'].mean().reset_index()
    df0 = df0['Applicant Peer Type'].value_counts().rename_axis('Applicant Peer Type').reset_index(name='\# of Users')

    # Summary Statistics by Rounds
    df_stats_dic['stats_group_size_peer'] = headcounts_by_group_peer(df)
    df_stats_dic['stats_group_rank_peer'] = law_school_ranks_by_group_peer(df)        
    df_stats_dic['stats_group_time_peer'] = application_time_by_group_peer(df)
    df_stats_dic['stats_group_range_first_peer'],df_stats_dic['stats_group_range_last_peer'] = range_applications_by_group_peer(df)
    df_stats_dic['stats_group_range_first_ranked_only_peer'],df_stats_dic['stats_group_range_last_ranked_only_peer'] = range_applications_by_group_peer(df_ranked_only)
    df_stats_dic['stats_group_char_peer'] = applicant_char_by_group_peer(df,sample_str)
    df_stats_dic['stats_group_first_outcome_peer'] = timing_outcomes_arrival_peer(df,'d1')
    df_stats_dic['stats_group3_bounds_peer'] = bounded_by_results_peer(df)
    df_stats_dic['app_before_arrival_of_outcomes_gp3_peer'],df_stats_dic['app_after_arrival_of_outcomes_gp3_peer']=timing_action_outcomes_peer(df)
    df_stats_dic['dynamic_rd_group2_peer'], df_stats_dic['dynamic_rd_group3_peer'] = rounds_char_dynamic_peer(df_ranked_only)
    
    print df_stats_dic.keys()
    return df_stats_dic

def export_group_stats_peer(df_stats_dic):
    lst_range = ['Best App Per Round','Worst App Per Round','Range of Apps Per Round','Pct Apps Ranked Per Round',
                 'Median App Per Round','Avg App Per Round'] #'Best Offer Per Round','Offer Rate Per Round'
    lst_range_shrt = [i.replace(' Per Round','') for i in lst_range]
    complex_row_col = {
            'stats_group_size_peer':[['Group 1','Group 2','Group 3'],{'':''},
                                ['\# of Users','\% of Users','\# of Rounds','\% of Rounds','\# of Apps','\% of Apps']],
            'stats_group_time_peer':[['Group 1','Group 2','Group 3'],{'':''},
                                ['Avg Days till 1st App','Avg Length of Span','Avg \# of Rounds','Avg \# of Apps']],
            'stats_group_rank_peer':[['Group 1','Group 2','Group 3'],{'rank':'Avg Ranks','ranked':'Pct Ranked'},
                                ['Avg Ranks','Pct Ranked']],
            'stats_group_range_first_peer':[['Group 1','Group 2','Group 3'],{'':''},lst_range],
            'stats_group_range_last_peer':[['Group 1','Group 2','Group 3'],{'':''},lst_range],
            'stats_group_range_first_ranked_only_peer':[['Group 1','Group 2','Group 3'],{'':''},lst_range],
            'stats_group_range_last_ranked_only_peer':[['Group 1','Group 2','Group 3'],{'':''},lst_range],
            'stats_group_char_peer':[['Group 1','Group 2','Group 3'],{'':''},['LSAT','GPA']],
            'stats_group3_bounds_peer':[['Total','Peers Having Offers at Hand','Worst App Strictly Better than Best Peer Offer at Hand',
                                    'Worst App Equaling to Best Peer Offer at Hand','Worst App Strictly Worse than Best Peer Offer at Hand',
                                    'Peers Having Rejections at Hand','Best App Strictly Better than Best Peer Rejection at Hand',
                                    'Best App Equaling to Best Peer Rejection at Hand','Best App Strictly Worse than Best Peer Rejection at Hand'],
                                    {'':''},['\# of Rounds','Pct of Rounds']],
            'stats_group_first_outcome_peer':[['First Peer Offer: Group 1','\qquad\qquad\quad\; Group 2','\qquad\qquad\quad\; Group 3',
                                          'First Peer Rejection: Group 1','\qquad\qquad\qquad\quad Group 2','\qquad\qquad\qquad\quad Group 3',
                                          'First Peer Waitlist: Group 1','\qquad\qquad\qquad\quad Group 2','\qquad\qquad\qquad\quad Group 3'],
                                         {'':''},['Date of Arrival','Obs']],
            'app_before_arrival_of_outcomes_gp3_peer':[['\# Rounds','\# Apps','First Day of App','Last Day of App'],{'':''},['Mean','SD']],
            'app_after_arrival_of_outcomes_gp3_peer':[['\# Rounds','\# Apps','First Day of App','Last Day of App',
                                                      '\# Peer Offers at First Round','\# Peer Rejections at First Round',
                                                      '\# Peer Waitlists at First Round'],{'':''},['Mean','SD']   ],
            'dynamic_rd_group2_peer':[None,{'':''},['Total Rounds','\# Applicant','Round Number','Avg Best App','Avg Worst App','Avg Range'],[1,4,8,13]],
            'dynamic_rd_group3_peer':[None,{'':''},['Total Rounds','\# Applicant','Round Number','Avg Best App','Avg Worst App','Avg Range'],[1,4,8,13]]                                                                          
            }
    for key, df in df_stats_dic.iteritems():
        cols = complex_row_col[key][2]
        df = df.rename(columns=complex_row_col[key][1])
        if complex_row_col[key][0]: # with row names
            df = df.assign(Variable=complex_row_col[key][0]) 
            df = df[cols+['Variable']]
            df2tex(df, '../../model/tables/','{}_obj.tex'.format(key), "%8.2f", 0, cols, ['Variable'], cols)
        else: # without row names
            df = df[cols]
            hline_lst = complex_row_col[key][3]
            df2tex_hline(df, '../../model/tables/','{}_obj.tex'.format(key), "%8.2f", 0, cols, None, cols,hline_lst)
    return

if __name__ == '__main__':
    df_stats_dic = group_basic_stats_peer('d1')
    export_group_stats_peer(df_stats_dic)