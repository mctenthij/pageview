#!/usr/bin/python
from datetime import datetime, timedelta
from time import mktime
import re

from pattern import PromotionPattern
from download import Downloader
from util import loadUrl

class Retriever:
	def __init__(self, start, end, patterns=[]):
		self.start = start
		self.current = datetime(self.start.year,self.start.month,self.start.day,0,0,0)
		self.end = end
		self.patterns = patterns


	def addPattern(self,pattern):
		self.patterns.append(pattern)

	def getArticles(self):
		for i in range(len(self.patterns)):
			self.patterns[i].getArchive(self.start,self.end)
		# for pattern in self.patterns:
		# 	pattern.getArchive(self.start,self.end)

	def run(self):
		while self.current < self.end:
			self.printCurrent()
			
			# Load pageview data
			artDict = self.buildArtDict()
			print artDict

			# Process pageview data
			dl = Downloader(self.current,self.current+timedelta(days=1))
			dl.run(artDict)

			self.updateCurrentTime()

	def buildArtDict(self):
		artDict = {}
		for pattern in self.patterns:
			tempList = []
			artDict[pattern.lang] = []

			# add MP to list
			MPList = self.buildMPList(pattern)
			artDict[pattern.lang] += MPList

			# add pattern pages to list
			artList = self.buildArtList(pattern)
			artDict[pattern.lang] += artList
		
		return artDict

	def buildMPList(self,pattern):
		res = re.findall('<link rel="canonical" href="([!:,-.()%/\w\s]*)" />',loadUrl("https://" + pattern.lang + ".wikipedia.org").read(),flags=re.UNICODE)
		return [res[0].split("/")[-1]]

	def buildArtList(self,pattern):
		artList = []
		for day in pattern.relativeDays:
			artList += self.addArticles(self.current+timedelta(days=day),pattern.arch.articles)

		tempList = []
		for art in artList:
			tempList.append(pattern.arch.articleTitleToURL[art])

		return tempList
	
	def addArticles(self,day,articles):
		tempList = []
		strfDate = day.strftime("%B %d, %Y")
		for art in articles:
			if articles[art] == strfDate:
				if art != None:
					tempList.append(art)
		return tempList

	def updateCurrentTime(self):
		self.current+=timedelta(days=1)

	def setCurrent(self,dt_obj):
		self.current = dt_obj
	
	def printCurrent(self):
		print self.current
		with open('progress.txt','a') as temp:
				temp.write(self.current.strftime("%Y-%m-%d %H")+'h is now being processed\n')