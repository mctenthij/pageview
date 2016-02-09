#!/usr/bin/python
import re
from datetime import datetime, timedelta
import os
import locale

from dateutils import relativedelta
import dateparser
from pycountry import languages

from util import loadUrl

class Archive:
	'''Scrapes the featured articles and the on this day articles from Wikipedia, for the given time period.'''

	def __init__(self,start,end,pattern,title):
		'''archive is constructed by two datetime objects, that indicate the beginning and the end of the period that must be scraped.'''
		self.start = start
		self.end = end
		self.title = title
		self.current = datetime(self.start.year,self.start.month,self.start.day,0,0,0)
		self.filename = title.lower()+"_"+start.strftime("%B_%Y")+"-"+end.strftime("%B_%Y")
		self.scrapePattern = pattern
		self.articles = {}
		self.articleTitleToURL = {}
		if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/arc"):
			os.makedirs(os.path.dirname(os.path.abspath(__file__))+"/arc")

	def getArticles(self):
		'''Checks if the required archive is already scraped. If it already scraped, it opens the archive file, else it makes one.'''
		if os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/arc/wiki_titles_"+self.filename+".txt"):
			self.extractArchive(os.path.dirname(os.path.abspath(__file__))+"/arc/wiki_titles_"+self.filename+".txt")
		else:
			if self.scrapePattern.archLink:
				self.getPages()
				self.makeOutput()

	def getPages(self):
		while self.current<self.end:
			self.loadPage()
			self.updateCurrent()
	
		self.resetCurrent()
		self.checkMissedDates()

	def loadPage(self):
		adress = self.scrapePattern.getArchiveLink(self.current)
		print adress
		response = loadUrl(adress)

		self.searchPatterns(response)	
	
	def checkMissedDates(self):
		with open(os.path.dirname(os.path.abspath(__file__))+"/arc/missed_pages_"+self.filename+".txt","ab") as outFile:
			datearray = []
			for art in self.articles:
				datearray.append(datetime.strptime(self.articles[art],"%B %d, %Y"))
			
			cur = datetime(self.start.year,self.start.month,self.start.day,0,0,0)
			while cur<self.end:
				if cur not in datearray:
					outFile.write(self.title+"\t"+cur.strftime("%B %d, %Y")+"\n")

				cur += timedelta(days=1)

	def makeOutput(self):
		with open(os.path.dirname(os.path.abspath(__file__))+"/arc/wiki_titles_"+self.filename+".txt", 'wb') as outFile:
			for article in self.articleTitleToURL:
				outFile.write("featured" + "\t" + self.articles[article] + "\t" + self.articleTitleToURL[article] + "\t" + article + "\n")
				
	def searchPatterns(self,source):
		res = re.findall(self.scrapePattern.pattern,source.read(),flags=re.UNICODE)
		if res is not None:
			if self.scrapePattern.lang == "es":
				for item in res:
					dt = dateparser.parse(item[2]+" "+str(self.current.year),languages=[self.scrapePattern.lang],date_formats=[self.scrapePattern.archTime_fmt])
					if dt != None: # Possible that day does not exist (e.g. 29 February 2015)
						self.articles[item[1]] = dt.strftime("%B %d, %Y")
						self.articleTitleToURL[item[1]] = item[0]
			else:
				for item in res:
					if "%Y" not in self.scrapePattern.archTime_fmt:
						dt = dateparser.parse(item[0]+" "+str(self.current.year),languages=[self.scrapePattern.lang],date_formats=[self.scrapePattern.archTime_fmt])
					else:
						dt = dateparser.parse(item[0],languages=[self.scrapePattern.lang],date_formats=[self.scrapePattern.archTime_fmt])
					if dt != None: # Possible that day does not exist (e.g. 29 February 2015)
						self.articles[item[2]] = dt.strftime("%B %d, %Y")
						self.articleTitleToURL[item[2]] = item[1]


	def updateCurrent(self):
		if "%B" in self.scrapePattern.archLink_fmt:
			self.current += relativedelta(months=1)
		else:
			self.current += relativedelta(years=1)

	def resetCurrent(self):
		self.current = datetime(self.start.year,self.start.month,self.start.day,0,0,0)

	def extractArchive(self,archivePath):
		with open(archivePath,"rb") as archive:
			for line in archive:
				cols = line.strip('\r\n').split("\t")
				self.articleTitleToURL[cols[3]] = cols[2]
				self.articles[cols[3]] = cols[1]