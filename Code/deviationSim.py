import matplotlib
matplotlib.use('Agg')
import pandas as pd
import os
import random
import scipy.stats
import numpy as np
import matplotlib.pyplot as plt

random.seed(12345)
np.random.seed(12345)


#reads the dataFileName, which should be the file created by createSingleDataFile.py
#Returns 7 dictionaries, all with circuit-years as keys
#The values of the dictionaries are the number of documents in that circuit year:
#total, with USParty, with DMP, with USParty and DMP, with USParty and no DMP, with no USParty and DMP, and with no USParty and no DMP respectively
def findCircYearObs(dataFileName):

	loadedData = pd.read_csv(dataFileName,index_col=0)

	totalCounts = {}
	UScounts = {}
	USDMPCounts = {}
	DMPCounts = {}

	USNoDMPCounts = {}
	nonUSDMPCounts = {}
	nonUSnoDMPCounts = {}
	for index, row in loadedData.iterrows():

		circYear = str(row['circuit']) +'-'+ str(int(row['year']))
		if circYear not in totalCounts:
			totalCounts[circYear] = 0
			UScounts[circYear] = 0
			USDMPCounts[circYear] = 0
			DMPCounts[circYear] = 0


			USNoDMPCounts[circYear] = 0
			nonUSDMPCounts[circYear] = 0
			nonUSnoDMPCounts[circYear] = 0

		totalCounts[circYear] += 1
		if str(row['USParty']).lower() == 'true':
			UScounts[circYear] += 1

			if int(row['demCount']) > 1:
				USDMPCounts[circYear] += 1
			else:
				USNoDMPCounts[circYear] +=1
		else:
			if int(row['demCount']) > 1:
				nonUSDMPCounts[circYear] += 1
			else:
				nonUSnoDMPCounts[circYear] +=1

		if int(row['demCount']) > 1:
				DMPCounts[circYear] += 1

	return totalCounts, UScounts, DMPCounts, USDMPCounts, USNoDMPCounts, nonUSDMPCounts, nonUSnoDMPCounts



#takes the dictionaries created by findCircYearObs and an open file object to write to as inputs
#goes through all circuit-years.  For each with at least 50 cases of each  US, nonUS, DMP, and non DMP
#Builds the 2x2 contingency table of USParty and DMP, then runs fisher's exact test on it
#outputs to the file, the number of circuit-years that are significant at various levels
#also outputs the combined p-value of all of them
def exactTestCircYears(totalCounts, UScounts, DMPCounts, USDMPCounts, USNoDMPCounts, nonUSDMPCounts, nonUSnoDMPCounts, outFileName):
	
	allExPVS = []

	#go through each circuit-year
	for circYear in totalCounts:

		#skip circ-years with too few cases
		if UScounts[circYear] < 50 or DMPCounts[circYear] < 50 or (totalCounts[circYear] - UScounts[circYear]) < 50 or (totalCounts[circYear] - DMPCounts[circYear]) < 50:
			continue

		#build contingency table
		contTable = [[USDMPCounts[circYear],USNoDMPCounts[circYear]],[nonUSDMPCounts[circYear],nonUSnoDMPCounts[circYear]]]

		#run exact test
		exStat, exPV = scipy.stats.fisher_exact(contTable)
		allExPVS.append(exPV)

	#output results
	outFile.write('Fisher\'s exact test on these circuit-years shows bias in:\n')
	outFile.write(str(len([ptemp for ptemp in allExPVS if ptemp <.05])) + " at p=.05\n")
	outFile.write(str(len([ptemp for ptemp in allExPVS if ptemp <.01])) + " were significant at p=.01\n")
	outFile.write(str(len([ptemp for ptemp in allExPVS if ptemp <.001])) + " were significant at p=.001\n\n")

	#combine p-values and output
	excombP = scipy.stats.combine_pvalues(allExPVS)
	outFile.write('Combining these exact test p-values gives a value of ' + str(excombP))
	
	
