import matplotlib
matplotlib.use('Agg')
import pandas as pd
import os
import random
import statsmodels.api as sm
import matplotlib.pyplot as plt
from patsy import dmatrices
import numpy as np
from scipy.interpolate import UnivariateSpline
import scipy.stats

random.seed(12345)
np.random.seed(12345)


#reads dataFileName, which should be the file created by createSingleDataFile.py
#for each year from 1970 through 2010 it looks at all data from that year and the year preceding and following it
#runs a logistic regression on the data predicting USParty from the number of democrats on the panel and the circuit
#keeps three dictionaries(keyed by year) of the estimated effect of demCount and of the upper and lower 95% CIs
#also keeps a list of the p-vals.
#writes the results of the years which showed at least a borderline significant effect to Results/USPartyWindowLogitResults.txt
#also writes results of combining all of the pvalues using fisher's combined probability test
#then creates a figure showing the point estimates of the effect of demCount over time, as well as smoothed versions of the
#point estimate and CIs and saves the figure to Results/Figures/figure4.png
def runWindowRegressions(dataFileName):
	loadedData = pd.read_csv(dataFileName,index_col=0)
	loadedData['USParty'] = (loadedData['USParty']).astype(int)
	estDict = {}
	lowerDict={}
	upperDict = {}
	pVals=[]

	with open(os.path.join('..','Results','USPartyWindowLogitResults.txt'),'w') as resultsFile:
		for year in range(1970,2011):
			#use data from this year, and the one before and after
			myData = loadedData.loc[loadedData['year'].isin([year-1,year,year+1]) ]

			y, X = dmatrices('USParty' +' ~ demCount +C(circuit)', myData, return_type="dataframe")
			y = np.ravel(y)

			#run the logistic regression
			logit = sm.Logit(y, X)
			result = logit.fit(disp=0)

			#add the results to our dictionaries and list
			pVals.append(result.pvalues['demCount'])
			estDict[year] = result.params['demCount']
			lowerDict[year] = result.conf_int(.05)[0]['demCount']
			upperDict[year] = result.conf_int(.05)[1]['demCount']

			#if this year is at least borderline significant, output to file
			if result.pvalues['demCount'] < .1:
				resultsFile.write('\nNumber of democrats was predictive of USparty at the .1 level in ' + str(year) )
				resultsFile.write('\n' + str(result.summary()) +' \n')

			
		#use fishers combined probability test to see if the pvalues, viewed as a single experiment show significance
		statistic,combP = scipy.stats.combine_pvalues(pVals)

		resultsFile.write("\n\nCombining all p-values gives p-value of: " + str(combP))

	createWindowLogitFigure(estDict,lowerDict,upperDict)


#create a figure showing the point estimates of the effect of demCount over time, as well as smoothed versions of the
#point estimate and CIs and saves the figure to Results/Figures/figure3b.png
def createWindowLogitFigure(estDict,lowerDict,upperDict):

	plt.figure(figsize=(10,8))
	lists = sorted(estDict.items())
	x, y = zip(*lists) 
	plt.plot(x, y, 'k',alpha=0.4)
	f= UnivariateSpline(x, y, s=.1)
	plt.plot(x, f(x),'k')

	lowerLists =  sorted(lowerDict.items())
	lowerX, lowerY = zip(*lowerLists) 
	lowerF= UnivariateSpline(lowerX, lowerY, s=.1)
	plt.plot(lowerX, lowerF(lowerX),'k--')

	upperLists =  sorted(upperDict.items())
	upperX, upperY = zip(*upperLists) 

	upperF= UnivariateSpline(upperX, upperY, s=.1)
	plt.plot(upperX, upperF(upperX),'k--')

	plt.savefig(os.path.join('..','Results','Figures','figure4.png'),dpi=500)


if __name__ == "__main__":  

	inFileName = os.path.join('..','Data','lustrumDemCountDataAllCircuits.csv')

	runWindowRegressions(inFileName)