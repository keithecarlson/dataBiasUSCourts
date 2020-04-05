import os
import matplotlib.pyplot as plt
import csv

#reads in the results of our previous regression from regResultsFileName
#creates a figure called figureOutFileName
#this figure shows all topics in which DMP had a significant (as defined by maxPVal) total effect on topic prevalence
#Topics are ordered by effect size (relative to corpus wide topic occurrence rate) descending and labeled according to the names in topicLabelFile 

def makeEffectPlot(regResultsFileName, topicLabelFile,figureOutFileName, maxPVal, overallPrevFileName):

	labels = []
	#create list of labels
	with open(topicLabelFile,'r') as tlFile:
		for line in tlFile.readlines():
			labels.append(line.strip())

	overallPrevs = []
	with open(overallPrevFileName,'r') as prevFile:
		prevCSV = csv.reader(prevFile)
		prevHeaders = prevCSV.next()

		for line in prevCSV:
			overallPrevs.append(float(line[prevHeaders.index('x')]))


	#Read in and store in lists, each topics point estimate of effect size and upper and lower ends of the confidence interval and p-val 
	xVals = []
	lowerVals = []
	upperVals = []
	pVals = []
	with open(regResultsFileName,'r') as regResultsFile:
		regCSV =csv.reader(regResultsFile)
		regHeaders = regCSV.next()

		curTopicNum = 0
		for line in regCSV:
		
			xVals.append(float(line[regHeaders.index('majorityParty Effect')])/overallPrevs[curTopicNum])
			lowerVals.append(float(line[regHeaders.index('Lower CI')])/overallPrevs[curTopicNum])
			upperVals.append(float(line[regHeaders.index('Upper CI')])/overallPrevs[curTopicNum])
			pVals.append(float(line[regHeaders.index('P-Val')]))
			curTopicNum +=1

	#find topics with significant effect
	topicsToShow = []
	for i in range(len(xVals)):
		if pVals[i]<maxPVal:
			topicsToShow.append(i)
	
	#sort by effect size
	dispOrder =sorted(topicsToShow, key=lambda k: abs(xVals[k]))
	xVals = [xVals[shown] for shown in dispOrder]
	lowerVals = [lowerVals[shown] for shown in dispOrder]
	upperVals = [upperVals[shown] for shown in dispOrder]

	yVals = range(1,len(dispOrder)+1)
	labels = [labels[labelNum] for labelNum in dispOrder]

	#create the figure
	plt.figure(figsize=(10,8))

	font = {'size'   : 10}
	plt.rc('font', **font)
	plt.plot(xVals,yVals,color='black', marker='o',linestyle='None',markersize=7, label='Total Effect')
	plt.axvline(0,ls='dashed',color='gray')
	plt.yticks(yVals,labels)
	#plot confidence intervals  as lines
	for i in range(len(xVals)):
		plt.hlines(y=yVals[i-1], xmin = float(lowerVals[i-1]), xmax=float(upperVals[i-1]),linewidth = 3,colors='gray', linestyles='solid')
		
	plt.tight_layout()
	plt.xticks
	x1,x2,y1,y2 = plt.axis()

	plt.axis((x1,x2,0,len(xVals)+1))
	plt.tight_layout()

	#save it as figureOutFileName
	plt.savefig(figureOutFileName,dpi=500)


if __name__ == "__main__":  
	#only show topics which are significant at this p-value
	maxPVal = .01

	#name of the file with the Regression results we are going to plot
	medResultsFileName = os.path.join('..','Results','topicRegressionResults','50TopicTrueDatatopicPrevOLS.csv')

	#name of the file which holds the topic labels, 1 per line which should be displayed on the figure
	topicLabelFile = os.path.join('..','Results','topicLabels.txt')

	#name of file with average prevalence of each topic in entire corpus
	overallPrevFileName = os.path.join('..','Results','topicRegressionResults','topicPrevalence.csv')

	#fileName for the resulting figure
	figureOutFileName = os.path.join('..','Results','Figures','figure5.png')

	makeEffectPlot(medResultsFileName, topicLabelFile, figureOutFileName ,maxPVal, overallPrevFileName)