#takes the dictionaries created by findCircYearObs, the number of simulations to run for each circ-year,
#an open file object to write to, and the name to be used for the created figure as inputs
#goes through all circuit-years.  For each with at least 50 cases of each  US, nonUS, DMP, and non DMP
#runs numSim iterations of permuting the USParty and DMP labels of the cases randomly
#counts the resulting number of USDMP cases and uses all of these results to find an expected mean
#and standard deviation of the number of USDMP cases in the circ-year if there was no correlation
#Calculates how many standard deviations away from expected each circuit-year is
#Does a KS test of these results against a normal distribution and outputs the results to outFile
#also creates a figure showing the results called outFigureName
def simPermutations(totalCounts, UScounts, DMPCounts, USDMPCounts, USNoDMPCounts, nonUSDMPCounts, nonUSnoDMPCounts, numSim, outFile, outFigureName):

	allDeviations = []
	#go through each circuit-year
	for circYear in totalCounts:
		#skip circ-years with too few cases
		if UScounts[circYear] < 50 or DMPCounts[circYear] < 50 or (totalCounts[circYear] - UScounts[circYear]) < 50 or (totalCounts[circYear] - DMPCounts[circYear]) < 50:
			continue

		simUSDMPCounts = []

		#simulate US and DMP overlap numSim times
		for sim in range(numSim):

			#create lists of 1's and 0's.  The lists have 1 entry for each case in the circuit year.
			#a 1 corresponds to USParty or DMP and a 0 to its absence
			USInds = [1] * UScounts[circYear] + [0] * (totalCounts[circYear] - UScounts[circYear])
			DMPInds = [1] * DMPCounts[circYear] + [0] * (totalCounts[circYear] - DMPCounts[circYear])
			#shuffle these lists for the simulation
			random.shuffle(USInds)
			random.shuffle(DMPInds)

			#recalculate the number of US DMP cases in this simulation
			simUSDMP = sum([1 for i in range(len(USInds)) if USInds[i] == 1 and DMPInds[i]==1])
			
			#add it to the circ-years list of simulation results
			simUSDMPCounts.append(simUSDMP)


		#calculate the standard deviation and mean of the number of USDMP cases in the simulations
		simSD = np.std(simUSDMPCounts)
		simMean = np.mean(simUSDMPCounts)

		#calculate how many standard deviations away from the mean the actual observed number of USDMP cases was
		deviationsAway = (USDMPCounts[circYear] - simMean)/simSD

		#record the number of deviations away for this circuit year
		allDeviations.append(deviationsAway)

	#compare the results of the deviations away for all tested circ-years to the normal distribution
	#outputu the results to outFile
	outFile.write('Tested ' + str(len(allDeviations)) + ' circuit-years.\n')
	ksResult = scipy.stats.kstest(allDeviations, 'norm')
	outFile.write('KS test of the number of deviations away from expected in observed data using simulations to calculate expected mean and standard deviation ' +
				'give a p-value of ' + str(ksResult) + '\n\n')


	#create a figure showing the results of these simulations
	makeDevGraph(allDeviations,outFigureName)
	
#creates a histogram showing the number of standard deviations away from expected the circuit-years were
#takes the list of number of deviations as input
#also shows a normal distribution for comparison
#Saves the figure as figureOutName
def makeDevGraph(allDeviations, outFigureName):

	plt.figure(figsize=(10,8))
	binCuts = [-5.0 + x * 0.25 for x in range(0, 41)]

	barSizes,bins,patches = plt.hist(allDeviations, bins=binCuts, density = True, alpha=0.5, facecolor='gray', edgecolor='gray')

	x_axis = np.arange(-5, 5, 0.001)

	plt.plot(x_axis, scipy.stats.norm.pdf(x_axis,0,1), color='black')

	plt.grid(True)
	
	plt.savefig(outFigureName,dpi=500)


if __name__ == "__main__":  

	inFileName = os.path.join('..','Data','lustrumDemCountDataAllCircuits.csv')

	outFileName = os.path.join('..','Results','USandDMPTestResults.txt')

	outFigureName = os.path.join('..','Results','Figures','figure3.png')

	totalCounts, UScounts, DMPCounts, USDMPCounts, USNoDMPCounts, nonUSDMPCounts, nonUSnoDMPCounts = findCircYearObs(inFileName)

	numSim = 1000

	with open(outFileName, 'w') as outFile:
		allDeviations = simPermutations(totalCounts, UScounts, DMPCounts, USDMPCounts, USNoDMPCounts, nonUSDMPCounts, nonUSnoDMPCounts, numSim, outFile, outFigureName)

		exactTestCircYears(totalCounts, UScounts, DMPCounts, USDMPCounts, USNoDMPCounts, nonUSDMPCounts, nonUSnoDMPCounts, outFileName)

