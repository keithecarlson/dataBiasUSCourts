import os
import csv
import scipy.stats
import numpy as np
import helpers

csv.field_size_limit(3000000)



#reads in circFileName and returns two dictionaries and two lists
#judgeToCaseNumDict is a dictionary mapping each judge to a list of the case index numbers in circFileName for which they are on the panel
#judgeToPartyDict is a dictionary mapping each judge to their party (0 for Republican, 1 for Democrat as used throughout)
#caseYears is a list where the ith entry is the year of the ith case in circFileName
#caseDemCounts is a list where the ith entry is the number of democrats on the panel of the ith case

def buildJudgeCaseDicts(circFileName):

	judgeToCaseNumDict={}
	judgeToPartyDict = {}
	caseYears = []
	caseDemCounts = []
	#open the file
	with open(circFileName,'rb') as circFile:
		circFileCSV = csv.reader(circFile)
		for line in circFileCSV:
			#for each line, add the year and number of dems on the case to our ordered lists
			if line[4].strip().isdigit():
				caseYears.append(int(line[4]))
				caseDemCounts.append(line[3].count('1'))
				jCount = 0
				
				for judgeRev in line[6].split(','):
					#for each judge on the case, find their name
					judge = judgeRev.strip().split(' ')[1].capitalize() + ' ' + judgeRev.strip().split(' ')[0].capitalize().strip()
					#if we haven't seen this judge yet, find their party and then add them as a key to our dictionaries
					if judge not in judgeToCaseNumDict:
						judgeToCaseNumDict[judge] = []
						judgeToPartyDict[judge] = int(line[3].split(',')[jCount].replace('[','').replace('\'','').replace(']','').strip())
					#add the current index of the end of the caseList to our judges list of caseIndices they appear on
					judgeToCaseNumDict[judge].append(len(caseYears)-1)
					jCount+=1

	return judgeToCaseNumDict,judgeToPartyDict,caseYears,caseDemCounts


#using the lists and dictionaries created by buildJudgeCaseDicts
#returns pDict, a nested dictionary of year->judgeName->percent of total judge appearances for the year this judge accounts for
#also returns obsAssociatesDict, a nested dictionary of year->judgeName->a 3-element list with the ith entry representing the number of times
#the judge appeared with i democrats on a panel in that year
def buildJudgeAppearanceRateDict(judgeToCaseNumDict,judgeToPartyDict, caseYears,caseDemCounts):
	pDict = {}
	obsAssociatesDict = {}

	for judge in judgeToCaseNumDict:
		#go through every case the judge is on
		for caseInd in judgeToCaseNumDict[judge]:
			if caseYears[caseInd] not in pDict:
				pDict[caseYears[caseInd]] = {}
				obsAssociatesDict[caseYears[caseInd]] = {}
			if judge not in pDict[caseYears[caseInd]]:
				pDict[caseYears[caseInd]][judge] =0 
				obsAssociatesDict[caseYears[caseInd]][judge] = [0,0,0]
			#keep track of how many times the judge appears in a given year	
			pDict[caseYears[caseInd]][judge] +=1
			#and keep track of the total number of times this judge appears with 0,1,or 2 democrats in each year
			obsAssociatesDict[caseYears[caseInd]][judge][caseDemCounts[caseInd]-judgeToPartyDict[judge]] +=1

	#normalize the number of times all jduges appear in each year so they are probabilities rather than counts
	for year in pDict:
		div = sum(pDict[year].values())
		for judge in pDict[year]:
			pDict[year][judge] = (0.0+pDict[year][judge])/div


	return pDict,obsAssociatesDict

