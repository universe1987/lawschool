

*------------------------------------------*
*            Logit Top Law Schools         *
*------------------------------------------*

eststo clear
foreach rlt in $result_pending{
	quiet logit `rlt' sent_delta i.year if law_top_14 == 1, robust cluster(user_name) coefl
	estpost margins, dydx(sent_delta)
	eststo `rlt'_1, title(${`rlt'_nm})
	quiet logit `rlt' sent_delta i.year $scores if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_2, title(${`rlt'_nm})
	quiet logit `rlt' sent_delta i.year $scores $urms if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_3, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	quiet logit `rlt' sent_delta i.year $scores $urms $college_type1 if law_top_14 == 1, robust cluster(user_name) 
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_4, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	quiet logit `rlt' sent_delta i.year $scores $urms $college_type1 $major if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_5, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	logit `rlt' sent_delta i.year $scores $urms $college_type1 $major $yrs_out if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_6, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	logit `rlt' sent_delta i.year $scores $urms $college_type1 $major $yrs_out $ec if law_top_14 == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_7, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	estadd local Extracurricular "Yes"

	esttab `rlt'_1 `rlt'_2 `rlt'_3 `rlt'_4 `rlt'_5 `rlt'_6  `rlt'_7 ///
          using "$dir_export/table_`rlt'_top_law_$tail.tex", replace mtitles keep(sent_delta gpa lsat) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")
}



*------------------------------------------*
*            Logit High-Caliber Sample     *
*------------------------------------------*

eststo clear
foreach rlt in $result_pending{
	logit `rlt' sent_delta i.year $law_rank if high_caliber == 1, robust cluster(user_name) 
	estpost margins, dydx(sent_delta)
	eststo `rlt'_1, title(${`rlt'_nm})
	logit `rlt' sent_delta i.year $law_rank $scores if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_2, title(${`rlt'_nm})
	logit `rlt' sent_delta i.year $law_rank $scores $urms if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_3, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	*logit `rlt' sent_delta $law_rank $scores $urms /*college_rank*/ if high_caliber == 1, robust cluster(user_name)  
	*estpost margins, dydx(sent_delta gpa lsat)
	*eststo `rlt'_4, title(${`rlt'_nm})
	*estadd local Gender "Yes"
	*estadd local Race "Yes"
	**estadd local College_Rank "Yes"
	logit `rlt' sent_delta i.year $law_rank $scores $urms /*college_rank*/ $major if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_5, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	*estadd local College_Rank "Yes"
	estadd local College_Major "Yes"
	logit `rlt' sent_delta i.year $law_rank $scores $urms /*college_rank*/ $major $yrs_out if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_6, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	*estadd local College_Rank "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	logit `rlt' sent_delta i.year $law_rank $scores $urms /*college_rank*/ $major $yrs_out $ec if high_caliber == 1, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_7, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	*estadd local College_Rank "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	estadd local Extracurricular "Yes"

	esttab `rlt'_1 `rlt'_2 `rlt'_3 /*`rlt'_4*/ `rlt'_5 `rlt'_6 `rlt'_7  ///
          using "$dir_export/table_`rlt'_high_caliber_$tail.tex", replace mtitles keep(sent_delta gpa lsat) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("Gender" "Race" /*"College_Rank"*/ "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")
}


*------------------------------------------*
*            DID [Different]               *
*------------------------------------------*

eststo clear
foreach rlt in $result_diff_pending{
	reg `rlt' sent_delta_diff $law_rank_diff, robust cluster(user_name) noconstant
	estpost margins, dydx(sent_delta)
	eststo `rlt'_dd, title(${`rlt'_nm})
}

esttab pending_diff_dd ///
       using "$dir_export/table_dd_$tail.tex", replace mtitles keep(sent_delta_diff) ///
       label star(* 0.05 ** 0.01 *** 0.001) ///
	   addnotes("")


*------------------------------------------*
*            Logit                         *
*------------------------------------------*

eststo clear
foreach rlt in $result_pending{
	quiet logit `rlt' sent_delta i.year $law_rank, robust cluster(user_name) coefl
	estpost margins, dydx(sent_delta)
	eststo `rlt'_1, title(${`rlt'_nm})
	quiet logit `rlt' sent_delta i.year $law_rank $scores, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_2, title(${`rlt'_nm})
	quiet logit `rlt' sent_delta i.year $law_rank $scores $urms, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_3, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	quiet logit `rlt' sent_delta i.year $law_rank $scores $urms $college_type1 , robust cluster(user_name) 
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_4, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	quiet logit `rlt' sent_delta i.year $law_rank $scores $urms $college_type1 $major , robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat)
	eststo `rlt'_5, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	logit `rlt' sent_delta i.year $law_rank $scores $urms $college_type1 $major $yrs_out, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_6, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	logit `rlt' sent_delta i.year $law_rank $scores $urms $college_type1 $major $yrs_out $ec, robust cluster(user_name)  
	estpost margins, dydx(sent_delta gpa lsat) 
	eststo `rlt'_7, title(${`rlt'_nm})
	estadd local Gender "Yes"
	estadd local Race "Yes"
	estadd local College_Type "Yes"
	estadd local College_Major "Yes"
	estadd local Yrs_Out_of_College "Yes"
	estadd local Extracurricular "Yes"

	esttab `rlt'_1 `rlt'_2 `rlt'_3 `rlt'_4 `rlt'_5 `rlt'_6  `rlt'_7 ///
          using "$dir_export/table_`rlt'_$tail.tex", replace mtitles keep(sent_delta gpa lsat) ///
     	  label star(* 0.05 ** 0.01 *** 0.001) ///
		  scalars("Gender" "Race" "College_Type" "College_Major" "Yrs_Out_of_College" "Extracurricular") ///
		  addnotes("")
}

