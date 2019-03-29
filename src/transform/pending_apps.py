import pandas as pd
import numpy as np
import __future__
import csv
from df2tex import df2tex


def extract_best_worst_offer(df_str):
    df = pd.read_csv('../../data/edit/{}.csv'.format(df_str))  
    print df.columns.tolist()
    
    df_offer = df[df['Accepted']==1.0]
    df_offer_user = df_offer.groupby(['User Name'])['rank_cross'].agg(['min','max']).reset_index()\
                     .rename(columns={'min':'best offer','max':'worst offer'})
    df_offer_user_unranked = df_offer.groupby(['User Name'])['unranked'].max().reset_index()\
                     .rename(columns={'unranked':'has unranked offer'})
    df_pending = df[df['Pending']==1.0]
    df_both = df_pending.merge(df_offer_user,on='User Name',how='left').drop_duplicates().reset_index()\
              .drop('level_0',axis=1)
    df_both = df_both.merge(df_offer_user_unranked,on='User Name',how='left').drop_duplicates().reset_index()
    df_both.loc[df_both['has unranked offer']==1.0,'worst offer'] = np.nan
    return df_both

def compare_pending_best_worst_offer(df_both):
    dic_pending={}
    
    dic_pending['Total Pending Applications']=[len(df_both),100]
    
    df_best_ranked = df_both[df_both['best offer'].notnull()]
    df_best_unranked = df_both[df_both['best offer'].isnull()]
    print 'obs with best offer ranked',len(df_best_ranked)
    print 'obs with best offer unranked',len(df_best_unranked)
    df1 = df_best_ranked[df_best_ranked['rank_cross']<df_best_ranked['best offer']]
    df2 = df_best_unranked[df_best_unranked['unranked']==0.0]
    dic_pending['Ranking Strictly Higher than Best Offer']=[len(df1)+len(df2),100.0*float(len(df1)+len(df2))/len(df_both)]
    
    df_worst_ranked = df_both[df_both['worst offer'].notnull()]
    df_worst_unranked = df_both[df_both['worst offer'].isnull()]
    print 'obs with worst offer ranked',len(df_worst_ranked)
    print 'obs with worst offer unranked',len(df_worst_unranked)
    df3 = df_worst_ranked[df_worst_ranked['rank_cross']>df_worst_ranked['worst offer']]
    df4 = df_worst_ranked[df_worst_ranked['rank_cross']==df_worst_ranked['worst offer']]
    dic_pending['Ranking Strictly Lower than Worst Offer'] = [len(df3),100.0*float(len(df3))/len(df_both)]
    
    print dic_pending
    return dic_pending

def export_pending_best_worst_offer(dic_pending):
    lists = [dic_pending['Total Pending Applications']]
    lists.append(dic_pending['Ranking Strictly Higher than Best Offer'])
    lists.append(dic_pending['Ranking Strictly Lower than Worst Offer'])
    df = pd.DataFrame(lists,columns=['Obs','Percent'])
    print df
    
    df_stats_dic = {}
    df_stats_dic['pending_compare_best_worst_offer'] = df
    
    complex_row_col = {
            'pending_compare_best_worst_offer':[['Total Pending Applications','Ranking Strictly Higher than Best Offer',
                                'Ranking Strictly Lower than Worst Offer'],{'':''},
                                ['Obs','Percent']]
            }
    for key, df in df_stats_dic.iteritems():
        df = df.assign(Variable=complex_row_col[key][0]) 
        df = df.rename(columns=complex_row_col[key][1])
        cols = complex_row_col[key][2]
        df = df[cols+['Variable']]
        df2tex(df, '../../model/tables/','{}.tex'.format(key), "%8.2f", 0, cols, ['Variable'], cols)

    return

if __name__ == '__main__':
    df_both = extract_best_worst_offer('df_all_samples_c1')
    dic_pending = compare_pending_best_worst_offer(df_both)
    export_pending_best_worst_offer(dic_pending)
    