#uses pDict from buildJudgeAppearanceRateDict and judgeToPartyDict telling us the party of each judge name
#returns a nested dictionary of year->judge->three element list where each entry is the expected probability of the
#judge appearing with 0,1,or 2 dems on a case in that year if there is no bias
def buildExpectedAssociateRateDict(pDict,judgeToPartyDict):
	expectedAssociateRateDict = {}
	for year in pDict:
		expectedAssociateRateDict[year] = {}
		for judge in pDict[year]:
			expectedAssociateRateDict[year][judge]=[0.0,0.0,0.0]

			for j1 in pDict[year]:
				for j2 in pDict[year]:
					if j1!=j2 and j1!=judge and j2!=judge:
						prob1 = pDict[year][j1]/(1-pDict[year][judge])
						prob2 = pDict[year][j2]/(1-pDict[year][judge]-pDict[year][j1])

						expectedAssociateRateDict[year][judge][judgeToPartyDict[j1]+judgeToPartyDict[j2]] += prob1*prob2

	return expectedAssociateRateDict

#uses the expected rate of a judge appearing with other panel member parties and the number of cases the judge saw in each year(taken from obsAssociatesDict)
#converts the expected rates to expected counts and returns a new dictionary
def convertExpectedRateToCount(expectedAssociateRateDict,obsAssociatesDict):
	expAssociateCountDict={}
	for year in expectedAssociateRateDict:
		expAssociateCountDict[year] = {}
		for judge in expectedAssociateRateDict[year]:
			expAssociateCountDict[year][judge] = [rate * sum(obsAssociatesDict[year][judge]) for rate in expectedAssociateRateDict[year][judge]]

	return expAssociateCountDict

#uses the counts of observed and expected parties of each judges associates to determine the probability that there was no bias
#in their associates party over their career
def findCareerBiasProbs(obsAssociatesDict,expAssociateCountDict):
	judgeCareerObsAssociates = {}
	judgeCareerExpAssociates = {}

	#sum the total and expected associate parties for the judge over their career
	for year in obsAssociatesDict:
		for judge in obsAssociatesDict[year]:
			if judge not in judgeCareerObsAssociates:
				judgeCareerObsAssociates[judge] = [0,0,0]
				judgeCareerExpAssociates[judge] = [0.0,0.0,0.0]
			judgeCareerObsAssociates[judge] = [sum(x) for x in zip(judgeCareerObsAssociates[judge],obsAssociatesDict[year][judge])]	
			judgeCareerExpAssociates[judge] = [sum(x) for x in zip(judgeCareerExpAssociates[judge],expAssociateCountDict[year][judge])]	

	judgeCareerPVals = {}

	#if there are at least 5 of all expected and observed associate party possibilities, do a chisquare to test bias
	for judge in judgeCareerObsAssociates:
		if (judgeCareerExpAssociates[judge][0]>=5 and judgeCareerExpAssociates[judge][1]>=5 and judgeCareerExpAssociates[judge][2]>=5 and
				judgeCareerObsAssociates[judge][0]>=5 and judgeCareerObsAssociates[judge][1]>=5 and judgeCareerObsAssociates[judge][2]>=5):
				
			jStat,jP =scipy.stats.chisquare(judgeCareerObsAssociates[judge],f_exp = judgeCareerExpAssociates[judge])
			judgeCareerPVals[judge] = jP

	#return the observed and expected associates for each judge over their career, and the p-vals of the chi square tests
	return judgeCareerObsAssociates,judgeCareerExpAssociates, judgeCareerPVals

