clear
set more off

** First collapse GDP data
** OLD
import delimited "gdp_panel.csv"
collapse (lastnm) year value countrycode, by(countryname)
rename year gdpyear
rename value gdp
rename countryname country
replace country = lower(country)
replace country = "egypt" if country == "egypt, arab rep."
replace country = "iran" if country == "iran, islamic rep."
replace country = "korea" if country == "korea, rep."
replace country = "macedonia" if country == "macedonia, fyr"
replace country = "russia" if country == "russian federation"
save "./gdp_cross.dta", replace
clear

** Now PER CAPITA GDP
import delimited "gdp_capita_panel.csv"
drop item
rename year capitayear
rename countryorarea country
replace country = lower(country)
replace country = "china" if country == "china, people's republic of"
replace country = "iran" if country == "iran, islamic republic of"
replace country = "korea" if country == "republic of korea"
replace country = "macedonia" if country == "the former yugoslav republic of macedonia"
replace country = "russia" if country == "russian federation"
replace country = "slovak republic" if country == "slovakia"
replace country = "tanzania" if country == "united republic of tanzania: mainland"
replace country = "vietnam" if country == "viet nam"
rename value capitagdp
collapse (firstnm) capitayear capitagdp, by(country)
save "./gdp_capita_cross.dta", replace
clear

import delimited "translation.csv"
replace country = lower(country)
merge 1:1 country using "./gdp_cross.dta", keep(master match) nogen
merge 1:1 country using "./gdp_capita_cross.dta"

gen loggdp = log(gdp)
gen logcapitagdp = log(capitagdp)

graph twoway (lfitci logcapitagdp year_of_publication) (scatter logcapitagdp year_of_publication, mlabel(countrycode)), legend(order(1 2)) title("Publication of 'Capital'") ytitle("Log GDP Per Capita, 2018 USD") xtitle("Year of Publication")
