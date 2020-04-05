library(stm)

#set the random seed so that the results are reproducible
set.seed(12345)
#Create the STMOutput Directory'
dir.create(file.path('..','Results'))
dir.create(file.path('..','Results','topicModelWords'))


#first run the model using the true party information
dataSource<-file.path('..','Data','RData','preparedData.Rdata')
numTopics<-50
modelName<-'50TopicTrueData'
load(file=dataSource)

#create a majorityParty variable which will be 1 if there are at least 2 democrats on the panel, and 0 otherwise
meta$majorityParty <-  ( as.character(meta$party) == "['0', '1', '1']" | as.character(meta$party) == "['1', '1', '1']" | as.character(meta$party) == "['1', '0', '1']" | as.character(meta$party) == "['1', '1', '0']") *1	

#Create the topic model, may take days or weeks.
mod.out <- stm(documents, vocab, K=numTopics, prevalence=~s(year)+circuit1+circuit2+circuit3+circuit4+circuit5+circuit6+circuit7+circuit8+circuit9+circuit10+circuit11+circuitdc+majorityParty,content=~majorityParty, data=meta,init.type="Spectral")

#save the image so we can reload and work with this topic model later.
save.image(file.path('..','Data','RData',paste(modelName,".Rdata",sep='')))

#save the words associated with each topic 
sink(file.path('..','Results','topicModelWords',paste(modelName,'TopicWords.txt',sep='')))
sageLabels(mod.out)
sink()











