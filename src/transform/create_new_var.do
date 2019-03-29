*==========================================*
*            Create New Vars               *
*==========================================*
sort user_name

local varlist sent_delta law_top_14 law_top_1550 law_below_51 law_unranked accepted rejected pending
foreach var in `varlist'{
   bysort user_name: egen `var'_avg= mean(`var')
   gen `var'_diff = `var' - `var'_avg
   sum `var'_avg `var'_diff, detail
}

gen high_caliber = national_top_5 + national_top_620 /* + national_top_2150*/
replace high_caliber = 1 if high_caliber > 1 & high_caliber!=.
tab high_caliber


gen legal_work = legal_internship+legal_work_experience
replace legal_work = 1 if legal_work>1&legal_work!=.

gen non_legal_work = nonlegal_work_experience + nonlegal_internship
replace non_legal_work = 1 if non_legal_work>1&non_legal_work!=.

gen intern = legal_internship + nonlegal_internship
replace intern = 1 if intern>1 & intern!=.

gen real_work = legal_work_experience + nonlegal_work_experience
replace real_work = 1 if real_work>1 & real_work!=.

forvalues i = 1(1)4{
   gen app_gp`i' = .
   replace app_gp`i' = 1 if gp==`i'
   replace app_gp`i' = 0 if gp!=`i' & gp!=.
}

*==========================================*
*            Quick Check                   *
*==========================================*
gen yrs_out = var_12_years + var_34_years + var_59_years + var_10_years + in_undergrad
gen yrs_out_cat = .
replace yrs_out_cat = 0 if in_undergrad == 1
replace yrs_out_cat = 1 if var_12_years == 1
replace yrs_out_cat = 2 if var_34_years == 1
replace yrs_out_cat = 3 if var_59_years == 1
replace yrs_out_cat = 4 if var_10_years == 1
/*
keep if yrs_out!=.
sum `yrs_out' in_undergrad
gen work = legal_work + nonlegal_work
sum legal_work if in_undergrad == 0.0
sum nonlegal_work  if in_undergrad == 0.0
tab work yrs_out_cat,cell nofreq
*/

*==========================================*
*            Label Variables               *
*==========================================*

label var sent_delta "Days to Submission"
label var decision_delta "Days to Decisions"
label var gpa "GPA"
label var lsat "LSAT"
label var law_top_14 "Top 14"
label var law_top_1550 "Top 15-50"
label var law_below_51 "Top 51-100"
label var sent_delta_diff "Days to Submission"
label var accepted_diff "Admitted"
label var rejected_diff "Rejected"
label var app_gp1 "Group 1"
label var app_gp2 "Group 2"
label var app_gp3 "Group 3"
label var app_gp4 "Group 4"


