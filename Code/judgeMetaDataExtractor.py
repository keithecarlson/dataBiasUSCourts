import pandas
import os
import csv

##reads the stata.dta file into a pandas dataframe
##creates a csv version with judge name, circuitnum, appointing president's party, year started, year ended
###year ended does not include senior status, so these have to be manually updated by researching online
#Other changes need to be made as described in DataSet Reconstruction Instructions
def createJudgeCSV(judgeDataOutFileName):

	df = pandas.read_stata(os.path.join('..','Data','judges','auburn_appct_stata.dta'))
	with open(judgeDataOutFileName,'wb') as outFile:

		csvOutFile = csv.writer(outFile,quoting=csv.QUOTE_ALL)
		csvOutFile.writerow(['Judge','Circuit','Party','StartYear','EndYear'])

		for index,row in df.iterrows():
			csvOutFile.writerow([row['name'].replace(",","<").strip(),row['circuit'],row['appres'],row['yeara'],row['yearl']])
			
if __name__ == "__main__":	

	judgeDataOutFileName = os.path.join('..','Data','judges','auburnDataAppointingPresParty.csv')

	createJudgeCSV(judgeDataOutFileName)

