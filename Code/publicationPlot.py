import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
import os
import helpers


#this code will make the figure showing the publication rate of each circuit which is in the paper
def createPublicationRatePlot(dataFileName, outFigureDirName, outFigureFileName):

	#make the directory to hold our figure if needed
	helpers.maybeMakeDirStructure(outFigureDirName)
	outFigureFileName = os.path.join(outFigureDirName,outFigureFileName)

	with open(dataFileName,'rb') as metaFileRaw:
		metaFile = csv.reader(metaFileRaw)
		headers = metaFile.next()
		circDict = {}

		#read the data from the file and populate a dictionary mapping each circuitName to a dictionary 
		#which maps each year to the pct of cases published that year
		for line in metaFile:
			circName = line[headers.index('circuitf')]
			if circName not in circDict:
				circDict[circName] = {}

			year = line[headers.index('year')]
			pubPct = line[headers.index('pubpct')]
			
			circDict[circName][year] = pubPct

	#set the colors and line styles for each circuit so they can be distinguished in the plot
	circOrder = ['1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','DC']
	lineOptions = ['-','--','-','--','-.','-',':','-','-',':',':','-.']
	lineColors = ['#000000','#888888','#000000','#000000','#888888','#444444','#444444','#888888','#888888','#444444','#444444','#888888']
	plt.figure(figsize=(10,8))
	i =0
	for circ in circOrder:
		x = []
		y =[]
		#draw the lines
		for year in sorted(circDict[circ].keys()):
			x.append(int(year) )
			y.append(float(circDict[circ][year]))
		plt.plot(x, y, lineOptions[i],color=lineColors[i])

		#adjust the labels on the right side up and down a bit to have them not overlap too much
		if circ=='2nd':
			plt.text(x[-1], y[-1]+2.5, circ)
		elif circ=='5th':
			plt.text(x[-1], y[-1]+1, circ)
		elif circ=='9th':
			plt.text(x[-1], y[-1]+.5, circ)
		else:
			plt.text(x[-1], y[-1], circ)
		i+=1
	plt.xticks([2000,2005,2010])
	plt.ylabel('Publication Rate') 
	plt.tight_layout()

	#finally save the figure
	plt.savefig(outFigureFileName,dpi=500)

if __name__ == "__main__":
	dataFileName = os.path.join('..','Data', 'uscaopsData01.csv')
	outFigureDirName = os.path.join('..','Results','Figures')
	outFigureFileName = 'figure2.png'

	createPublicationRatePlot(dataFileName,outFigureDirName,outFigureFileName)