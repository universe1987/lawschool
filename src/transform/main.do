clear all 
clear matrix
capture log close
set more off
set mem 200m
cd "/Users/yuwang/Documents/research/research/lawschool/data/edit"
local dir_export "/Users/yuwang/Documents/research/research/lawschool/model/tables"


*==========================================*
*            Load Data                     *
*==========================================*
insheet using sample_a2.csv, clear names
save ./sample_a2, replace

use ./sample_a2, clear


*==========================================*
*            Create New Vars               *
*==========================================*
sort user_name

local varlist sent_delta law_top_14 law_top_1550 law_below_51 law_unranked accepted rejected
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

*==========================================*
*            Bundle Regressors             *
*==========================================*
local scores gpa lsat
local urms male asian_and_pacific_islander hispanic mixed_probably_not_urm minority /*white */
local college_type1 ranked_nationally ranked_regionally described_positively described_negatively /*described_neutrally*/
local college_type2 national_top_5 national_top_620 national_top_2150 /*national_below_51*/
local major social_sciences arts_humanities business_management /*stem_others*/
local yrs_out var_12_years var_34_years var_59_years var_10_years /*in_undergrad*/
local law_rank law_top_14 law_top_1550 law_below_51 /*law_unranked */
local ec athleticvarsity communityvolunteer greek leadership legal_internship legal_work_experience military nonlegal_work_experience nonlegal_internship overseas strong_letters student_societies
local ec2 athleticvarsity communityvolunteer greek leadership legal_work military non_legal_work overseas strong_letters student_societies
local ec3 athleticvarsity communityvolunteer greek leadership military intern real_work overseas strong_letters student_societies

local result accepted rejected
local accepted_nm "Admitted"
local rejected_nm "Rejected"

local law_rank_diff law_top_14_diff law_top_1550_diff law_below_51_diff law_unranked_diff
local result_diff accepted_diff rejected_diff
local accepted_diff_nm "Admitted"
local rejected_diff_nm "Rejected"

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


*==========================================*
*            Early Advantage               *
*==========================================*

*------------------------------------------*
*            Logit Top Law Schools         *
*------------------------------------------*

eststo clear
foreach rlt in `result'{
	quiet logit `rlt' sent_delta if law_top_14 == 1, robust cluster(user_name) coefl
	estpost margins, dydx(sent_delta)
	eststo `rlt'_1, title(``rlt'_nm')
	quiet logit `rlt' sent_delta `scores' if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_2, title(``rlt'_nm')
	quiet logit `rlt' sent_delta `scores' `urms' if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_3, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	quiet logit `rlt' sent_delta `scores' `urms' `college_type1' if law_top_14 == 1, robust cluster(user_name) 
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_4, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	quiet logit `rlt' sent_delta `scores' `urms' `college_type1' `major' if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_5, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	logit `rlt' sent_delta `scores' `urms' `college_type1' `major' `yrs_out' if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_6, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	logit `rlt' sent_delta `scores' `urms' `college_type1' `major' `yrs_out' `ec' if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_7, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	estadd local Extracurricular "Yes"

	esttab `rlt'_1 `rlt'_2 `rlt'_3 `rlt'_4 `rlt'_5 `rlt'_6  `rlt'_7 ///
          using "`dir_export'/table_`rlt'_top_law.tex", replace mtitles keep(sent_delta gpa lsat) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")
}


stop
*------------------------------------------*
*            Logit High-Caliber Sample     *
*------------------------------------------*

