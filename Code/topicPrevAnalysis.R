library(stm)

#set the random seed so that the results are reproducible
set.seed(12345)

#create the output directories
dir.create(file.path('..','Results','topicRegressionResults'))
dir.create(file.path('..','Results','Figures'))

#load the model we want to run these regression for
modelName <- '50TopicTrueData'

#load the data which includes the fit of the topic model
load(file=file.path('..','Data','RData',paste(modelName,'.Rdata',sep='')))

#Construct OLSData to hold the relevant info for us to run our regressions on.
OLSData <- list()
OLSData$year.f <- factor(data$year)
OLSData$circuit.f <- factor(data$circuit)
OLSData$majorityParty <- as.integer(meta$majorityParty)

#runs an OLS regression for each topic where topic proportion of a document is predicted by the provided values
#topic proportions are extracted from model, but all other fields need to be present in regData
#the items in regData must be the same as in model, i.e. the first item in regData has the meta information for the first document used for the model
#indVars should be a string like "~ var1 + var2"
#varOfInterest should be one of the variables in indVars that you want the results to be printed for
#writes results to outFileName
topicRegression <- function(regData,model,indVars,varOfInterest,outFileName){
	regResults <- c()
	#find top probability words for each topic for printing out with other info
	topicLabels <- sageLabels(model,n=4)$marginal$prob

	#run the regression for each topic, add topic top words, and estimated effect and CIs and p-values for varOfInterest to our running list of results
	for (i in 1:numTopics){
		regData$topicProp <- model$theta[,i]
		topicLM <- lm(as.formula(paste("topicProp", indVars)), regData)
		CI <- confint(topicLM,varOfInterest,level=0.95)
		pVal <- summary(topicLM)$coefficients[varOfInterest,4]
		regResults <- rbind(regResults,c(toString(topicLabels[i,]),topicLM$coefficients[varOfInterest],CI[1],CI[2],pVal))
	}

	#print the results of the effect of varOfInterest
	colnames(regResults) <- c('TopicWords',paste(varOfInterest,'Effect',sep=' '),'Lower CI','Upper CI','P-Val')
	write.csv(regResults,file=outFileName, quote=TRUE)
}

topicRegression(OLSData,mod.out,"~ majorityParty +circuit.f +year.f","majorityParty",file.path('..','Results','topicRegressionResults',paste(modelName,'topicPrevOLS.csv',sep='')))

#we will also need to use topic prevlance in future figures we create, so output that to a file now as well
#estimated portion each topic makes up of corpus
topics <- 1:mod.out$settings$dim$K
frequency <- colMeans(mod.out$theta[,topics])

write.csv(frequency, file = file.path('..','Results','topicRegressionResults','topicPrevalence.csv'))

#now we will run the same regressions using the permuted model data
#load the model we want to run these regression for
modelName <- '50TopicPermDMP'

#load the data which includes the fit of the topic model
load(file=file.path('..','Data','RData',paste(modelName,'.Rdata',sep='')))

#Construct OLSData to hold the relevant info for us to run our regressions on.
OLSData <- list()
OLSData$year.f <- factor(data$year)
OLSData$circuit.f <- factor(data$circuit)
OLSData$majorityParty <- as.integer(meta$majorityParty)

topicRegression(OLSData,mod.out,"~ majorityParty +circuit.f +year.f","majorityParty",file.path('..','Results','topicRegressionResults',paste(modelName,'topicPrevOLS.csv',sep='')))
