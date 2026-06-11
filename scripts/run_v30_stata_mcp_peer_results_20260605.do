version 17
clear all
set more off

local root "/Users/mac/computerscience/23实证选题探索/T05_GAI_financial_disclosure_market_reaction"
local v29 "`root'/results/v29_pom_style_peer_results_20260605"
local out "`root'/results/v30_stata_mcp_peer_results_20260605"
cap mkdir "`out'"

log using "`out'/stata_v30.log", text replace

display "v30 Stata-MCP audit for POM-style peer results"
display "Input folder: `v29'"

capture which reghdfe
if _rc {
    display as error "reghdfe is not installed."
    exit 199
}
capture which ivreg2
if _rc {
    display as error "ivreg2 is not installed."
    exit 199
}

capture program drop collect_coef_scalars
program define collect_coef_scalars
    foreach v in spec_ai ai peer_rank peer_similarity peer_car_pre10_m2_mm peer_car_pre20_m2_mm {
        capture scalar b_`v' = _b[`v']
        if _rc scalar b_`v' = .
        capture scalar se_`v' = _se[`v']
        if _rc scalar se_`v' = .
        scalar p_`v' = .
        if !missing(b_`v') & !missing(se_`v') & se_`v' > 0 {
            scalar p_`v' = 2 * normal(-abs(b_`v' / se_`v'))
        }
    }
end

display ""
display "=============================="
display "Table 2 audit: event study"
display "=============================="

import delimited using "`v29'/analysis_sample_used_in_table2.csv", clear varnames(1) encoding("utf-8")
egen event_fe = group(event_key)
egen peer_fe = group(peer_code)
gen one = 1

tempname t2
postfile `t2' str20 outcome double nobs mean se z p median wilcoxon_z wilcoxon_p positive_share sign_z sign_p using "`out'/stata_table2_raw.dta", replace

