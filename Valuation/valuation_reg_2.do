use "final_data_valuation_huber_log.dta", clear

sort gvkey qtr

gen qtr_only = quarter(dofq(qtr))
egen predicted_count_std = std(predicted_count)
egen mtb_num_std = std(mtb_num)
egen sales_lag_std = std(sales_lag)
egen profitability_lag_std = std(profitability_lag)
egen leverage_lag_std = std(leverage_lag)

xtset gvkey qtr
* keep company info from 1980 to 2024
keep if qtr >= tq(1980q1) & qtr <= tq(2024q4)

* Drop firms with fewer than 12 time periods
bysort gvkey (qtr): gen obs_per_firm = _N
drop if obs_per_firm < 12

gen log_mtb = log(mtb_num + 1)
gen log_predicted_count = predicted_count_log

* Winsorize log_mtb at 1st and 99th percentiles
winsor2 log_mtb, replace cuts(1 99)
winsor2 log_predicted_count, replace cuts(1 99)

egen log_mtb_std = std(log_mtb)
egen log_predicted_count_std = std(log_predicted_count)

* Declare panel structure
xtset gvkey qtr

* keep companies where are the quarters are present to avoid unbalanced dataset
gen byte tag = !missing(gvkey)
bysort gvkey (qtr): gen byte first = _n == 1
egen actual_qtrs = total(tag), by(gvkey)
egen min_qtr = min(qtr), by(gvkey)
egen max_qtr = max(qtr), by(gvkey)
gen expected_qtrs = max_qtr - min_qtr + 1
keep if actual_qtrs == expected_qtrs

distinct tic

summarize

* fixed_regression
xtreg log_mtb_std c.log_predicted_count_std##i.gsector sales_lag_std profitability_lag_std leverage_lag_std i.qtr_only, fe vce(robust)


*cross-sectional
collapse (mean) mtb_num mtb_num_std predicted_count predicted_count_std sales_lag profitability_lag leverage_lag sales_lag_std profitability_lag_std leverage_lag_std log_mtb log_mtb_std log_predicted_count log_predicted_count_std ///
         (firstnm) tic conml ggroup gind gsector gsubind, by(gvkey)
	 
reg log_mtb_std log_predicted_count_std i.gsector sales_lag_std profitability_lag_std leverage_lag_std, vce(robust)	
	
*event study
gen name_change = (predicted_count_std != predicted_count_std[_n-1]) ///
    if gvkey == gvkey[_n-1]
	
gen name_change = (predicted_count_std != predicted_count_std[_n-1]) ///
    if gvkey == gvkey[_n-1]

gen event_time = .
bysort gvkey (qtr): replace event_time = qtr if name_change == 1
bysort gvkey (event_time): replace event_time = event_time[1] // keep first only
bysort gvkey (qtr): replace event_time = event_time[_n-1] if missing(event_time)

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

xtreg log_mtb_std relm4 relm3 relm2 rel0 rel1 rel2 rel3 rel4 ///
       ///
      sales_lag_std profitability_lag_std leverage_lag_std i.qtr_only, fe vce(robust)
	  

*diff-in-diff
gen treated_1 = !missing(event_time)
label var treated_1 "Firm experienced name change"

gen post = (qtr >= event_time) if treated_1 == 1
replace post = 0 if treated_1 == 0
label var post "Post-event period indicator"

gen did = treated_1 * post
label var did "DiD interaction term"

xtreg log_mtb_std did sales_lag_std profitability_lag_std leverage_lag_std i.qtr_only, fe vce(robust)








