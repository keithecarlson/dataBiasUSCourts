import pandas as pd
import os

#this is some simple code which takes all of the cases used for the stm and creates a single csv file for them with one row per case
#and columns for the parties of the 3 judges, year, circuit, corpParty, USParty, number of Dems on the panel, and lustrum (5 year span)

def createLustrumDataFile(dataDir,circuitList,outFileName):
	myData = []
	for circ in circuitList:
	    myData.append(pd.read_csv(os.path.join(dataDir,'stmCSV',circ+'DataForSTM.csv'),usecols=['party','year','circuit','corpParty','USParty']))

	loadedData = pd.concat(myData)

	loadedData['demCount'] = loadedData.apply(lambda row: str(row.party).count('1'), axis=1)
	loadedData['lustrum'] = loadedData.apply(lambda row: (int(row.year)-1970)/5, axis=1)

	#rather than have 2010 completely alone we group it with the 2005-2009 lustrum
	loadedData['lustrum'] = loadedData.apply(lambda row: row.lustrum if row.lustrum!= 8 else 7, axis=1)

	loadedData.to_csv(outFileName)

if __name__ == "__main__":	

	dataDir= os.path.join('..','Data')
	circuitList = ['ca1','ca2','ca3','ca4','ca5','ca6','ca7','ca8','ca9','ca10','ca11','cadc']
	outFileName = os.path.join(dataDir,'lustrumDemCountDataAllCircuits.csv')


	createLustrumDataFile(dataDir, circuitList, outFileName)