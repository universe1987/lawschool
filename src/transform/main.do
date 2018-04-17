clear all 
clear matrix
capture log close
set more off
set mem 200m
cd "/Users/yuwang/Documents/research/research/lawschool/data/edit"

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








