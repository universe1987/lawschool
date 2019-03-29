clear all 
clear matrix
capture log close
set more off
set mem 200m
cd "/Users/yuwang/Documents/research/research/lawschool/data/edit"
local dir_export "/Users/yuwang/Documents/research/research/lawschool/model/tables"


insheet using df_official_lsn.csv
gen idd = _n
gen app_pct_diff = abs(app_pct - app_pct_lsn)
sum app_pct_diff if app_pct>0, detail
sum app_pct if app_pct >0, detail
scatter app_pct_diff app_pct if app_pct>0

see
*==========================================*
*            Load Data                     *
*==========================================*
insheet using school_dx.csv, clear names
bysort lawschool: egen mods = mode(sent_delta), minmode
keep if lawschool == "Northeastern University" | lawschool == "University of Connecticut"
ksmirnov sent_delta, by(lawschool)
kdensity sent_delta if lawschool == "Northeastern University", ///
plot (kdensity sent_delta if lawschool == "University of Connecticut") 
see


keep if lawschool == "Harvard University" | lawschool == "University of Virginia"
ksmirnov sent_delta, by(lawschool)
kdensity sent_delta if lawschool == "Harvard University", ///
plot (kdensity sent_delta if lawschool == "University of Virginia") 

see
bysort lawschool: egen mods = mode(sent_delta), minmode
keep if lawschool == "Columbia University"
hist sent_delta if sent_delta<=150
collapse mods, by(lawschool)
list
see


insheet using representative_app_date.csv, clear names
ttest lsn==official
twoway (connected lsn index) (connected official index)
see

*==========================================*
*            Load Data                     *
*==========================================*
insheet using representative_apps_adm.csv, clear names
see

*==========================================*
*            Good T-test                   *
*==========================================*
ttest app_pct = app_pct_lsn
gen diff = app_pct_lsn - app_pct
ttest diff == 0


ttest adm2_pct = adm2_pct_lsn



*==========================================*
*            Bad T-test                    *
*==========================================*
ttest adm1_pct = adm1_pct_lsn
ttest select_pct = select_pct_lsn
