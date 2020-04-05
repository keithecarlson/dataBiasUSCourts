import os
import numpy as np
from scipy import stats
import csv
np.random.seed(12345)

#reads the regression results for STM modelName.
#finds the forNLargestEffects topics with the greatest effect size.
#calculates the average effect size and standard deviation for these topics
#writes the results to outFile (an open file object) and and also returns an array of the point estimates to be used for a ks test
def findAverageEffectSize(modelName,forNLargestEffects,outFile):

	regResultsFileName = os.path.join('..','Results','topicRegressionResults',modelName +'topicPrevOLS.csv')
	effectList = []

	with open(regResultsFileName,'r') as regResultsFile:
		regCSV =csv.reader(regResultsFile)
		regHeaders = regCSV.next()

		for line in regCSV:
			
			effectList.append(abs(float(line[regHeaders.index('majorityParty Effect')])))
		
	effectList = sorted(effectList)[-forNLargestEffects:]

	
	outFile.write("\n\nModel " + modelName + " analyzed using " + str(forNLargestEffects) + ' topics with largest effect in regression: \n')
	outFile.write("Average Effect: " + str(np.mean(effectList)))
	outFile.write("\nStandard Deviation: " + str(np.std(effectList)))

	return effectList


#takes two lists of the point estimates of the absolute value of effect sizes, one for the true model and one for permuted
#does a 2 sample ks test to see if they are drawn from the same distribution
#writes results to a outFile(an open file object)
def testDistributions(effectList1,effectList2,outFile):
	s,pv = stats.ks_2samp(effectList1, effectList2)

	
	outFile.write("\n\nResults of KS test to see if true model and permuted model have their largest effects drawn from same distribution:\n")
	outFile.write("KS statistic: " + str(s))
	outFile.write("\np-value: " + str(pv))

if __name__ == "__main__":	

	with open(os.path.join('..','Results','topicRegressionResults','effectSizeKSTest.txt'),'w') as outFile:

		trueEffects = findAverageEffectSize('50TopicTrueData',10,outFile)
		permEffects = findAverageEffectSize('50TopicPermDMP',10,outFile)

		testDistributions(trueEffects,permEffects,outFile)