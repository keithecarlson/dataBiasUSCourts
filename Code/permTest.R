library(stm)

#set the random seed so that the results are reproducible
set.seed(12345)

setwd(file.path('..','Data','RData'))

#load the data that has been formatted by preProcessData.R
load(file="preparedData.Rdata")

nRuns<-100
sampleSize <- 50000
nTopics <- 5

#should be 1 if you haven't done any runs yet, otherwise if it failed at some point during running this allows you to be sure you aren't reusing permutations.
#The final column in the output file permTestResults tells you the perm num used for that test.  Set this to a greater number than the final row's value there if it needs to be re-run
startWithPermNum <- 1


#create the output directory
dir.create(file.path('..','..','Results','STMPermutationTest'))

#define a function to run two models, one on real data and one on permuted at judge level data
#it theh appends the results to the csv
runModels <- function(permNumOffset,initWith = 'Spectral'){
	#set the seed fresh each run to be sure that even if we only completed some of the model runs we have the same results as reported
	set.seed(12345 + startWithPermNum + permNumOffset)
	#sample rows and build objects holding only the sampled rows to pass to the STM
	sampleIndices <- sample(NROW(data),sampleSize)
	sampleDocuments <- documents[sampleIndices]
	sampleMeta <- meta[sampleIndices,]

	#calculate true majorityParty
	sampleMeta$majorityParty <-  ( as.character(sampleMeta$party) == "['0', '1', '1']" | as.character(sampleMeta$party) == "['1', '1', '1']" | as.character(sampleMeta$party) == "['1', '0', '1']" | as.character(sampleMeta$party) == "['1', '1', '0']") *1
	
	#calculate permuted majorityParty for this run
	permField <- paste('permutedParty', toString(startWithPermNum-1+permNumOffset),sep='')
	sampleMeta$permMajorityParty <- ( as.character(sampleMeta[,permField]) =="['0', '1', '1']"| as.character(sampleMeta[,permField]) == "['1', '1', '1']" | as.character(sampleMeta[,permField]) == "['1', '0', '1']" | as.character(sampleMeta[,permField]) == "['1', '1', '0']")*1

	#fit the two STMs one on true majorityParty and one on permuted
	mod.out <- stm(sampleDocuments, vocab, nTopics, prevalence=~s(year)+circuit1+circuit2+circuit3+circuit4+circuit5+circuit6+circuit7+circuit8+circuit9+circuit10+circuit11+circuitdc+majorityParty, data=sampleMeta,init.type=initWith)
	permMod.out <- stm(sampleDocuments, vocab, nTopics, prevalence=~s(year)+circuit1+circuit2+circuit3+circuit4+circuit5+circuit6+circuit7+circuit8+circuit9+circuit10+circuit11+circuitdc+permMajorityParty, data=sampleMeta,init.type=initWith)

	#estimate the effects of the meta fields on topic proportions
	prep <- estimateEffect(1:nTopics ~ s(year)+circuit1+circuit2+circuit3+circuit4+circuit5+circuit6+circuit7+circuit8+circuit9+circuit10+circuit11+circuitdc+majorityParty, mod.out,meta=sampleMeta)
	permPrep <- estimateEffect(1:nTopics ~ s(year)+circuit1+circuit2+circuit3+circuit4+circuit5+circuit6+circuit7+circuit8+circuit9+circuit10+circuit11+circuitdc+permMajorityParty, permMod.out,meta=sampleMeta)

	#create a summary of the estimated effects
	prepSum <- summary(prep)
	permPrepSum <- summary(permPrep)
	largestTopicNum <-0
	largestEffect <-0.0
	largestPermTopicNum <-0
	largestPermEffect <-0.0
	#find the topic with the largest estimated effect for the true model and for the permuted model
	for(j in 1:nTopics){
		if (abs(prepSum$tables[[j]]['majorityParty','Estimate']) > largestEffect){
			largestEffect <- abs(prepSum$tables[[j]]['majorityParty','Estimate'])
			largestTopicNum <- j
		}
		if (abs(permPrepSum$tables[[j]]['permMajorityParty','Estimate']) > largestPermEffect){
			largestPermEffect <- abs(permPrepSum$tables[[j]]['permMajorityParty','Estimate'])
			largestPermTopicNum <- j
		}
	}
	#write out the point estimate and CI of the topic with the largest absolute value effect for each prep and permPrep to a file
	line <- paste('majorityParty',toString(prepSum$tables[[largestTopicNum]]['majorityParty',]),toString(startWithPermNum+i-1),sep=',')
	write(line,file=file.path('..','..','Results','STMPermutationTest','permTestResults.csv'),append=TRUE)
	line <- paste('permMajorityParty',toString(permPrepSum$tables[[largestPermTopicNum]]['permMajorityParty',]),toString(startWithPermNum+i-1),sep=',')
	write(line,file=file.path('..','..','Results','STMPermutationTest','permTestResults.csv'),append=TRUE)

}


i<-1
while(i < nRuns+1){
	#sometimes the fitting of the stm fails for a specific seed.  
	#In this case we will try to rerun it using random instead of spectral initialization
	result = tryCatch({
    		runModels(i)
		
		}, error = function(e) {
			print(e)
	    	runModels(i,initWith="Random")
		}, finally = {

		  i<-i+1
		})

}