foreach y in peer_ar_m1_mm peer_ar0_mm peer_ar_p1_mm {
    quietly count if !missing(`y')
    local nobs = r(N)
    quietly ivreg2 `y' one if !missing(`y'), nocons cluster(event_fe peer_fe)
    local mean = _b[one]
    local se = _se[one]
    local z = `mean' / `se'
    local p = 2 * normal(-abs(`z'))
    quietly summarize `y' if !missing(`y'), detail
    local median = r(p50)
    quietly signrank `y' = 0 if !missing(`y')
    local wz = r(z)
    local wp = r(p)
    quietly signtest `y' = 0 if !missing(`y')
    local positive = r(N_pos)
    local pos_share = `positive' / `nobs'
    local sz = (`positive' - 0.5 * `nobs') / sqrt(0.25 * `nobs')
    local sp = 2 * normal(-abs(`sz'))
    post `t2' ("`y'") (`nobs') (`mean') (`se') (`z') (`p') (`median') (`wz') (`wp') (`pos_share') (`sz') (`sp')
}
postclose `t2'

use "`out'/stata_table2_raw.dta", clear
export delimited using "`out'/stata_table2_raw.csv", replace
list, noobs clean

display ""
display "======================================"
display "Table 3 audit: cross-sectional models"
display "======================================"

import delimited using "`v29'/analysis_sample_used_in_table3.csv", clear varnames(1) encoding("utf-8")
egen event_fe = group(event_key)
egen peer_fe = group(peer_code)
egen indweek_fe = group(peer_industry_week)

local rhs ai spec_ai peer_rank peer_similarity peer_car_pre10_m2_mm peer_car_pre20_m2_mm

tempname t3
postfile `t3' str4 col str20 dep str32 fe double nobs events peers ///
    b_spec_ai se_spec_ai p_spec_ai ///
    b_ai se_ai p_ai ///
    b_peer_rank se_peer_rank p_peer_rank ///
    b_peer_similarity se_peer_similarity p_peer_similarity ///
    b_peer_car_pre10_m2_mm se_peer_car_pre10_m2_mm p_peer_car_pre10_m2_mm ///
    b_peer_car_pre20_m2_mm se_peer_car_pre20_m2_mm p_peer_car_pre20_m2_mm ///
    overall_r2 within_r2 using "`out'/stata_table3_raw.dta", replace

quietly reghdfe peer_ar0_mm `rhs', absorb(event_fe) keepsingletons vce(cluster event_fe peer_fe)
collect_coef_scalars
post `t3' ("(1)") ("PeerAR[0]") ("Event FE") (e(N)) (e(N_clust1)) (e(N_clust2)) ///
    (b_spec_ai) (se_spec_ai) (p_spec_ai) ///
    (b_ai) (se_ai) (p_ai) ///
    (b_peer_rank) (se_peer_rank) (p_peer_rank) ///
    (b_peer_similarity) (se_peer_similarity) (p_peer_similarity) ///
    (b_peer_car_pre10_m2_mm) (se_peer_car_pre10_m2_mm) (p_peer_car_pre10_m2_mm) ///
    (b_peer_car_pre20_m2_mm) (se_peer_car_pre20_m2_mm) (p_peer_car_pre20_m2_mm) ///
    (e(r2)) (e(r2_within))

quietly reghdfe peer_ar0_mm `rhs', absorb(event_fe indweek_fe) keepsingletons vce(cluster event_fe peer_fe)
collect_coef_scalars
post `t3' ("(2)") ("PeerAR[0]") ("Event+IndustryWeek FE") (e(N)) (e(N_clust1)) (e(N_clust2)) ///
    (b_spec_ai) (se_spec_ai) (p_spec_ai) ///
    (b_ai) (se_ai) (p_ai) ///
    (b_peer_rank) (se_peer_rank) (p_peer_rank) ///
    (b_peer_similarity) (se_peer_similarity) (p_peer_similarity) ///
    (b_peer_car_pre10_m2_mm) (se_peer_car_pre10_m2_mm) (p_peer_car_pre10_m2_mm) ///
    (b_peer_car_pre20_m2_mm) (se_peer_car_pre20_m2_mm) (p_peer_car_pre20_m2_mm) ///
    (e(r2)) (e(r2_within))

quietly reghdfe peer_ar0_mm `rhs', absorb(event_fe peer_fe) keepsingletons vce(cluster event_fe peer_fe)
collect_coef_scalars
post `t3' ("(3)") ("PeerAR[0]") ("Event+PeerFirm FE") (e(N)) (e(N_clust1)) (e(N_clust2)) ///
    (b_spec_ai) (se_spec_ai) (p_spec_ai) ///
    (b_ai) (se_ai) (p_ai) ///
    (b_peer_rank) (se_peer_rank) (p_peer_rank) ///
    (b_peer_similarity) (se_peer_similarity) (p_peer_similarity) ///
    (b_peer_car_pre10_m2_mm) (se_peer_car_pre10_m2_mm) (p_peer_car_pre10_m2_mm) ///
    (b_peer_car_pre20_m2_mm) (se_peer_car_pre20_m2_mm) (p_peer_car_pre20_m2_mm) ///
    (e(r2)) (e(r2_within))

quietly reghdfe peer_car_0_p1_mm `rhs', absorb(event_fe) keepsingletons vce(cluster event_fe peer_fe)
collect_coef_scalars
post `t3' ("(4)") ("PeerCAR[0,+1]") ("Event FE") (e(N)) (e(N_clust1)) (e(N_clust2)) ///
    (b_spec_ai) (se_spec_ai) (p_spec_ai) ///
    (b_ai) (se_ai) (p_ai) ///
    (b_peer_rank) (se_peer_rank) (p_peer_rank) ///
    (b_peer_similarity) (se_peer_similarity) (p_peer_similarity) ///
    (b_peer_car_pre10_m2_mm) (se_peer_car_pre10_m2_mm) (p_peer_car_pre10_m2_mm) ///
    (b_peer_car_pre20_m2_mm) (se_peer_car_pre20_m2_mm) (p_peer_car_pre20_m2_mm) ///
    (e(r2)) (e(r2_within))

quietly reghdfe peer_car_0_p1_mm `rhs', absorb(event_fe indweek_fe) keepsingletons vce(cluster event_fe peer_fe)
collect_coef_scalars
post `t3' ("(5)") ("PeerCAR[0,+1]") ("Event+IndustryWeek FE") (e(N)) (e(N_clust1)) (e(N_clust2)) ///
    (b_spec_ai) (se_spec_ai) (p_spec_ai) ///
    (b_ai) (se_ai) (p_ai) ///
    (b_peer_rank) (se_peer_rank) (p_peer_rank) ///
    (b_peer_similarity) (se_peer_similarity) (p_peer_similarity) ///
    (b_peer_car_pre10_m2_mm) (se_peer_car_pre10_m2_mm) (p_peer_car_pre10_m2_mm) ///
    (b_peer_car_pre20_m2_mm) (se_peer_car_pre20_m2_mm) (p_peer_car_pre20_m2_mm) ///
    (e(r2)) (e(r2_within))

quietly reghdfe peer_car_0_p1_mm `rhs', absorb(event_fe peer_fe) keepsingletons vce(cluster event_fe peer_fe)
collect_coef_scalars
post `t3' ("(6)") ("PeerCAR[0,+1]") ("Event+PeerFirm FE") (e(N)) (e(N_clust1)) (e(N_clust2)) ///
    (b_spec_ai) (se_spec_ai) (p_spec_ai) ///
    (b_ai) (se_ai) (p_ai) ///
    (b_peer_rank) (se_peer_rank) (p_peer_rank) ///
    (b_peer_similarity) (se_peer_similarity) (p_peer_similarity) ///
    (b_peer_car_pre10_m2_mm) (se_peer_car_pre10_m2_mm) (p_peer_car_pre10_m2_mm) ///
    (b_peer_car_pre20_m2_mm) (se_peer_car_pre20_m2_mm) (p_peer_car_pre20_m2_mm) ///
    (e(r2)) (e(r2_within))

postclose `t3'

use "`out'/stata_table3_raw.dta", clear
export delimited using "`out'/stata_table3_raw.csv", replace
format b_* se_* p_* overall_r2 within_r2 %10.6f
list col dep fe nobs events peers b_spec_ai se_spec_ai p_spec_ai overall_r2 within_r2, noobs clean

display ""
display "Stata audit outputs:"
display "`out'/stata_table2_raw.csv"
display "`out'/stata_table3_raw.csv"
display "`out'/stata_v30.log"

log close
