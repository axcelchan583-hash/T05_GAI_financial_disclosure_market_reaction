clear all
set more off

local root "/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction"
local out "`root'/results/v23_qian_supplier_replication_20260602"

capture log close
log using "`out'/stata_qian_supplier_replication_check.log", replace text

import delimited using "`out'/analysis_sample_first_valid_events_for_stata.csv", clear varnames(1) encoding("utf-8")

destring ar_m1_mm ar_0_mm ar_p1_mm car_0_p1_mm car_m1_p1_mm, replace force

display "Qian-style supplier replication Stata check"
display "Main sample: first_valid_events"
tab relation

foreach rel in upstream_supplier downstream_customer {
    display "=================================================="
    display "Relation: `rel'"
    foreach var in ar_m1_mm ar_0_mm ar_p1_mm car_0_p1_mm car_m1_p1_mm {
        display "Outcome: `var'"
        summarize `var' if relation == "`rel'", detail
        ttest `var' == 0 if relation == "`rel'"
    }
}

tempname handle
postfile `handle' str30 relation str20 outcome double n mean se t p median positive_rate using "`out'/stata_check_summary.dta", replace

foreach rel in upstream_supplier downstream_customer {
    foreach var in ar_m1_mm ar_0_mm ar_p1_mm car_0_p1_mm car_m1_p1_mm {
        quietly summarize `var' if relation == "`rel'", detail
        scalar n = r(N)
        scalar mean = r(mean)
        scalar median = r(p50)
        scalar se = .
        scalar t = .
        scalar p = .
        if n > 1 & r(sd) > 0 {
            scalar se = r(sd) / sqrt(n)
            scalar t = mean / se
            scalar p = 2 * ttail(n - 1, abs(t))
        }
        tempvar positive
        quietly generate byte `positive' = (`var' > 0) if relation == "`rel'" & !missing(`var')
        quietly summarize `positive' if relation == "`rel'" & !missing(`var'), meanonly
        scalar positive_rate = r(mean)
        post `handle' ("`rel'") ("`var'") (n) (mean) (se) (t) (p) (median) (positive_rate)
        drop `positive'
    }
}
postclose `handle'

use "`out'/stata_check_summary.dta", clear
export delimited using "`out'/stata_check_summary.csv", replace
list, abbreviate(20)

log close
