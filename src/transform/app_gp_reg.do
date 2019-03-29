*==========================================*
*            Early Advantage               *
*==========================================*

*------------------------------------------*
*            Logit: App-Group-Affil        *
*------------------------------------------*

eststo clear
foreach rlt in $result{
	quiet logit `rlt' sent_delta i.year $app_gp $law_rank, robust cluster(user_name) coefl
	estpost margins, dydx(sent_delta $app_gp)
	eststo `rlt'_1, title(${`rlt'_nm})
	quiet logit `rlt' sent_delta i.year $app_gp $law_rank $scores, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat $app_gp)
	eststo `rlt'_2, title(${`rlt'_nm})
	quiet logit `rlt' sent_delta i.year $app_gp $law_rank $scores $urms, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat $app_gp)
	eststo `rlt'_3, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	quiet logit `rlt' sent_delta i.year $app_gp $law_rank $scores $urms $college_type1 , robust cluster(user_name) 
	estpost margins, dydx(sent_delta gpa lsat $app_gp)
	eststo `rlt'_4, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	quiet logit `rlt' sent_delta i.year $app_gp $law_rank $scores $urms $college_type1 $major , robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat $app_gp)
	eststo `rlt'_5, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	logit `rlt' sent_delta i.year $app_gp $law_rank $scores $urms $college_type1 $major $yrs_out, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat $app_gp) 
	eststo `rlt'_6, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	logit `rlt' sent_delta i.year $app_gp $law_rank $scores $urms $college_type1 $major $yrs_out $ec, robust cluster(user_name)  coefl
	estpost margins, dydx(sent_delta gpa lsat $app_gp) 
	eststo `rlt'_7, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	estadd local Extracurricular "Yes"

	esttab `rlt'_1 `rlt'_2 `rlt'_3 `rlt'_4 `rlt'_5 `rlt'_6  `rlt'_7 ///
          using "$dir_export/table_`rlt'_gp_$tail.tex", replace mtitles keep(sent_delta gpa lsat $app_gp) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")
}

*------------------------------------------*
*            DID: App-Group-Affil          *
*------------------------------------------*
eststo clear
foreach rlt in $result_diff{
	reg `rlt' sent_delta_diff $law_rank_diff $app_gp, robust cluster(user_name) noconstant
	estpost margins, dydx(sent_delta $app_gp)
	eststo `rlt'_dd, title(${`rlt'_nm})
}

esttab accepted_diff_dd  rejected_diff_dd ///
       using "$dir_export/table_dd_gp_$tail.tex", replace mtitles keep(sent_delta_diff $app_gp) ///
       label star(* 0.05 ** 0.01 *** 0.001) ///
	   addnotes("")

	   
*------------------------------------------*
*            Group 3: Worse Apps           *
*------------------------------------------*
quiet reg rank_cross  i.year $app_gp, robust cluster(user_name) coefl
estpost margins, dydx( $app_gp)
eststo rank_cross_1, title("Rank")
quiet reg rank_cross  i.year $app_gp $scores, robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_2, title("Rank")
quiet reg rank_cross  i.year $app_gp  $scores $urms, robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_3, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
quiet reg rank_cross  i.year $app_gp  $scores $urms $college_type1 , robust cluster(user_name) 
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_4, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
quiet reg rank_cross  i.year $app_gp  $scores $urms $college_type1 $major , robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_5, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
reg rank_cross  i.year $app_gp  $scores $urms $college_type1 $major $yrs_out, robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp) 
eststo rank_cross_6, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major $yrs_out $ec, robust cluster(user_name)  coefl
estpost margins, dydx( gpa lsat $app_gp) 
eststo rank_cross_7, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
estadd local Extracurricular "Yes"

