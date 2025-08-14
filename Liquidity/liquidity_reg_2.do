use "final_data_liquidity_huber_log.dta", clear

* Set panel data structure
xtset gvkey qtr

corr liquidity_log_std size_lag_std profitability_lag_std mtb_num_lag_std price_lag_std volatility_lag_std log_predicted_count_std 

*fixed_effect model
xtreg liquidity_log_std c.log_predicted_count_std##i.gsector size_lag_std profitability_lag_std mtb_num_lag_std price_lag_std volatility_lag_std i.qtr_only, fe vce(robust)

*cross-sectional
collapse (mean) log_liquidity liquidity_log_std predicted_count_std log_predicted_count log_predicted_count_std profitability_lag_std mtb_num_lag_std price_lag_std volatility_lag_std ///
         (firstnm) tic conml ggroup gind gsector, by(gvkey)
 
reg liquidity_log_std log_predicted_count_std profitability_lag_std mtb_num_lag_std price_lag_std volatility_lag_std i.gsector, vce(robust)


*event study
gen name_change = (predicted_count_std != predicted_count_std[_n-1]) ///
    if gvkey == gvkey[_n-1]
	
gen event_time = .
bysort gvkey (qtr): replace event_time = qtr if name_change == 1
bysort gvkey (event_time): replace event_time = event_time[1] 
bysort gvkey (qtr): replace event_time = event_time[_n-1] if missing(event_time)

gen rel_time = qtr - event_time
summarize rel_time
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
xtreg liquidity_log_std relm4 relm3 relm2 rel0 rel1 rel2 rel3 rel4 ///
	  profitability_lag_std mtb_num_lag_std price_lag_std volatility_lag_std i.qtr_only, fe vce(robust)
	  
*diff-in-diff
gen treated_1 = !missing(event_time)
label var treated_1 "Firm experienced name change"

gen post = (qtr >= event_time) if treated_1 == 1
replace post = 0 if treated_1 == 0
label var post "Post-event period indicator"

gen did = treated_1 * post
label var did "DiD interaction term"

xtreg liquidity_log_std did profitability_lag_std mtb_num_lag_std price_lag_std volatility_lag_std i.qtr_only, fe vce(robust)
