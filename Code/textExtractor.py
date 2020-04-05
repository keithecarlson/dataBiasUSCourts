import os
import sys
import csv
import random 
from collections import defaultdict
import caseClass
import helpers
reload(sys)
sys.setdefaultencoding('utf-8')

##This file contains code to prune cases based on our criteria and then output a csv file for each circuit containing the text of the 
##remaining cases and some meta information about them, including our tagging of USParty, corpParty, and judges on the panel.
##It will also create a file for each circuit with the number of cases that were excluded for each step of the pruning process.
##Finally it will sample cases and output them and the assigned judges and USParty and corpParty tags which can be used to
# manually verify the accuracy of the tagging process
##See Dataset Reconstruction Instructions for an example of how to run it.

def extractText(circuitName,numPermsToGenerate, judgeFileName,opinionDir,clusterDir,stmOutFileName,pruningOutFileName,sampleCaseCandidateList):

	#open the file that we will write everything out to to run the topic model on
	with open(stmOutFileName,'wb') as stmFile:

		stmCSVFile = csv.writer(stmFile,quoting=csv.QUOTE_ALL)

		headerRow = ['','filename','document','party','year','circuit','judges','USParty','corpParty']
		for permIndex in range(numPermsToGenerate):
			headerRow.append('permutedParty' + str(permIndex+1))
		stmCSVFile.writerow(headerRow)

		#a dictionary to keep track of how many files pass each stage of pruning
		countsDict = defaultdict(int)

		#will hold all judges on this circuit and will be used for judgeTagging
		judgeList = helpers.makePotentialJudgesList(circuitName,judgeFileName)

		#we will generate a list of lists of permuted within each circuit judge parties to use as pseudo data later for the topic modeling
		judgePartyPermutations = []

		#generate the random permutations of judges to parties
		judgeParties = [j.party for j in judgeList]
		for i in range(numPermsToGenerate):
			judgePartyPermutations.append(random.sample(judgeParties,len(judgeParties)))
		
		#will hold the actual instances of case classes for the cases in sampleCaseCandidateList
		#we also build a list of the text at this point so that for a case we can assign it a value of the text before
		#judge names are removed, newlines are removed etc.  otherwise it will be hard to manually validate
		sampleCases=[]
		sampleCaseText=[]	


		rowNum = 0
		#go through every opinion from this circuit
		for fileName in os.listdir(opinionDir):
			countsDict['Total'] +=1
			if countsDict['Total']%500==0:
				print "Processed " + str(countsDict['Total']) + " files for " + circuitName + "."
			
			#create an instance of our caseClass corresponding to this case.	
			curCase = caseClass.case(fileName, circuitName,opinionDir,clusterDir)

			#check for things which may exclude this case from analysis
			if not curCase.validCluster:
				countsDict['No Cluster'] +=1
				continue
			if not curCase.precedential:
				countsDict['Not Precedential'] +=1
				continue
			if curCase.fedCite == None or curCase.fedCite == "":
				countsDict['No Federal Citation'] +=1
				continue
			if curCase.yearFiled<1970:
				countsDict['Before 1970'] += 1
				continue
			if curCase.yearFiled>2010:
				countsDict['After 2010'] += 1
				continue
			if curCase.soup == None:
				countsDict['No Valid HTML'] +=1
				continue

			#if it has passed all checks so far, create the plain text version of the case 
			curCase.assignCleanText()
			
			#throw out cases with insufficent amount of text
			if curCase.getTextSize() <3000:
				countsDict['Smaller than 3KB'] +=1
				continue


			#keep only cases where the federal citation number in the header(cluster)
			#is the same as what is listed at the top of the cases text
			if curCase.fedCite.lower() not in curCase.cleanText.split('\n')[0].lower(): 
				countsDict['Fed Cite not in Text'] +=1
				continue

			#if we passed these checks then assign judges to the case
			curCase.assignJudges(judgeList)

			#identify if the United States is one of two entities the case is between
			curCase.assignUSParty()

			#identify if a corporation is one of the parties on the case
			curCase.assignCorpParty()

			#if we've passed all of these checks so far then we will consider outputting this case for validation of the tagging processes
			sampleCases.append(curCase)
			sampleCaseText.append(curCase.cleanText)

			#throw out cases where there aren't exactly three judges from the circuit on the case
			if len(curCase.caseJudges) != 3:
				countsDict['Not Exactly Three Judges'] +=1
				continue

			#Remove the judges' last names from the text so that the topic model doesn't learn to associate individual names with a specific party
			#Remove United, States, America from text
			#Remove corporation words from text
			#remove state names from the text so we don't end up with topics which are just states names
			curCase.removeTargetWordsFromText()

			

			rowNum+=1
			newRow=[rowNum,fileName,curCase.cleanText,curCase.getJudgePartiesList(),curCase.yearFiled,curCase.circuitNum,
						curCase.getJudgeNames(),curCase.USParty,curCase.corpParty]
			

			#add the permuted party data to the row before we write it
			for permNum in range(numPermsToGenerate):
				permJudgeList = []
				for nextJudge in curCase.caseJudges:
					permJudgeList.append(judgePartyPermutations[permNum][judgeList.index(nextJudge)])
				newRow.append(permJudgeList)

			stmCSVFile.writerow(newRow)
													


	#create a file which tells how many opinions remained at each step of pruning	
	pruningOrder = ['No Cluster','Not Precedential','No Federal Citation','Before 1970','After 2010','No Valid HTML','Smaller than 3KB','Fed Cite not in Text','Not Exactly Three Judges']							
	
	with open(pruningOutFileName,'w') as statOut:
		statOut.write("Started with " + str(countsDict['Total']) + ' opinions from court listener.  The following numbers were removed for each reason:\n')
		for key in pruningOrder:
			statOut.write(key + ": " + str(countsDict[key]) +'\n')
	
		statOut.write("\nLeaving a total of " + str(rowNum) + ' documents in our corpus from this circuit.')

	return sampleCases,sampleCaseText

