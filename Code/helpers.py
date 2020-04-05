import os
import judgeClass
from unidecode import unidecode
import re
#contains methods which are generally useful for our analysis and are referenced by multiple files.  Not meant to be run directly


#checks if path dirPath exists and if not makes it and any higher level directories needed
def maybeMakeDirStructure(dirPath):
	if not os.path.exists(dirPath):
		os.makedirs(dirPath)

#create a list of every opinion file in the circuits in the list
def createOpinionFileList(baseOpinionDir,circuitList):

	allFilesList = []
	for circuit in circuitList:
		opinionDir = os.path.join(baseOpinionDir, circuit)
		for file in os.listdir(opinionDir):
			allFilesList.append(os.path.join(opinionDir,file))
	return allFilesList


#reads in the csv file judgeFileName
#For every judge in the file who served on the circuit specified by circuitName
#we create an instance of judge class and append it to a list of all such judges
#return this list
def makePotentialJudgesList(circuitName, judgeFileName):

	judgeList = []
	#populate the list of potential judges for this circuit
	with open(judgeFileName,'r') as judgeFile:
	
		#circuits are named differently in auburn data, convert
		circuitNameInCSV = circuitName[2:]
		if circuitNameInCSV == 'dc':
			circuitNameInCSV = '12'

		for line in judgeFile.readlines()[1:]:
			lineJudge = judgeClass.judge(line)
			if lineJudge.circuit == circuitNameInCSV:
				judgeList.append(judgeClass.judge(line))
	return judgeList


#looks through file text and identifies the judges on the case
#it considers the judges in judgeList(who should only be judges from the circuit of this case) who were active within 1 year of fileYear
def findJudges(fileText, judgeList, fileYear, windowSize=30):
	ignoreJudgeWords= ['circuit','judge','judges','u.s','court','of','for','customs','patent','appeals','united','states','district','southern','northern','eastern','western']
	
	#find all judges who were active during this cases year that we should consider searching for
	potentialFileJudges = [judge for judge in judgeList if judge.start <= fileYear+1 and judge.end >=fileYear-1]

	fileText = unidecode(fileText).lower()

	#normalize the text used to announce judges
	fileText = fileText.replace("present:",'before').replace('b e f o r e','before').replace('before:','before')

	#remove the ignored words from the text
	myRegex = re.compile(r'\b%s\b' % r'\b|\b'.join(map(re.escape, ignoreJudgeWords)))
	fileText = myRegex.sub("", fileText)

	#replace tab, newline, to make splitting easier
	fileText = fileText.replace('\t',' ').replace('\n',' ')

	#put a space before these brackets that are used to mark notes and around commas, semicolons, asterisks, and parentheses
	fileText = fileText.replace('[',' [').replace(',',' , ').replace(';',' ; ').replace('(',' (').replace('*',' * ')

	#replace multiple consecutive spaces with just one
	fileText = re.sub( '\s+', ' ', fileText ).strip()

	words = fileText.split(' ')

	fileJudges = []

	
	for i in range(len(words)-windowSize):
				consideredWords = words[i:i+windowSize]
				
				#should start with our now standardized "before" word
				if 'before' == consideredWords[0]:
					
					#end window early if they seem to be getting into the case
					if 'order' in consideredWords:
						consideredWords= consideredWords[:consideredWords.index('order')]
					if 'opinion' in consideredWords:
						consideredWords= consideredWords[:consideredWords.index('opinion')]
					
					#end window early if a period seems to be ending the sentence
					for posEndWord in consideredWords:
						if posEndWord[-1] == '.' and (len(posEndWord)>2 or len(posEndWord)==1) and posEndWord.count('.') == 1:
							consideredWords = consideredWords[:consideredWords.index(posEndWord)]
							break

					##find overlap of text and potential judges
					foundJudges = []
					

					for wordIndex in range(len(consideredWords)):
						word = consideredWords[wordIndex]

						#make sure that this name/word is right before a comma or 'and', otherwise we may confuse
						#the first name of a judge for the last name of a different judge and add the wrong one
						if wordIndex+1< len(consideredWords) and consideredWords[wordIndex+1] not in [',','and']:
							continue
						for judge in potentialFileJudges:
							if word == judge.lastName and judge not in foundJudges:
								foundJudges.append(judge)

									
						

					###if there are two potential judges with the same last name try to figure out which of them is actually on the case
					for first in foundJudges:
						for second in foundJudges:
							if first!=second and first.lastName == second.lastName and consideredWords.count(first.lastName) <2:
								
								#we will consider the word before the confusing last name
								prevWord = consideredWords[consideredWords.index(first.lastName)-1]
								secondPrev = ""

								#if there are two words before the confusing name we will consider the word 2 before it as well
								if consideredWords.index(first.lastName) >1:
									secondPrev = consideredWords[consideredWords.index(first.lastName)-2]
								
								#if the word before is the name or first initial of one of the judges get rid of the other
								if prevWord.replace('.','')==first.firstName or prevWord.split('.')[0] == first.firstName[0]:
									foundJudges.remove(second)
								elif prevWord.replace('.','')==second.firstName or prevWord.split('.')[0] == second.firstName[0]:
									foundJudges.remove(first)

								#else if the word 2 spaces before is the first name or initial of a judge get rid of the other
								elif secondPrev.replace('.','')==first.firstName or secondPrev.split('.')[0] == first.firstName[0]:
									foundJudges.remove(second)
								elif secondPrev.replace('.','')==second.firstName or secondPrev.split('.')[0] == second.firstName[0]:
									foundJudges.remove(first)

								#otherwise just take whatever judge started earlier, since they aren't bothering to specify 
								#which of them it is, its usually because the later judge wasn't around yet
								elif first.start<second.start:
									foundJudges.remove(second)
								else:
									foundJudges.remove(first)

					##We will eventually use the window which produced the highest number of judge names
					##if this is more judges that we had associated with the file, use the current window
					if len(foundJudges)>len(fileJudges):
						fileJudges=foundJudges
						

	return fileJudges
