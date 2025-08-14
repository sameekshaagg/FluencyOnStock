use "final_data_perform_huber_log.dta", clear
distinct permno

describe

egen size_lag_std = std(size_lag)
egen profitability_lag_std = std(profitability_lag)
egen price_lag_std = std(price_lag)

*cross-sectional
collapse (mean) log_mthret log_mthret_std log_predicted_count log_predicted_count_std mthret mthret_std predicted_count predicted_count_std size_lag_std profitability_lag_std price_lag_std ///
         (firstnm) ticker issuernm ggroup_x gind_x gsector_x, by(permno)
	 
reg mthret_std predicted_count_std profitability_lag_std price_lag_std size_lag_std i.gsector_x, vce(robust)
	 
	 
*fixed Effects
xtreg mthret_std c.predicted_count_std##i.gsector size_lag_std profitability_lag_std price_lag_std i.quarter, fe vce(robust)


*event study
gen name_change = (predicted_count_std != predicted_count_std[_n-1]) ///
    if permno == permno[_n-1]

gen event_time = .
bysort permno (qtr): replace event_time = qtr if name_change == 1
bysort permno (event_time): replace event_time = event_time[1] // keep first only
bysort permno (qtr): replace event_time = event_time[_n-1] if missing(event_time)

gen rel_time = qtr - event_time
gen treated = !missing(event_time)

local reltimes -4 -3 -2 -1 0 1 2 3 4

foreach i of local reltimes {
    if `i' < 0 {
        gen relm`=abs(`i')' = (rel_time == `i') if treated
        replace relm`=abs(`i')' = 0 if missing(relm`=abs(`i')')
    }
    else {
        gen rel`i' = (rel_time == `i') if treated
        replace rel`i' = 0 if missing(rel`i')
    }
}

* Run event study FE regression	  
xtreg mthret_std relm4 relm3 relm2 rel0 rel1 rel2 rel3 rel4 ///
      size_lag_std profitability_lag_std price_lag_std i.quarter, fe vce(robust)
	  
*diff-in-diff
gen treated_1 = !missing(event_time)
label var treated_1 "Firm experienced name change"

gen post = (qtr >= event_time) if treated_1 == 1
replace post = 0 if treated_1 == 0
label var post "Post-event period indicator"

gen did = treated_1 * post
label var did "DiD interaction term"

xtreg mthret_std did size_lag_std profitability_lag_std price_lag_std i.quarter, fe vce(robust)















