import os
import csv
import scipy.stats
import numpy
import helpers
csv.field_size_limit(3000000)


#reads the processed data in circFileName which should be created by textExtractor.py
#creates and returns a dictionary whose keys are years in yearRange and whose values are dictionaries
#the keys of the inner dictionary are instances of judgeClass and the values are the number of appearances 
#for the given judge in the given year divided by the total number of judge appearances for the year
def buildJudgePDict(judgeList, circFileName,yearRange):
	pDict = {}
	for year in yearRange:
		pDict[year] = {}

	with open(circFileName,'rb') as circFile:
		circFileCSV = csv.reader(circFile)
		for line in circFileCSV:
			if line[4].strip().isdigit() and int(line[4].strip()) in yearRange:

				year = int(line[4])
				judges = line[6].split(',')
				
				#for each judge on the case
				for lj in [j.strip() for j in judges]:
					#for each judge active in the case's year
					for pj in [j for j in judgeList if j.start<=year and j.end>=year]:

						if pj.lastName == lj.split(' ')[0].strip() and pj.firstName == lj.split(' ')[1].strip():

							#keep track of how many cases each judge appears on in each year
							if pj not in pDict[year]:
								pDict[year][pj]=0
							pDict[year][pj] += 1
				
	#Now divide the counts of judge occurrences for a given year by the total number of judge occurrences and return
	for year in yearRange:
		div = sum(pDict[year].values())
		for j in pDict[year]:
			pDict[year][j] = (0.0+pDict[year][j])/div

	return pDict



#using judgePDict, the probability dictionary of a judge appearing in a specific arbitrary postion for the given year
#return a list of the expected probability of each panel type (going from 0 dems to 3 dems) assuming that 
#the probabilities of judges appearing in cases are independent of each other.
def findExpectedRatios(judgePDict,year):
	probs = [0.0,0.0,0.0,0.0]
	for j1 in judgePDict[year]:
		for j2 in judgePDict[year]:
			for j3 in judgePDict[year]:
				if j1!=j2 and j2!=j3 and j1!=j3:
					prob1 = judgePDict[year][j1]
					prob2 = judgePDict[year][j2]/(1-judgePDict[year][j1])
					prob3 = judgePDict[year][j3]/(1-judgePDict[year][j1]-judgePDict[year][j2])

					probs[(j1.party+j2.party+j3.party).count('1')] += prob1*prob2*prob3

	return probs


