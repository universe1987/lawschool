clear all 
clear matrix
capture log close
set more off
set mem 200m
cd "/Users/yuwang/Documents/research/research/lawschool/data/edit"
global dir_export "/Users/yuwang/Documents/research/research/lawschool/model/tables"
global dir_graph_export "/Users/yuwang/Documents/research/research/lawschool/model/graphs"
global src "/Users/yuwang/Documents/research/research/lawschool/src/transform"

*==========================================*
*            Load Data                     *
*==========================================*
insheet using sample_a2.csv, clear names
save ./sample_a2, replace


insheet using simulate_outputs_student_d1.csv, clear names
gen gp = applicanttype
collapse (mean) totalrounds, by(username gp)
tab gp
forvalues i=1/3{
    replace gp = "`i'" if gp=="Group `i'"
}
destring gp, replace
rename username user_name
merge 1:m user_name using ./sample_a2
keep if _merge==3
drop _merge

/*insheet using sample_app_group_affil.csv, clear names
count
count if gp <=4
count if gp ==.*/
save ./sample_app_group_affil, replace


*==========================================*
*            Create New Vars               *
*==========================================*
use ./sample_a2, clear
do $src/create_new_var.do
do $src/bundle_regressors.do
save ./sample_a2_new, replace

use ./sample_a2, clear
replace sent_delta = sent_delta - opening_dates_delta
do $src/create_new_var.do
do $src/bundle_regressors.do
save ./sample_a2_actual, replace

use ./sample_app_group_affil, clear
do $src/create_new_var.do
save ./sample_app_group_affil_new, replace

use ./sample_a2, clear
replace accepted = 1 if pending == 1 
do $src/create_new_var.do
do $src/bundle_regressors.do
save ./sample_a2_new_pending_offer, replace

use ./sample_a2, clear
replace sent_delta = sent_delta - opening_dates_delta
replace accepted = 1 if pending == 1 
do $src/create_new_var.do
do $src/bundle_regressors.do
save ./sample_a2_actual_pending_offer, replace



*=====*=====*=====*=====*=====*=====*=====*=====*=====*
*               Common Regressions                    *
*=====*=====*=====*=====*=====*=====*=====*=====*=====*

use ./sample_a2_actual, clear
global tail a2_actual
do $src/common_reg.do
do $src/app_timing.do


use ./sample_app_group_affil_new, clear
sum $app_gp
global tail app_gp
do $src/common_reg.do


use ./sample_a2_new, clear
global tail a2_pending
do $src/common_reg_pending.do


use ./sample_a2_new, clear
keep if pending == 0
global tail a2_nopending
do $src/common_reg.do


use ./sample_a2_new_pending_offer, clear
global tail a2_pending_offer
do $src/common_reg.do

use ./sample_a2_actual_pending_offer, clear
global tail a2_actual_pending_offer
do $src/common_reg.do


use ./sample_a2_new, clear
global tail a2
do $src/common_reg.do
do $src/app_timing.do




*=====*=====*=====*=====*=====*=====*=====*=====*=====*
*               Pending Comparison                    *
*=====*=====*=====*=====*=====*=====*=====*=====*=====*
use ./sample_a2_new, clear
ttest sent_delta, by(pending)
ttest rank_cross, by(pending)



*=====*=====*=====*=====*=====*=====*=====*=====*=====*
*                App Group Regressions                *
*=====*=====*=====*=====*=====*=====*=====*=====*=====*
use ./sample_app_group_affil_new, clear
global tail app_gp
do $src/app_gp_reg.do

use ./sample_app_group_affil_new, clear
forvalues i = 1/4{
   sum accepted if gp == `i'
}

*=====*=====*=====*=====*=====*=====*=====*=====*=====*
*                App Group Statistics                 *
*=====*=====*=====*=====*=====*=====*=====*=====*=====*

use ./sample_app_group_affil_new, clear
collapse (count) lsat, by(year gp)
rename lsat obs
save ./collapse1, replace

collapse (sum) obs, by(year)
rename obs obs_total
merge 1:m year using ./collapse1

gen pct = obs / obs_total * 100.0
sort gp year
keep pct year gp
reshape wide pct, i(year) j(gp)
twoway (connected pct1 year) (connected pct2 year) (connected pct3 year) (connected pct4 year)

*==========================================*
*            LSAT score release            *
*==========================================*
do LSAT_release.do

*==========================================*
*            Peer Effect                   *
*==========================================*
do peer_effect.do
insheet using simulate_outputs_student_d1.csv, clear names
local rank_list rank bestoffer worstoffer bestrejection worstrejection bestpeeroffer bestpeerrejection
foreach var in `rank_list'{
   replace `var' = "" if `var' == "nan"
   destring `var',replace
   sum `var',detail
}
reg rank lsat gpa bestoffer worstoffer bestrejection worstrejection bestpeeroffer bestpeerrejection