esttab rank_cross_1 rank_cross_2 rank_cross_3 rank_cross_4 rank_cross_5 rank_cross_6  rank_cross_7 ///
	  using "$dir_export/table_rank_cross_app_gp_$tail.tex", replace mtitles keep( gpa lsat $app_gp) ///
	  label star(* 0.05 ** 0.01 *** 0.001) ///
	  scalars("Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
	  addnotes("")


*----------------------------------------------------*
*            Group 3: Worse Outcomes? No...          *
*----------------------------------------------------*
quiet reg rank_cross i.year  $app_gp  if accepted == 1, robust cluster(user_name) coefl
estpost margins, dydx( $app_gp)
eststo rank_cross_1, title("Rank")
quiet reg rank_cross i.year  $app_gp  $scores if accepted == 1, robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_2, title("Rank")
quiet reg rank_cross i.year  $app_gp  $scores $urms if accepted == 1, robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_3, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
quiet reg rank_cross i.year  $app_gp  $scores $urms $college_type1 if accepted == 1 , robust cluster(user_name) 
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_4, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
quiet reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major  if accepted == 1, robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_5, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major $yrs_out if accepted == 1, robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp) 
eststo rank_cross_6, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major $yrs_out $ec if accepted == 1, robust cluster(user_name)  coefl
estpost margins, dydx( gpa lsat $app_gp) 
eststo rank_cross_7, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
estadd local Extracurricular "Yes"

esttab rank_cross_1 rank_cross_2 rank_cross_3 rank_cross_4 rank_cross_5 rank_cross_6  rank_cross_7 ///
	  using "$dir_export/table_rank_cross_offer_gp_$tail.tex", replace mtitles keep( gpa lsat $app_gp) ///
	  label star(* 0.05 ** 0.01 *** 0.001) ///
	  scalars("Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
	  addnotes("")
	  
*----------------------------------------------------*
*            Group 3: Worse Outcomes? No Again...    *
*----------------------------------------------------*
use ./sample_app_group_affil_new, clear
keep if accepted == 1
collapse (min) rank_cross, by(user_name year $app_gp $scores $urms $college_type1 $major $yrs_out $ec) 

quiet reg rank_cross i.year  $app_gp , robust cluster(user_name) coefl
estpost margins, dydx( $app_gp)
eststo rank_cross_1, title("Rank")
quiet reg rank_cross i.year  $app_gp  $scores , robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_2, title("Rank")
quiet reg rank_cross i.year  $app_gp  $scores $urms , robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_3, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
quiet reg rank_cross i.year  $app_gp  $scores $urms $college_type1 , robust cluster(user_name) 
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_4, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
quiet reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major , robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_5, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major $yrs_out , robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp) 
eststo rank_cross_6, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major $yrs_out $ec , robust cluster(user_name)  coefl
estpost margins, dydx( gpa lsat $app_gp) 
eststo rank_cross_7, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
estadd local Extracurricular "Yes"

esttab rank_cross_1 rank_cross_2 rank_cross_3 rank_cross_4 rank_cross_5 rank_cross_6  rank_cross_7 ///
	  using "$dir_export/table_rank_cross_best_offer_gp_$tail.tex", replace mtitles keep( gpa lsat $app_gp) ///
	  label star(* 0.05 ** 0.01 *** 0.001) ///
	  scalars("Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
	  addnotes("")
	  
*----------------------------------------------------*
*            Group 3: Worse Outcomes? Still No...    *
*----------------------------------------------------*
use ./sample_app_group_affil_new, clear
keep if attend == 1

quiet reg rank_cross i.year  $app_gp , robust cluster(user_name) coefl
estpost margins, dydx( $app_gp)
eststo rank_cross_1, title("Rank")
quiet reg rank_cross i.year  $app_gp  $scores , robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_2, title("Rank")
quiet reg rank_cross i.year  $app_gp  $scores $urms , robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_3, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
quiet reg rank_cross i.year  $app_gp  $scores $urms $college_type1 , robust cluster(user_name) 
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_4, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
quiet reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major , robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp)
eststo rank_cross_5, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major $yrs_out , robust cluster(user_name)  
estpost margins, dydx( gpa lsat $app_gp) 
eststo rank_cross_6, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
reg rank_cross i.year  $app_gp  $scores $urms $college_type1 $major $yrs_out $ec , robust cluster(user_name)  coefl
estpost margins, dydx( gpa lsat $app_gp) 
eststo rank_cross_7, title("Rank")
estadd local Gender "Yes"
estadd local Race "Yes"
estadd local College_Type "Yes"
estadd local College_Major "Yes"
estadd local Yrs_Out_of_College "Yes"
estadd local Extracurricular "Yes"

esttab rank_cross_1 rank_cross_2 rank_cross_3 rank_cross_4 rank_cross_5 rank_cross_6  rank_cross_7 ///
	  using "$dir_export/table_rank_cross_attend_gp_$tail.tex", replace mtitles keep( gpa lsat $app_gp) ///
	  label star(* 0.05 ** 0.01 *** 0.001) ///
	  scalars("Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
	  addnotes("")
