import pandas as pd
import numpy as np
from Registry import Registry
from Application import Application
import __future__
import csv
from df2tex import df2tex

def screen_app_adm():
    df = pd.read_csv('../../data/edit/df_official_lsn.csv')
    print df.columns.tolist()
    print df['LSAT Score'].unique()
    print df['GPA'].unique()
    
     '0.00-2.74' '0.00-2.49' '0.00-2.99'
     '2.00-2.49' '2.50-2.99' 
     
    GPA_cplt1 = ['0.00-1.99','2.00-2.24','2.25-2.49','2.50-2.74','2.75-2.99','3.00-3.24',
                 '3.25-3.49','3.50-3.74','3.75-4.00']
    GPA_cplt2 = ['0.00-2.74']
    GPA_cplt3 = ['0.00-2.49']
    GPA_cplt4 = ['0.00-2.99']
    GPA_cplt5 = ['2.50-2.99']
    
    LSAT_cplt1 = ['120-124','125-129','130-134','135-139','140-144','145-149',
                  '150-154','155-159','160-164','165-169','170-174','175-180']
    LSAT_cplt2 = ['120-153','154-156','157-159','160-162','163-165','166-168','169-180'] # U Washington
    LSAT_cplt3 = ['120-139','140-149','150-159','160-164','165-169','170-174','175-180'] # Boston College
    LSAT_cplt4 = ['120-144','145-149','150-154','155-159','160-164','165-169','170-174','175-180'] # DePaul
    LSAT_cplt5 = ['120-144','145-149','150-154','155-159','160-164','165-169','170-180'] # Syracuse
    LSAT_cplt6 = ['120-144','145-154','155-159','160-164','165-180'] # Loyola Chicago
    LSAT_cplt7 = ['120-149','150-154','155-159','160-164','165-180'] # Maryland
    LSAT_cplt8 = ['120-154','155-159','160-164','165-169','170-174','175-180'] # Yale
    LSAT_cplt9 = ['120-154','155-159','160-164','165-169','170-180'] # Fordham
    LSAT_cplt10 = ['120-139','140-144','145-149','150-154','155-159','160-164','165-169','170-180']  
                   # Temple, Duke(07-11),Houston,Indiana-Indianapolis,U Kansas,Gonzaga (09-11),
                   # Northern Illinois(07), Cincinnati(09),Boston University(10),Cleveland State(11),
                   # Seton Hall(11), Georgia State(11)
                        
                        
    
    return


if __name__ == '__main__':
    screen_app_adm()
    
    
    