eststo clear
foreach rlt in `result'{
	logit `rlt' sent_delta `law_rank' if high_caliber == 1, robust cluster(user_name) 
	estpost margins, dydx(sent_delta)
	eststo `rlt'_1, title(``rlt'_nm')
	logit `rlt' sent_delta `law_rank' `scores' if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_2, title(``rlt'_nm')
	logit `rlt' sent_delta `law_rank' `scores' `urms' if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_3, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	*logit `rlt' sent_delta `law_rank' `scores' `urms' /*college_rank*/ if high_caliber == 1, robust cluster(user_name)  
	*estpost margins, dydx(sent_delta gpa lsat)
	*eststo `rlt'_4, title(``rlt'_nm')
	*estadd local Gender "Yes"
	*estadd local Race "Yes"
	**estadd local College_Rank "Yes"
	logit `rlt' sent_delta `law_rank' `scores' `urms' /*college_rank*/ `major' if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_5, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	*estadd local College_Rank "Yes"
	estadd local College_Major "Yes"
	logit `rlt' sent_delta `law_rank' `scores' `urms' /*college_rank*/ `major' `yrs_out' if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_6, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	*estadd local College_Rank "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	logit `rlt' sent_delta `law_rank' `scores' `urms' /*college_rank*/ `major' `yrs_out' `ec' if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_7, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	*estadd local College_Rank "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	estadd local Extracurricular "Yes"

	esttab `rlt'_1 `rlt'_2 `rlt'_3 /*`rlt'_4*/ `rlt'_5 `rlt'_6 `rlt'_7  ///
          using "`dir_export'/table_`rlt'_high_caliber.tex", replace mtitles keep(sent_delta gpa lsat) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("Gender" "Race" /*"College_Rank"*/ "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")
}


*------------------------------------------*
*            DID                           *
*------------------------------------------*

eststo clear
foreach rlt in `result_diff'{
	reg `rlt' sent_delta_diff `law_rank_diff', robust cluster(user_name) noconstant
	estpost margins, dydx(sent_delta)
	eststo `rlt'_dd, title(``rlt'_nm')
}

esttab accepted_diff_dd  rejected_diff_dd ///
       using "`dir_export'/table_dd.tex", replace mtitles keep(sent_delta_diff) ///
       label star(* 0.05 ** 0.01 *** 0.001) ///
	   addnotes("")


*------------------------------------------*
*            Logit                         *
*------------------------------------------*

eststo clear
foreach rlt in `result'{
	quiet logit `rlt' sent_delta `law_rank', robust cluster(user_name) coefl
	estpost margins, dydx(sent_delta)
	eststo `rlt'_1, title(``rlt'_nm')
	quiet logit `rlt' sent_delta `law_rank' `scores', robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_2, title(``rlt'_nm')
	quiet logit `rlt' sent_delta `law_rank' `scores' `urms', robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_3, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	quiet logit `rlt' sent_delta `law_rank' `scores' `urms' `college_type1' , robust cluster(user_name) 
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_4, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	quiet logit `rlt' sent_delta `law_rank' `scores' `urms' `college_type1' `major' , robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_5, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	logit `rlt' sent_delta `law_rank' `scores' `urms' `college_type1' `major' `yrs_out', robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_6, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	logit `rlt' sent_delta `law_rank' `scores' `urms' `college_type1' `major' `yrs_out' `ec', robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_7, title(``rlt'_nm')
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	estadd local Extracurricular "Yes"

	esttab `rlt'_1 `rlt'_2 `rlt'_3 `rlt'_4 `rlt'_5 `rlt'_6  `rlt'_7 ///
          using "`dir_export'/table_`rlt'.tex", replace mtitles keep(sent_delta gpa lsat) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")
}



*==========================================*
*         Application Timing               *
*==========================================*	
eststo clear


* Applicants apply to higher-ranking schools earlier
reg sent_delta `law_rank',robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51)
eststo app_rank_1, title("Days")
reg sent_delta `law_rank' `scores' ,robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_2, title("Days")
estadd local GPA_LSAT "Yes"
reg sent_delta `law_rank' `scores' `urms',robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_3, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
reg sent_delta `law_rank' `scores' `urms' `college_type1',robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_4, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
reg sent_delta `law_rank' `scores' `urms' `college_type1' `major',robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_5, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
reg sent_delta `law_rank' `scores' `urms' `college_type1' `major' `yrs_out',robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_6, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
reg sent_delta `law_rank' `scores' `urms' `college_type1' `major' `yrs_out' `ec',robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_7, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
estadd local Extracurricular "Yes"

esttab app_rank_1 app_rank_2 app_rank_3 app_rank_4 app_rank_5 app_rank_6  app_rank_7 ///
          using "`dir_export'/table_app_rank.tex", replace mtitles keep(law_top_14 law_top_1550 law_below_51 lsat gpa) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("GPA_LSAT" "Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")




