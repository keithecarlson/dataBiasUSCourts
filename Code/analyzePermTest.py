import os
from scipy import stats
import numpy as np
import csv

####This code will take the results of running models on samples of the data with true and permuted majorityParty produced by permTest.R
####And print some significance tests and other statistics for them
resultsFileName = os.path.join('..','Results','STMPermutationTest','permTestResults.csv')

outputFileName = os.path.join('..','Results','STMPermutationTest','permTestAnalysis.txt')

#set the random seed so that results are reproducible
np.random.seed(12345)

#load the point estimates of the true and permuted data into two lists
with open(resultsFileName,'rb') as file:
	trueResults = []
	permResults = []
	csvFile = csv.reader(file)
	for line in csvFile:
		if line[0] == 'majorityParty':
			trueResults.append(abs(float(line[1])))
		if line[0] == 'permMajorityParty':
			permResults.append(abs(float(line[1])))

#print results to file
with open(outputFileName,'w') as outFile:
	outFile.write("Average Largest Effects:")
	outFile.write('\nTrue Data: ' + str(sum(trueResults) / float(len(trueResults))))
	outFile.write('\nPermuted Data: ' + str(sum(permResults) / float(len(permResults))))

	outFile.write("\n\nStandard Deviation of Largest Effects:")
	outFile.write('\nTrue Data: ' + str(np.std(trueResults)))
	outFile.write('\nPermuted Data: ' + str(np.std(permResults)))

	#do various tests to see if results from true data and results from permuted data are drawn from the same distribution
	outFile.write("\n\nTwo Sample KS-Test\n")
	outFile.write(str(stats.ks_2samp(trueResults, permResults)))

	outFile.write('\n\nDependent T-Test\n')
	outFile.write(str(stats.ttest_rel(trueResults,permResults)))

	outFile.write('\n\nIndependent T-Test\n')
	outFile.write(str(stats.ttest_ind(trueResults,permResults)))


