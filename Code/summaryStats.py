import csv
import os
import helpers
#since the text of some cases is so long we need to increase the csv field size limit in order to read it
csv.field_size_limit(3000000)


#This script goes through the processed data and produces summary statistics about it.
#Finds the number of cases which have the United States as one of two parties on the case for each circuit.
#Finds the number of cases with 0, 1, 2, and 3 democrats on the panel for each circuit.
#Also prints the total number of cases in the corpus

def summarize(circuits,circuitCSVDirName,summaryStatsDir):

	#make our output directory
	helpers.maybeMakeDirStructure(summaryStatsDir)

	#open our output files
	with open(os.path.join(summaryStatsDir,'USPartyCount.csv'),'wb') as USOutFileRaw:
		USPartyOutFile = csv.writer(USOutFileRaw)
		USPartyOutFile.writerow(['Circuit','US Party Case Count','Non US Party Case Count', 'Percent of Cases with US as Party'])
	
		with open(os.path.join(summaryStatsDir,'panelComposition.csv'),'wb') as demsOutFileRaw:
			demsOnPanelOutFile = csv.writer(demsOutFileRaw)
			demsOnPanelOutFile.writerow(['Circuit','Cases with 0/3 Democrats','Cases with 1/3 Democrats','Cases with 2/3 Democrats','Cases with 3/3 Democrats'])


			
			#go through all circuits
			for circuit in circuits:
				with open(os.path.join(circuitCSVDirName,circuit + 'DataForSTM.csv'),'rb') as metaFileRaw:
					metaFile = csv.reader(metaFileRaw)

					#initialize variables for us to store the aggregate counts in for this circuit
					usPartyCount=0
					count = 0
					demDict = {}
					for demCount  in range(4):
						demDict[str(demCount)] = 0

					#for each case read in the relevant data	
					for line in metaFile:
						fileName = line[1]
						fileParties = line[3]
						fileUSParty = line[7]

						#skip the header line
						if fileName!='filename':
							count +=1

							if fileUSParty == "True":
								usPartyCount+=1

							demCount = str(fileParties.count('1'))
							demDict[demCount]+=1

					#write out the results for this circuit
					USPartyOutFile.writerow([circuit,usPartyCount,count-usPartyCount,(0.0+usPartyCount)/count])
					demsOnPanelOutFile.writerow([circuit,demDict['0'],demDict['1'],demDict['2'],demDict['3']])



if __name__ == "__main__":		

	circuitCSVDirName = os.path.join('..','Data','stmCSV')
	summaryStatsDir = os.path.join('..','Results','summaryStats')
	
	circuitList = ['ca1','ca2','ca3','ca4','ca5','ca6','ca7','ca8','ca9','ca10','ca11','cadc']
	summarize(circuitList,circuitCSVDirName,summaryStatsDir)