#actuallyRun the creation of the the .csv files for the circuits in circuitlist	
#circuitList names needs to match the folder names in opinions, clusters
#will output numValidationSamplesOutput cases with the USParty, corpParty, and judge's identified for manual validation
def runExtraction(baseOpinionDir, baseClusterDir, circuitList, numPermsToGenerate,numValidationSamplesOutput):

	#file with information on judge names, parties, etc
	judgeFileName = os.path.join('..','Data','judges',"auburnDataAppointingPresParty.csv")

	#directory to contain CSVs for the STM
	outPutDir = os.path.join('..','Data','stmCSV')


	#directory to contain information about how many files were removed at each step of our pruning process
	pruningOutDir = os.path.join('..','Results','pruningStats')


	#directory to contain the cases sampled for validation of our tagging methods
	valOutputDir = os.path.join('..','Results','validationSample')

	#make folders to hold the produced files
	helpers.maybeMakeDirStructure(outPutDir)
	helpers.maybeMakeDirStructure(pruningOutDir)
	helpers.maybeMakeDirStructure(valOutputDir)

	#create a list of all opinions
	sampleFilesList=helpers.createOpinionFileList(baseOpinionDir,circuitList)

	#shuffle them so that just reading sequentially through the list will access them at random
	#keep 5 times the number we want to ultimately have in our sample so we have enough even after pruning
	random.shuffle(sampleFilesList)
	sampleFilesList = sampleFilesList[:10*numValidationSamplesOutput]
	
	#will hold the casees and case text for our validation sample
	sampleCases=[]
	sampleCaseText =[]

	for circuitName in circuitList:
		#directories holding raw json from courtlistener
		opinionDir = os.path.join(baseOpinionDir, circuitName)
		clusterDir = os.path.join(baseClusterDir,circuitName)

		#names of output files
		stmOutFileName = os.path.join(outPutDir,circuitName + 'DataForSTM.csv')
		pruningOutFileName = os.path.join(pruningOutDir,circuitName + 'pruningStats.txt')

		#create the .csv for the STM for this circuit and update our lists of the cases we use for validation
		circuitCases,circuitCaseText = extractText(circuitName,numPermsToGenerate,judgeFileName,opinionDir,clusterDir,stmOutFileName,pruningOutFileName,sampleFilesList)
		sampleCases = sampleCases+circuitCases
		sampleCaseText = sampleCaseText + circuitCaseText	
	
	#shuffle the cases which passed the preliminary validation again, since we added them ciruit by circuit
	sampleInds = range(len(sampleCases))
	random.shuffle(sampleInds)

	#create the actual files which will be manually inspected for validation
	for caseInd in sampleInds[:numValidationSamplesOutput]:
		curCase = sampleCases[caseInd]
		with open(os.path.join(valOutputDir,curCase.opinionFileName[:-4]+'txt'),'w') as outFile:
			judgeOut = [j.fullName for j in curCase.caseJudges ]
			outFile.write('Judges: ' + str(judgeOut) + '\n')
			outFile.write('USParty: ' + str(curCase.USParty) + '\n')
			outFile.write('corpParty: ' + str(curCase.corpParty) + '\n')
			outFile.write('case title from cluster: ' + str(curCase.caseTitle) + '\n')
			outFile.write('Case Text:\n\n' + sampleCaseText[caseInd])

if __name__ == "__main__":

	#seed the random generator so future runs are consistent with reported results
	random.seed(12345)

	circuitList = ['ca1','ca2','ca3','ca4','ca5','ca6','ca7','ca8','ca9','ca10','ca11','cadc']
	numPermsToGenerate = 100
	numValidationSamplesOutput = 100

	baseOpinionDir=os.path.join('..','Data','opinions')
	baseClusterDir=os.path.join('..','Data','clusters')

	runExtraction(baseOpinionDir,baseClusterDir,circuitList,numPermsToGenerate,numValidationSamplesOutput)
	


		


		