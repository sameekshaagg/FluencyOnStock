import delimited "Liquidity/trial_check/final_data_liquidity_huber_log.csv", clear

describe

gen qtr = quarterly(datafqtr, "YQ")
format qtr %tq

gen qtr_only = quarter(dofq(qtr))

bysort gvkey qtr (illiq): keep if _n == _N

* creating variables
egen predicted_count_std = std(predicted_count)
gen log_predicted_count = predicted_count_log
egen log_predicted_count_std = std(log_predicted_count)
gen size_num = real(size)
gen illiq_num = real(illiq)
gen liquidity = (1/illiq_num)
gen log_liquidity = log(liquidity + 1)
drop if abs(illiq_num) == .
gen mtb_num = real(market_to_book_ratio)
egen illiq_std = std(illiq_num)
egen vol_std = std(volatility)

egen mtb_std = std(mtb_num)

winsor2 log_predicted_count, replace cuts(1 99)
keep if qtr >= tq(1980q1) & qtr <= tq(2024q4)

* ensure that companies with atleast 3 years data is kept
bysort gvkey: gen n_obs = _N
egen tag = tag(gvkey)
tabulate n_obs if tag == 1
keep if n_obs >= 12
distinct gvkey

xtset gvkey qtr

* ensuring that all the quarter of the company are avaliable to have a balanced dataset
gen byte tag1 = !missing(gvkey)
bysort gvkey (qtr): gen byte first = _n == 1
egen actual_qtrs = total(tag1), by(gvkey)
egen min_qtr = min(qtr), by(gvkey)
egen max_qtr = max(qtr), by(gvkey)
gen expected_qtrs = max_qtr - min_qtr + 1
keep if actual_qtrs == expected_qtrs

distinct tic 

* creating variables
bysort gvkey (qtr): gen size_lag = size_num[_n-1]
bysort gvkey (qtr): gen profitability_lag = profitability[_n-1]
bysort gvkey (qtr): gen mtb_num_lag = mtb_num[_n-1]
bysort gvkey (qtr): gen price_lag = price[_n-1]
bysort gvkey (qtr): gen volatility_lag = vol_std[_n-1]
egen mtb_num_lag_std = std(mtb_num_lag)
egen size_lag_std = std(size_lag)
egen profitability_lag_std = std(profitability_lag)
egen volatility_lag_std = std(volatility_lag)
egen price_lag_std = std(price_lag)
egen liquidity_std = std(liquidity)
egen liquidity_log_std = std(log_liquidity)

save "final_data_liquidity_huber_log.dta", replace