#This code will do the panel composition analysis reported in the paper.
#For each circuit-year it will find theexpected and observed number of panels of each composition 
#as well as the result of a KS-test to see if the observed panels are drawn from the expected distribution
#will report summaries of these tests when grouped by circuit-year, or circuit, or year or using the whole dataset as a single test
def runExpectedCompAnalysis(judgeFileName,circList,dataDirName,outFileName,yearRange):
	#list to track the p-values of the tested circuit-years
	circYearPVals = []
	circPVals = []

	#Create lists of 4 elements to hold expected and observed panel counts across all Data
	totalExpCounts = [0.0,0.0,0.0,0.0]
	totalObsCounts = [0,0,0,0]
	

	pVals = []
	ePVals=[]

	#create dictionaries of year to Expected and Observed Counts of panel types which will be summed over all circuits 
	yearExpCounts = {}
	yearObsCounts = {}
	for yearExp in yearRange:
		yearExpCounts[yearExp] = [0.0,0.0,0.0,0.0]
		yearObsCounts[yearExp] = [0,0,0,0]


	with open(outFileName,'w') as outFile:
		#For each circuit create lists of 4 elements to hold expected and observed panel counts within the circuit
		for circ in circList:
			print "Doing circuit " + str(circ)
			outFile.write("For circuit " + str(circ) + '\n')
			circuitExpCounts = [0.0,0.0,0.0,0.0]
			circuitObsCounts = [0,0,0,0]
			circFileName = os.path.join(dataDirName,circ+ 'DataForSTM.csv')
				

			#populate list with all judges from the circuit
			judgeList = helpers.makePotentialJudgesList(circ,judgeFileName)


			#populate nested dictionary of year->judge->probability of judge appearing in arbitrary "position" (1,2, or 3) in that year for this circuit
			judgePDict = buildJudgePDict(judgeList,circFileName,yearRange)
			
			probs = {}
			obs = {}
			#populate probs with the expected panel ratios for each year
			for year in yearRange:
				probs[str(year)] = findExpectedRatios(judgePDict,year)
				obs[str(year)] = [0,0,0,0]

			#populate obs with the observed panel counts for each year.
			with open(circFileName,'rb') as circFile:
				circFileCSV = csv.reader(circFile)
				for line in circFileCSV:
					if line[4].strip() in probs:
						year = line[4]
						obs[str(year)][line[3].count('1')] +=1

			#for each year in this circuit
			for year in yearRange:
				
				#create lists which will just be equal to obs and probs except with panel types where the expected count is 0 removed
				holderO = []
				holderN = []

				#skip this iteration if there are zero cases for this circ-year (11th circuit wasn't established early on)
				if sum(obs[str(year)]) ==0:
					continue


				#i will range over panel types, i.e. 0,1,2,or 3 Democrats
				for i in range(4):

					#if some panel type can't occur, don't add it to holderO,holderN so that we can 
					#still perform chi-square test on other panel types
					#this will happen if for example there are only 2 Republican judges in this circuit-year
					if probs[str(year)][i] != 0.0:

						holderO.append(obs[str(year)][i]) 
						holderN.append(probs[str(year)][i] * sum(obs[str(year)]))
						
					
						#update expected and observed total counts in the circuit, year, and overall records
						totalExpCounts[i]+=probs[str(year)][i] * sum(obs[str(year)])
						totalObsCounts[i] += obs[str(year)][i]
						circuitExpCounts[i]+=probs[str(year)][i] * sum(obs[str(year)])
						circuitObsCounts[i] += obs[str(year)][i]
						yearObsCounts[year][i] +=  obs[str(year)][i]
						yearExpCounts[year][i] += probs[str(year)][i] * sum(obs[str(year)])


				#if all panel types with expected or observed count>0 also have expected/observed count>5 then 
				#this circuit-year is valid for testing with chisquare
				valid = True				
				for ex in holderN:
					if ex<5.0:
						valid = False
				for ob in holderO:
					if ob<5.0:
						valid = False

				#if there are at least 5 observed and expected panels of each type in this circ-year, do chisquare test and
				#keep track of all these pvalues
				if valid:
					ch,pv = scipy.stats.chisquare(holderO, f_exp = holderN)
					circYearPVals.append(pv)
								

			outFile.write( "Expected panel counts in this circuit: \n")
			outFile.write( str(circuitExpCounts) + '\n')

			outFile.write( "Observed panel counts in this circuit: \n")
			outFile.write( str(circuitObsCounts)+'\n')


			#do chisquare for this circuit when combined for all years and output results
			circStat,circP = scipy.stats.chisquare(circuitObsCounts,f_exp = circuitExpCounts)
			outFile.write("p-value that these were drawn from the same distribution: " + str(circP) + '\n\n')
			for i in range(4):
				outFile.write("In total, panels with " + str(i) + ' dems were expected to occur ' + str(circuitExpCounts[i]) +' times for this circuit.  They were observed ' + str(circuitObsCounts[i]) + ' times.\n')
				singleType = [circuitObsCounts[i],sum(circuitObsCounts)-circuitObsCounts[i]]
				singleExp = [circuitExpCounts[i],sum(circuitExpCounts)-circuitExpCounts[i]]
				panelStat,panelP = scipy.stats.chisquare(singleType,f_exp = singleExp)
				outFile.write('The probability of this happening assuming no bias is: ' + str(panelP) + '.\n\n')
			circPVals.append(circP)


		yearPVals = []

		#do the chisquare test for each year and output results
		for yearNum in yearRange:
			outFile.write("Expected Panels in " + str(yearNum) + ': \n')
			outFile.write(str(yearExpCounts[yearNum])+'\n')
			outFile.write("Observed panels in " + str(yearNum) + ': \n')
			outFile.write(str(yearObsCounts[yearNum])+'\n')

			yearStat,yearP = scipy.stats.chisquare(yearObsCounts[yearNum],f_exp = yearExpCounts[yearNum])
			outFile.write("p-value that these were drawn from the same distribution: " + str(yearP) + '\n\n')
			yearPVals.append(yearP)


		#output the number of circuits, years, circ-years which were siginficantly biased at various pvalues.
		outFile.write('Tested ' + str(len(circPVals)) + ' circuits.\n')
		outFile.write(str(len([cp for cp in circPVals if cp <=.05])) + ' showed panel composition bias at .05 significance level.\n')
		outFile.write(str(len([cp for cp in circPVals if cp <=.01])) + ' showed panel composition bias at .01 significance level.\n')
		outFile.write(str(len([cp for cp in circPVals if cp <=.001])) + ' showed panel composition bias at .001 significance level.\n\n')

		outFile.write('Tested ' + str(len(yearRange)) + ' years.\n')
		outFile.write(str(len([yp for yp in yearPVals if yp <=.05])) + ' showed panel composition bias at .05 significance level.\n')
		outFile.write(str(len([yp for yp in yearPVals if yp <=.01])) + ' showed panel composition bias at .01 significance level.\n')
		outFile.write(str(len([yp for yp in yearPVals if yp <=.001])) + ' showed panel composition bias at .001 significance level.\n\n')


		outFile.write("Tested " + str(len(circYearPVals)) + ' circ-years.\n')
		outFile.write(str(len([cyp for cyp in circYearPVals if cyp <=.05])) + ' showed panel composition bias at .05 significance level.\n')
		outFile.write(str(len([cyp for cyp in circYearPVals if cyp <=.01])) + ' showed panel composition bias at .01 significance level.\n')
		outFile.write(str(len([cyp for cyp in circYearPVals if cyp <=.001])) + ' showed panel composition bias at .001 significance level.\n\n')


		#combined all of our observations and see if there is overall bias when treating all observations and expectations as a single test
		outFile.write("Total expected panels (all cases in corpus): " + str(totalExpCounts) +'\n')


		outFile.write("Total observed panels: " + str(totalObsCounts)+'\n')

		totalStat,totalP = scipy.stats.chisquare(totalObsCounts,f_exp = totalExpCounts)

		outFile.write("p-value that these were drawn from the same distribution: " + str(totalP) + '\n\n')

		#see which of the panel types are over or under represented across the whole circuit
		for i in range(4):
			outFile.write("In total, panels with " + str(i) + ' dems were expected to occur ' + str(totalExpCounts[i]) +' times.  They were observed ' + str(totalObsCounts[i]) + ' times.\n')
			singleType = [totalObsCounts[i],sum(totalObsCounts)-totalObsCounts[i]]
			singleExp = [totalExpCounts[i],sum(totalExpCounts)-totalExpCounts[i]]
			panelStat,panelP = scipy.stats.chisquare(singleType,f_exp = singleExp)
			outFile.write('The probability of this happening assuming no bias is: ' + str(panelP) + '.\n\n')


if __name__ == "__main__":	

	numpy.random.seed(12345)

	judgeFileName = os.path.join('..','Data','judges','auburnDataAppointingPresParty.csv')

	circList = ['ca1','ca2','ca3','ca4','ca5','ca6','ca7','ca8','ca9','ca10','ca11','cadc']

	dataDirName = os.path.join('..','Data','stmCSV')

	outFileName = os.path.join('..','Results','panelBiasResults','panelCompositionResults.txt')

	yearRange = range(1970,2011)

	helpers.maybeMakeDirStructure(os.path.join('..','Results','panelBiasResults'))
	
	runExpectedCompAnalysis(judgeFileName,circList,dataDirName,outFileName,yearRange)
	
	
