insheet using df_all_lsat_c1.csv,clear
forvalues i = 1/2{
   gen before`i' = sent_delta - actualdelta`i'
}
save df, replace

use df, clear
keep if before1>=0 & before1<=7
count

use df, clear
collapse (min) before1, by(username)
rename before1 before1_min
save df1, replace

use df, clear
collapse (max) before1,by(username)
rename before1 before1_max
save df2, replace

use df1, clear
merge 1:1 username using df2
keep if before1_min>=0 & before1_max<=7
count

local typlist "actual official"
foreach typ in `typlist'{
    forvalues v = 1/2{
        gen before_`typ'`v' = sent_delta - `typ'delta`v'
    }
}
save df_all, replace

local LSAT_1 "LSAT (October)"
local LSAT_2 "LSAT (December)"
foreach typ in `typlist'{
    forvalues v = 1/2{
        use df_all, clear
        collapse (count) sent_delta, by(before_`typ'`v')
		rdrobust sent_delta before_`typ'`v'
	    rdplot sent_delta before_`typ'`v', ci(95) shade ///
			   graph_options(graphregion(fcolor(gs16) lcolor(gs16)) plotregion(lcolor(gs16) margin(zero))  ///
			   legend(off) ///
			   title(`LSAT_`v'', size(large)) ///
			   name(LSAT_`typ'`v',replace) ///
			   xsize(12) ysize(8) graphregion(lcolor(white) lwidth(vthick) margin( 2 4 0 2 ) )  ///
			   xlabel(-200(50)350 , labsize(medlarge)) ///	
			   ylabel(-200(200)800 , labsize(medium)) ///
	           xtick(-200(10)350) ytick(-500(100)900) ///
			   ytitle("Number of Applicants",size(medlarge) margin(medlarge) ) ///
	           xtitle("Days between Application and LSAT score release",size(medlarge) margin(medium)) )   
	}
	graph combine LSAT_`typ'1 LSAT_`typ'2, ///
              cols(1)  scheme(s1color) ysize(20) xsize(15) 
    graph export $dir_graph_export/LSAT_`typ'.eps, replace orientation(landscape) fontface(Times)
			
}