* Early applicants do not hear back early
reg decision_delta sent_delta `law_rank',robust cluster(user_name)
estpost margins, dydx(sent_delta)
eststo app_decision_1, title("Days")
reg decision_delta sent_delta `law_rank' `scores' ,robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_2, title("Days")
estadd local GPA_LSAT "Yes"
reg decision_delta sent_delta `law_rank' `scores' `urms',robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_3, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
reg decision_delta sent_delta `law_rank' `scores' `urms' `college_type1',robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_4, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
reg decision_delta sent_delta `law_rank' `scores' `urms' `college_type1' `major',robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_5, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
reg decision_delta sent_delta `law_rank' `scores' `urms' `college_type1' `major' `yrs_out',robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_6, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
reg decision_delta sent_delta `law_rank' `scores' `urms' `college_type1' `major' `yrs_out' `ec',robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_7, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
estadd local Extracurricular "Yes"

esttab app_decision_1 app_decision_2 app_decision_3 app_decision_4 app_decision_5 app_decision_6  app_decision_7 ///
          using "`dir_export'/table_app_decision.tex", replace mtitles keep(sent_delta  lsat gpa) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("GPA_LSAT" "Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")


* Applicants are more likely to attend late-applying and late-moving schools
eststo clear
tab attend_reported accepted
logit attend sent_delta decision_delta `law_rank' if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_1, title("Attend")
logit attend sent_delta decision_delta `law_rank' `scores' if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_2, title("Attend")
estadd local GPA_LSAT "Yes"
logit attend sent_delta decision_delta `law_rank' `scores' `urms' if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_3, title("Attend")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
logit attend sent_delta decision_delta `law_rank' `scores' `urms' `college_type1' if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_4, title("Attend")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
logit attend sent_delta decision_delta `law_rank' `scores' `urms' `college_type1' `major' if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_5, title("Attend")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
logit attend sent_delta decision_delta `law_rank' `scores' `urms' `college_type1' `major' `yrs_out' if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_6, title("Attend")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
logit attend sent_delta decision_delta `law_rank' `scores' `urms' `college_type1' `major' `yrs_out' `ec' if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_7, title("Attend")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
estadd local Extracurricular "Yes"

esttab app_attend_1 app_attend_2 app_attend_3 app_attend_4 app_attend_5 app_attend_6  app_attend_7 ///
          using "`dir_export'/table_app_attend.tex", replace mtitles keep(sent_delta decision_delta) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("GPA_LSAT" "Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")




   

   
