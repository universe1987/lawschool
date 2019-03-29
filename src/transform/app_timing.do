

*==========================================*
*         Application Timing               *
*==========================================*	
eststo clear


* Applicants apply to higher-ranking schools earlier
reg sent_delta $law_rank,robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51)
eststo app_rank_1, title("Days")
reg sent_delta $law_rank $scores ,robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_2, title("Days")
estadd local GPA_LSAT "Yes"
reg sent_delta $law_rank $scores $urms,robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_3, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
reg sent_delta $law_rank $scores $urms $college_type1,robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_4, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
reg sent_delta $law_rank $scores $urms $college_type1 $major,robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_5, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
reg sent_delta $law_rank $scores $urms $college_type1 $major $yrs_out,robust cluster(user_name) 
estpost margins, dydx(law_top_14 law_top_1550 law_below_51 lsat gpa)
eststo app_rank_6, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
reg sent_delta $law_rank $scores $urms $college_type1 $major $yrs_out $ec,robust cluster(user_name) 
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
          using "$dir_export/table_app_rank_$tail.tex", replace mtitles keep(law_top_14 law_top_1550 law_below_51 lsat gpa) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("GPA_LSAT" "Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")




* Early applicants do not hear back early
reg decision_delta sent_delta $law_rank,robust cluster(user_name)
estpost margins, dydx(sent_delta)
eststo app_decision_1, title("Days")
reg decision_delta sent_delta $law_rank $scores ,robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_2, title("Days")
estadd local GPA_LSAT "Yes"
reg decision_delta sent_delta $law_rank $scores $urms,robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_3, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
reg decision_delta sent_delta $law_rank $scores $urms $college_type1,robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_4, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
reg decision_delta sent_delta $law_rank $scores $urms $college_type1 $major,robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_5, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
reg decision_delta sent_delta $law_rank $scores $urms $college_type1 $major $yrs_out,robust cluster(user_name) 
estpost margins, dydx(sent_delta gpa lsat)
eststo app_decision_6, title("Days")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
reg decision_delta sent_delta $law_rank $scores $urms $college_type1 $major $yrs_out $ec,robust cluster(user_name) 
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
          using "$dir_export/table_app_decision_$tail.tex", replace mtitles keep(sent_delta  lsat gpa) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("GPA_LSAT" "Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")


* Applicants are more likely to attend late-applying and late-moving schools
eststo clear
tab attend_reported accepted
logit attend sent_delta decision_delta $law_rank if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_1, title("Attend")
logit attend sent_delta decision_delta $law_rank $scores if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_2, title("Attend")
estadd local GPA_LSAT "Yes"
logit attend sent_delta decision_delta $law_rank $scores $urms if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_3, title("Attend")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
logit attend sent_delta decision_delta $law_rank $scores $urms $college_type1 if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_4, title("Attend")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
logit attend sent_delta decision_delta $law_rank $scores $urms $college_type1 $major if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_5, title("Attend")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
logit attend sent_delta decision_delta $law_rank $scores $urms $college_type1 $major $yrs_out if attend_reported ==1 & accepted == 1,robust cluster(user_name)
estpost margins, dydx(sent_delta decision_delta)
eststo app_attend_6, title("Attend")
estadd local GPA_LSAT "Yes"
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
logit attend sent_delta decision_delta $law_rank $scores $urms $college_type1 $major $yrs_out $ec if attend_reported ==1 & accepted == 1,robust cluster(user_name)
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
          using "$dir_export/table_app_attend_$tail.tex", replace mtitles keep(sent_delta decision_delta) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("GPA_LSAT" "Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")
