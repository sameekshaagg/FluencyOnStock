import delimited "Performance/trial_check/final_data_performance_huber_log.csv", clear

describe

gen size_num = real(size)
gen date = daily(mthcaldt, "DMY")
format date %td
gen month = mofd(date)
format month %tm
gen month_num = month(date)
bysort permno month (mthret): keep if _n == _N
gen log_mthret = log(mthret + 1)
gen log_predicted_count = predicted_count_log


* Winsorize log_mtb at 1st and 99th percentiles
winsor2 log_mthret, replace cuts(1 99)
winsor2 log_predicted_count, replace cuts(1 99)

egen log_mthret_std = std(log_mthret)
egen log_predicted_count_std = std(log_predicted_count)
egen predicted_count_std = std(predicted_count)
egen mthret_std = std(mthret)

* Set panel data structure
xtset permno month

keep if month >= tm(1980m1) & month <= tm(2024m12)
gen qtr = qofd(dofm(month))
format qtr %tq

*coverting monthly data into quarterly data
collapse (mean) log_mthret log_mthret_std log_predicted_count log_predicted_count_std mthret mthret_std predicted_count predicted_count_std size_num profitability price ///
         (firstnm) ticker issuernm ggroup_x gind_x gsector_x, by(permno qtr)

xtset permno qtr

distinct permno

gen quarter = quarter(dofq(qtr))
bysort permno: gen n_obs = _N
egen tag = tag(permno)

*keeping data value that are valid for certain quarter
tabulate n_obs if tag == 1
keep if n_obs >= 12
distinct permno

xtset permno qtr

*keeping company with full quarter data 
gen byte tag1 = !missing(permno)
bysort permno (qtr): gen byte first = _n == 1
egen actual_qtrs = total(tag1), by(permno)

egen min_qtr = min(qtr), by(permno)
egen max_qtr = max(qtr), by(permno)
gen expected_qtrs = max_qtr - min_qtr + 1

keep if actual_qtrs == expected_qtrs

drop if ggroup_x == .

distinct permno

bysort permno (qtr): gen size_lag = size_num[_n-1]
bysort permno (qtr): gen profitability_lag = profitability[_n-1]
bysort permno (qtr): gen price_lag = price[_n-1]

save "final_data_perform_huber_log.dta", replace
