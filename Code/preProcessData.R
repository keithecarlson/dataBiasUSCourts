library(stm)

#set the random seed so that the results are reproducible
set.seed(12345)

setwd(file.path('..','Data','stmCSV'))


#####Load all of our circuit data
data1 <- read.csv("ca1DataForSTM.csv")
data2 <- read.csv("ca2DataForSTM.csv")
data3 <- read.csv("ca3DataForSTM.csv")
data4 <- read.csv("ca4DataForSTM.csv")
data5 <- read.csv("ca5DataForSTM.csv")
data6 <- read.csv("ca6DataForSTM.csv")
data7 <- read.csv("ca7DataForSTM.csv")
data8 <- read.csv("ca8DataForSTM.csv")
data9 <- read.csv("ca9DataForSTM.csv")
data10 <- read.csv("ca10DataForSTM.csv")
data11 <- read.csv("ca11DataForSTM.csv")
datadc <- read.csv("cadcDataForSTM.csv")

data <- do.call("rbind", list(data1,data2,data3,data4,data5,data6,data7,data8,data9,data10,data11,datadc))

#Process all of the data (stemming, removing stopwords, punctuation, converting to lowercase, and removing words which appear in fewer than 100 documents)
processed <- textProcessor(data$document, metadata = data)
out <- prepDocuments(processed$documents, processed$vocab,processed$meta, lower.thresh = 100)
documents <- out$documents
vocab <- out$vocab
meta <- out$meta

#Create indicator variables for each circuit
meta$circuit1 <- (meta$circuit == "ca1")*1
meta$circuit2 <- (meta$circuit == "ca2")*1
meta$circuit3 <- (meta$circuit == "ca3")*1
meta$circuit4 <- (meta$circuit == "ca4")*1
meta$circuit5 <- (meta$circuit == "ca5")*1
meta$circuit6 <- (meta$circuit == "ca6")*1
meta$circuit7 <- (meta$circuit == "ca7")*1
meta$circuit8 <- (meta$circuit == "ca8")*1
meta$circuit9 <- (meta$circuit == "ca9")*1
meta$circuit10 <- (meta$circuit == "ca10")*1
meta$circuit11 <- (meta$circuit == "ca11")*1
meta$circuitdc <- (meta$circuit == "cadc")*1


#save an image of this data now that all of the preprocessing and cleaning is finished so we can use it elsewhere without repeating these steps
setwd(file.path('..'))
dir.create(file.path('RData'))
save.image(file.path('RData','preparedData.Rdata'))


#write the vocab size after the lowercasing, stemming etc to a file.
file.create(file.path('..','Results','vocabSize.txt'))
fileConn<-file(file.path('..','Results','vocabSize.txt'))
writeLines(c('After preprocessing the number of unique tokens in the vocab is:',toString(NROW(vocab))), fileConn)
close(fileConn)
