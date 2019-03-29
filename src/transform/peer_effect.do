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
insheet using sample_simulate_outputs_student_d1.csv, clear names
rename median_peer_offer_newly_received median_peer_offer_newly  
rename median_peer_rejection_newly_rece median_peer_rejection_newly
rename best_peer_offer_newly_received best_peer_offer_newly
rename best_peer_rejection_newly_receiv best_peer_rejection_newly
rename median_offer_newly_received median_offer_newly  
rename median_rejection_newly_rece median_rejection_newly
rename best_offer_newly_received best_offer_newly
rename best_rejection_newly_received best_rejection_newly


*==========================================*
*            Create New Vars               *
*==========================================*
local var_c1 lsat gpa
local var_c2 round_number application_time
local var_om1 with_offer with_rejection 
local var_om2 with_offer_newly with_rejection_newly
local var_om3 with_peer_offer with_peer_rejection
local var_om4 with_peer_offer_newly with_peer_rejection_newly
local var_best1 best_offer_c best_rejection_c
local var_best2 best_offer_newly_c best_rejection_newly_c
local var_best3 best_peer_offer_c best_peer_rejection_c
local var_best4 best_peer_offer_newly_c best_peer_rejection_newly_c
local var_median1 median_offer_c median_rejection_c
local var_median2 median_offer_newly_c median_rejection_newly_c
local var_median3 median_peer_offer_c median_peer_rejection_c
local var_median4 median_peer_offer_newly_c median_peer_rejection_newly_c

local outcome_list1 best_offer best_rejection best_peer_offer best_peer_rejection 
local outcome_list2 best_offer_newly best_rejection_newly best_peer_offer_newly best_peer_rejection_newly
local outcome_list3 median_offer median_rejection median_peer_offer median_peer_rejection
local outcome_list4 median_offer_newly median_rejection_newly median_peer_offer_newly median_peer_rejection_newly

forvalues i = 1/2{
foreach item in `outcome_list`i''{
    local item_key = substr("`item'",6,.)
	di "`item_key'"
	local item_nm1 = "with_" + "`item_key'"
	gen `item_nm1' = 0
	replace `item_nm1' = 1 if `item' != .
}
}

forvalues i = 1/4{
foreach item in `outcome_list`i''{
    local item_key = substr("`item'",6,.)
	di "`item_key'"
	sum `item',detail
	local item_nm2 = "`item'" + "_c"
	gen `item_nm2' = `item'
	replace `item_nm2' = 0 if `item' == .
}
}

save peer_effect, replace

*==========================================*
*            Regressions                   *
*==========================================*
use peer_effect, clear
*keep if ranked_only == 1
collapse (max) rank `var_c1'  ///
                  `var_om1' `var_best1' `var_median1' ///
                  `var_om2' `var_best2' `var_median2' ///
		          `var_om3' `var_best3' `var_median3' ///
				  `var_om4' `var_best4' `var_median4', by(user_name application_time round_number)
rename rank rank_max
save peer_effect_max_app, replace

use peer_effect, clear
*keep if ranked_only == 1
collapse (min) rank `var_c1'  ///
                  `var_om1' `var_best1' `var_median1' ///
                  `var_om2' `var_best2' `var_median2' ///
		          `var_om3' `var_best3' `var_median3' ///
				  `var_om4' `var_best4' `var_median4', by(user_name application_time round_number)
rename rank rank_min
save peer_effect_min_app, replace

use peer_effect, clear
*keep if ranked_only == 1
collapse (median) rank `var_c1'  ///
                  `var_om1' `var_best1' `var_median1' ///
                  `var_om2' `var_best2' `var_median2' ///
		          `var_om3' `var_best3' `var_median3' ///
				  `var_om4' `var_best4' `var_median4', by(user_name application_time round_number)
rename rank rank_median
save peer_effect_median_app, replace

use peer_effect_max_app, clear
keep rank_max user_name application_time round_number
merge 1:1 user_name application_time round_number using peer_effect_min_app
drop _merge
save peer_effect_max_min_app, replace

use peer_effect_median_app, clear
keep rank_median user_name application_time round_number
merge 1:1 user_name application_time round_number using peer_effect_max_min_app
drop _merge
save peer_effect_max_min_median_app, replace

use peer_effect_max_min_median_app, clear
gen rank_range = rank_max - rank_min
rename rank_median rank
sort user_name application_time
local lag_list rank round_number application_time
foreach var in `lag_list'{
   di `var'
   local `var'_lag = "`var'"+"_lag"
   by user_name: gen `var'_lag = `var'[_n-1]
   gen `var'_diff = `var' - `var'_lag
}

save peer_effect_diff, replace
use peer_effect_diff, clear
sum rank_diff, detail
reg rank_diff `var_c1' `var_c2' `var_om2' `var_om4' 
                                *`var_best2' `var_median2' `var_best4' `var_median4' 