/*
local dir_export "/Users/yuwang/Documents/research/research/lawschool/model/tables"

insheet using app_clean.csv, clear
eststo clear

* Applicants differ in their unobserved ability. It takes time to prepare application materials.
* Early applicants may be favored by schools.
* Schools desire for early commitments/rejections by candidates so they fill the class better.

* Early applications help, despite of ed and sp
local dir_export "/Users/yuwang/Documents/research/research/lawschool/model/tables"
label var sent_delta "Days to Apply"
label var decision_delta "Days to Outcomes"
label var rank_cross "Ranked\times Ranks"
label var unranked "Unranked"
/*
forvalues yr = 2006/2015{
   di "year = "`yr'
   quiet logit accepted sent_delta i.ed i.sp gpa lsat rank_cross unranked if year == `yr',robust cluster(lawschool)
   estpost margins, dydx(sent_delta gpa lsat)
   eststo accept1_`yr', title("Accepted")
   quiet logit accepted sent_delta i.sp gpa lsat rank_cross unranked if year == `yr' & ed==0 ,robust cluster(lawschool)
   estpost margins, dydx(sent_delta gpa lsat)
   eststo accept2_`yr', title("Accepted")
   quiet logit accepted sent_delta gpa lsat rank_cross unranked if year == `yr' & ed==0 & sp==0,robust cluster(lawschool)
   estpost margins, dydx(sent_delta gpa lsat rank_cross)
   eststo accept3_`yr', title("Accepted")
   quiet logit rejected sent_delta gpa lsat rank_cross unranked if year == `yr' & ed==0 & sp==0,robust cluster(lawschool)
   estpost margins,dydx(sent_delta gpa lsat)
   eststo rejected_`yr', title("Rejected")
   quiet logit waitlisted sent_delta gpa lsat rank_cross unranked if year == `yr' & ed==0 & sp==0,robust cluster(lawschool)
   estpost margins,dydx(sent_delta gpa lsat)
   eststo waitlisted_`yr', title("Waitlisted")
   esttab accept1_`yr' accept2_`yr' accept3_`yr'  rejected_`yr' waitlisted_`yr' ///
          using "`dir_export'/table_accept`yr'.tex", mtitles replace keep(sent_delta gpa lsat) ///
		  label star(* 0.05 ** 0.01 *** 0.001) addnotes("Note: (1) Full sample (2) ED dropped (3)/(4)/(5) ED/SP dropped." "Control Variables: ED,SP,GPA,LSAT,Unranked,Ranked*Rank; Marginal Effects Reported.")
}

*/

set more off
label var decision_delta "Days to Outcomes"
label var rank_cross "Ranked\times Ranks"
label var unranked "Unranked"

local dir_export "/Users/yuwang/Documents/research/research/lawschool/model/tables"
forvalues yr = 2006/2015{
   di "year = " `yr'
   
   * It takes time to prepare application materials
   quiet reg sent_delta gpa lsat rank_cross unranked if year == `yr'&ed==0 & sp==0 ,robust cluster(lawschool)
   estpost margins, dydx(gpa lsat rank_cross unranked) atmeans
   eststo prepare_`yr', title("Days to Apply")
   
   * Early applicants do not hear back early
   quiet reg decision_delta sent_delta gpa lsat rank_cross unranked if year == `yr'&ed==0 & sp==0 ,robust cluster(lawschool)
   estpost margins, dydx(sent_delta gpa lsat rank_cross unranked) atmeans
   eststo decide_`yr', title("Days to Outcomes")
   
   * Early applications do not help with grant 
   quiet logit grantyes sent_delta gpa lsat rank_cross unranked if year == `yr'&ed==0 & sp==0,robust cluster(lawschool)
   estpost margins,dydx(sent_delta gpa lsat)
   eststo grantyes_`yr', title("Grants Given")
   quiet reg grant sent_delta i.ed i.sp gpa lsat rank_cross unranked if year == `yr'&ed==0 & sp==0,robust cluster(lawschool)
   estpost margins,dydx(sent_delta gpa lsat)
   eststo grant_`yr', title("Size of Grants")
   
   
   * "Early" seem to be a welcoming signal in both application and admission
   quiet probit attend sent_delta gpa lsat rank_cross unranked decision_delta if year == `yr'&ed==0 & sp==0 & attendreported ==1 & accepted == 1,robust 
   estpost margins, dydx(sent_delta decision_delta rank_cross unranked)
   eststo attend_`yr', title("Attend")
   
   
   esttab prepare_`yr' decide_`yr' grantyes_`yr' grant_`yr'  attend_`yr'  ///
          using "`dir_export'/table_grant`yr'.tex", mtitles replace keep(sent_delta gpa lsat decision_delta rank_cross unranked) ///
		  label star(* 0.05 ** 0.01 *** 0.001) addnotes("Note: ED/SP dropped. Control Variables: GPA,LSAT,Unranked,Ranked*Rank; Marginal Effects Reported.")
   
}








