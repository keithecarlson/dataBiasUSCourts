library(stm)

#this script looks at each document and its topic prevalences and outputs the average topic share of the most 
#prevalent topic in a document, the 2nd most...to the 5th most

modelName <- '50TopicTrueData'

#load the data which includes the fit of the topic model
load(file=file.path('..','Data','RData',paste(modelName,'.Rdata',sep='')))

top1 <- 0.0
top2 <- 0.0
top3 <- 0.0
top4 <- 0.0
top5 <- 0.0
for (i in 1:150012){

	orderedDoc <- sort(mod.out$theta[i,],decreasing=TRUE)

	top1 <- top1 + orderedDoc[1]
	top2 <- top2 + orderedDoc[2]
	top3 <- top3 + orderedDoc[3]
	top4 <- top4 + orderedDoc[4]
	top5 <- top5 + orderedDoc[5]
}

sink(file.path('..','Results',paste(modelName,'averageTopicDensity.txt',sep='')))

av1 <- top1/150012.0
av2 <- top2/150012.0
av3 <- top3/150012.0
av4 <- top4/150012.0
av5 <- top5/150012.0

print('The average prevalence of the top 5 topics in a document are:')
print(av1)
print(av2)
print(av3)
print(av4)
print(av5)

sink()