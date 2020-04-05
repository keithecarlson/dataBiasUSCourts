#This is a simple class definition to hold information about each judge.  Is used by other files, and is not to be run directly.

class judge(object):
   #initialized using a "line".  This should be a line from the .csv file produced by judgeMetaDataExtractor.py
	def __init__(self,line):
		parts = line.strip().split(',')
		self.circuit = parts[1]
		self.start = int(parts[3])
		self.end = int(parts[4])
		self.party = parts[2]
		self.fullName = parts[0]
		self.lastName = parts[0].split('<')[0].lower()
		self.firstName =  parts[0].split('<')[1].lower().strip().split(' ')[0]
	def __str__(self):
		return self.fullName + ' Circuit: ' + self.circuit + ' Party: ' + self.party +' Start: ' +str(self.start) + ' End: ' +str(self.end)
	def __repr__(self):
		return self.fullName + ' Circuit: ' + self.circuit + ' Party: ' + self.party +' Start: ' +str(self.start) + ' End: ' +str(self.end)

