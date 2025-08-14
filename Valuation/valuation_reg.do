import delimited "Valuation/trial_check/final_data_valuation_huber_log.csv", clear

gen qtr = quarterly(datafqtr, "YQ")
format qtr %tq

duplicates drop gvkey qtr, force

xtset gvkey qtr

gen sales_num = real(sales)
gen profitability_num = real(profitability)
gen leverage_num = real(leverage)
gen mtb_num = real(market_to_book_ratio)
gen log_mtb = log(mtb_num)

bysort gvkey (qtr): gen sales_lag = sales_num[_n-1]
bysort gvkey (qtr): gen profitability_lag = profitability_num[_n-1]
bysort gvkey (qtr): gen leverage_lag = leverage_num[_n-1]

gen name_changed = conml != conml[_n-1] & gvkey == gvkey[_n-1]

summarize mtb_num predicted_count sales_lag profitability_lag leverage_lag 
describe

drop sales profitability leverage market_to_book_ratio

save "final_data_valuation_huber_log.dta", replace











