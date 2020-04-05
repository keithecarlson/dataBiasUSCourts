import json
import os
from bs4 import BeautifulSoup
import helpers
import sys
from unidecode import unidecode
import re
import string

#This class holds information associated with a single case in our corpus
#it extracts this info from the json file opinionFileName in opinionDir and the associated json cluster File in clusterDir

class case(object):
   
	def __init__(self,opinionFileName, circuitNum, opinionDir, clusterDir):

		with open(os.path.join(opinionDir,opinionFileName)) as opinionFile:
			opinionData = json.load(opinionFile)

			#when we initialize an instance: populate opinionFileName and circuitNum
			self.opinionFileName = opinionFileName
			self.circuitNum = circuitNum
			html = opinionData['html']
			lawbox = opinionData['html_lawbox']
			columbia = opinionData['html_columbia']
			htmlCitations =opinionData['html_with_citations']

			#assign html to soup if any of the html fields are populated
			self.soup = None
			if html != None and len(html) > 10:
				self.soup = BeautifulSoup(html,'lxml')
				
			elif lawbox != None and len(lawbox) >10:
				self.soup = BeautifulSoup(lawbox,'lxml')
				
			elif columbia != None and len(columbia) >10:
				self.soup = BeautifulSoup(columbia,'lxml')

			elif htmlCitations != None and len(htmlCitations) >10:
				self.soup = BeautifulSoup(htmlCitations,'lxml')

			#create empty placeholders for caseJudges,USParty,corpParty,cleanText
			self.caseJudges = None
			self.USParty = None
			self.corpParty = None
			self.cleanText = None

			#check if the cluster this opinion claims is associated with it actually exists and store boolean value in validCluster.
			self.validCluster = False
			clusterFileName = opinionData['cluster'].split('/')[-2]+'.json'
			if os.path.exists(os.path.join(clusterDir,clusterFileName)):
				self.validCluster = True
				with open(os.path.join(clusterDir,clusterFileName)) as clusterFile:

					clusterData = json.load(clusterFile)

					#if the cluster actually existed extract federal citation number, precedential status, data, and name of the case from it
					self.fedCite = clusterData['federal_cite_one']
					self.precedential = (clusterData['precedential_status'] == 'Published')
					self.yearFiled = int(clusterData['date_filed'].split('-')[0])
					caseName= clusterData['case_name']
					fullCaseName = clusterData['case_name_full']

					#For name of the case, we prefer the longer form of case_name_full, but if it is not populated we will use case_name
					if fullCaseName != None and len(fullCaseName) > 3 :
						self.caseTitle = fullCaseName
					else:
						self.caseTitle = caseName


	def __str__(self):
		return str(self.opinionFileName) + ' Title: ' + str(self.caseTitle) + ' Judges: ' + str(self.caseJudges) +' Year: ' +str(self.yearFiled) + ' Circuit: ' +str(self.circuitNum)
	def __repr__(self):
		return str(self.opinionFileName) + ' Title: ' + str(self.caseTitle) + ' Judges: ' + str(self.caseJudges) +' Year: ' +str(self.yearFiled) + ' Circuit: ' +str(self.circuitNum)
	
	#uses cleanText and judgeList to try to find the judges on this case.  Requires assignCleanText to have already been run
	def assignJudges(self, judgeList):
		self.caseJudges = helpers.findJudges(self.cleanText, judgeList, self.yearFiled)

	#uses the title of the case to identify if the US is one of exactly two parties involved in the case
	def assignUSParty(self):
		self.USParty = False
		caseBetween = self.caseTitle.split(' v. ')
		stripPunctRE = re.compile('[%s]' % re.escape(string.punctuation))
		if len(caseBetween) == 2:
			
			if (stripPunctRE.sub(' ',caseBetween[0].strip().lower()) == 'united states' or stripPunctRE.sub(' ',caseBetween[0].strip().lower()) == 'united states of america' or 
						stripPunctRE.sub(' ',caseBetween[1].strip().lower()) == 'united states' or stripPunctRE.sub(' ',caseBetween[1].strip().lower()) == 'united states of america' ):
				self.USParty = True

	#uses title of the case to identify if a corporation is a party on the case
	def assignCorpParty(self):
		self.corpParty =  False
		corpTitleWords =['llc','inc','incorporated','co','corp','corporation','ltd','llp','company']

		stripPunctRE = re.compile('[%s]' % re.escape(string.punctuation))
		cleanCaseTitle = stripPunctRE.sub(' ',self.caseTitle.lower())
		cleanTitleWords = cleanCaseTitle.split(' ')

		if len([word for word in corpTitleWords if (word in cleanTitleWords or word+'.' in cleanTitleWords)]) >0:
			self.corpParty = True

	#creates a plain text version of the opinion's html and stores it in cleanText
	def assignCleanText(self):
		self.cleanText = self.soup.get_text().strip()

	#goes through clean text and removes all occurrences of the names of U.S. states, judges, 'united','states','america', and corporation words from the case.  
	#Removes only if they appear as a whole word or followed by an "'s" (which covers possessive usage)
	#requires assignCleanText to have been run
	def removeTargetWordsFromText(self):
		judgeLastNames = [j.lastName.lower() for j in self.caseJudges]
		judgeFirstNames = [j.firstName.lower() for j in self.caseJudges]
		judgeNames = judgeFirstNames+judgeLastNames 
		usWords = ['united','states','america']
		corpWords = ['llc','inc','incorporated','co','corp','corporation','ltd','llp','company']

		stateNames = ['alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'florida', 'georgia', 
						'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts', 
						'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'new hampshire', 'new jersey', 
						'new mexico', 'new york', 'north carolina', 'north dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode island', 
						'south carolina', 'south dakota', 'tennessee', 'texas', 'utah', 'vermont', 'virginia', 'washington', 'west virginia', 
						'wisconsin', 'wyoming','columbia']

		targetWords = judgeNames+usWords+corpWords+stateNames

		cleanWordList = re.split('(\s|,|\.)+',self.cleanText)
		stripPunctRE = re.compile('[%s]' % re.escape(string.punctuation))
		remainingWords = []

		#go through the text one word at a time
		for wordInd in range(len(cleanWordList)):
			curWord = cleanWordList[wordInd]

			#strip off "'s" if its there
			if len(curWord) >2 and curWord[-2:] =='\'s':
				curWord=curWord[:-2]

			#replace all punctuation and remove any whitespace
			curWord = stripPunctRE.sub('',curWord.lower()).replace(' ','')

			#if the word isn't one we want to remove
			if curWord not in targetWords:
				if wordInd<len(cleanWordList)-1:

					#grab the next word too, so we can check for two word state names
					nextWord = cleanWordList[wordInd+1]

					#strip off "'s" if its there
					if len(nextWord) >2 and nextWord[-2:] =='\'s':
						nextWord=nextWord[:-2]

					nextWord = stripPunctRE.sub('',nextWord.lower()).replace(' ','')
				#and if the combination of the word and the next word isn't in our list
				if wordInd>=len(cleanWordList)-1 or curWord + ' ' + nextWord not in targetWords:
					#add the word to our "kept" words list
					remainingWords.append(cleanWordList[wordInd])
		self.cleanText = ' '.join(remainingWords)
		self.cleanText = re.sub(' +',' ', self.cleanText)


	#returns number of bytes that would be in a file containing cleanText
	def getTextSize(self):
		return sys.getsizeof(unidecode(self.cleanText))

	#returns a list of the parties of the judges
	def getJudgePartiesList(self):
		fileParties = []
		for judge in self.caseJudges:
			fileParties.append(judge.party)
		return fileParties

	#returns a string of the names of the judges
	def getJudgeNames(self):
		fileJudgeNames = ''
		for judge in self.caseJudges:
			fileJudgeNames += judge.lastName+ ' ' + judge.firstName +', '
		return fileJudgeNames[:-2]

