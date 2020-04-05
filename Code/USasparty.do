  
clear

import delimited "lustrumDemCountDataAllCircuits.csv"

encode circuit, g(cir)

gen time = year - 1969

gen timesq = time^2

gen US = 0

replace US = 1 if usparty == "TRUE"

* Table 4, Aggregate Effects from Judge Affiliation on United States as a Party 

logit US dem, vce(r) 

logit US dem if year > 1989, vce(r) 

logit US dem i.time i.cir, vce(r)

logit US dem i.time i.cir if year > 1989, vce(r)

logit US dem i.cir time timesq i.cir#c.time i.cir#c.timesq, vce(r)

logit US dem i.cir time timesq i.cir#c.time i.cir#c.timesq if year > 1989, vce(r)

logit US dem i.lust##i.cir, vce(r)

logit US dem i.lust##i.cir if year > 1989, vce(r)

	
* Table 5, Alternative Specification  


logit US i.dem, vce(r) 

logit US i.dem if year > 1989, vce(r) 

logit US i.dem i.time i.cir, vce(r)

logit US i.dem i.time i.cir if year > 1989, vce(r)

logit US i.dem i.cir time timesq i.cir#c.time i.cir#c.timesq, vce(r)

logit US i.dem i.cir time timesq i.cir#c.time i.cir#c.timesq if year > 1989, vce(r)

logit US i.dem i.lust##i.cir, vce(r)

logit US i.dem i.lust##i.cir if year > 1989, vce(r)