#Run the whole thing to find how many and which judges did not appear with other panel members(by party) at the predicted rate
def findJudgeBiasesForCircuit(circFileName,judgeOutFileName,summaryOutFileName,circuit):
	judgeToCaseNumDict,judgeToPartyDict,caseYears,caseDemCounts = buildJudgeCaseDicts(circFileName)

	pDict,obsAssociatesDict = buildJudgeAppearanceRateDict(judgeToCaseNumDict,judgeToPartyDict,caseYears,caseDemCounts)

	expectedAssociateRateDict = buildExpectedAssociateRateDict(pDict,judgeToPartyDict)

	expAssociateCountDict = convertExpectedRateToCount(expectedAssociateRateDict,obsAssociatesDict)

	judgeCareerObsAssociates,judgeCareerExpAssociates, judgeCareerPVals = findCareerBiasProbs(obsAssociatesDict,expAssociateCountDict)
	
	#print the results to files
	with open(judgeOutFileName,'a') as judgeOutFile:
		
		judgeOutCSV = csv.writer(judgeOutFile,quoting=csv.QUOTE_ALL)
		
		for judge in judgeCareerPVals:
			pvalOut = "{:.3f}".format(judgeCareerPVals[judge])
			if pvalOut == '0.000':
				pvalOut='<0.001'
			judgeOutCSV.writerow([judge,circuit,[int(round(x)) for x in judgeCareerExpAssociates[judge]],
					judgeCareerObsAssociates[judge],pvalOut])
	
	with open(summaryOutFileName,'a') as summaryOutFile:
		summaryOutFile.write(str(len([p for p in judgeCareerPVals.values() if p <.05])) + ' out of ' +str(len(judgeCareerPVals)) +
			 ' judges showed panel associate bias at p=.05 for circuit ' + circuit+'\n')
		summaryOutFile.write(str(len([p for p in judgeCareerPVals.values() if p <.01])) + ' out of ' +str(len(judgeCareerPVals)) +
			 ' judges showed panel associate bias at p=.01 for circuit ' + circuit+'\n')
		summaryOutFile.write(str(len([p for p in judgeCareerPVals.values() if p <.001])) + ' out of ' +str(len(judgeCareerPVals)) +
			 ' judges showed panel associate bias at p=.001 for circuit ' + circuit+'\n\n')

	return judgeCareerPVals.values()
if __name__ == "__main__":	

	np.random.seed(12345)
	dataDirName = os.path.join('..','Data','stmCSV')
	circList = ['ca1','ca2','ca3','ca4','ca5','ca6','ca7','ca8','ca9','ca10','ca11','cadc']

	outDirName = os.path.join('..','Results','panelBiasResults')
	judgeOutFileName = os.path.join(outDirName, 'judgeBiases.csv')
	summaryOutFileName = os.path.join(outDirName,'judgeBiasSummary.txt')

	helpers.maybeMakeDirStructure(outDirName)
		
	
	with open(summaryOutFileName,'w') as summaryOutFile:
		summaryOutFile.write('Tested whether judges showed bias in party of judges they appeared on panels with on the cases they published.\n\n')

	with open(judgeOutFileName,'w') as judgeOutFile:
		judgeOutCSV = csv.writer(judgeOutFile,quoting=csv.QUOTE_ALL)
		judgeOutCSV.writerow(['Judge','Circuit','Expected Associates','Observed Associates','p-value'])

	allJudgePVals= []

	#run the tests for each circuit individually
	for circ in circList:
		circFileName = os.path.join(dataDirName,circ+ 'DataForSTM.csv')
		allJudgePVals =  allJudgePVals + findJudgeBiasesForCircuit(circFileName,judgeOutFileName,summaryOutFileName,circ)

	#also output the number of judges in the whole corpus who's panel associates were biased across their career
	with open(summaryOutFileName,'a') as summaryOutFile:
		summaryOutFile.write(str(len([p for p in allJudgePVals if p <.05])) + ' out of ' +str(len(allJudgePVals)) +
			 ' judges showed panel associate bias at p=.05 the whole corpus\n')
		summaryOutFile.write(str(len([p for p in allJudgePVals if p <.01])) + ' out of ' +str(len(allJudgePVals)) +
			 ' judges showed panel associate bias at p=.01 for the whole corpus\n')
		summaryOutFile.write(str(len([p for p in allJudgePVals if p <.001])) + ' out of ' +str(len(allJudgePVals)) +
			 ' judges showed panel associate bias at p=.001 for the whole corpus\n')


