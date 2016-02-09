#!/usr/bin/python
import os
from calendar import timegm
from datetime import datetime, timedelta
from time import mktime, sleep
import gzip
from urllib2 import urlopen, HTTPError

from pycountry import languages

class Downloader:
	def __init__(self,start,end):
		if not isinstance(start,datetime):
			try:
				start = datetime.fromtimestamp(mktime(start))
			except TypeError:
				raise TypeError('start must be a time or datetime.datetime object')
		elif not isinstance(end,datetime):
			try:
				end = datetime.fromtimestamp(mktime(end))
			except TypeError:
				raise TypeError('end must be a time or datetime.datetime object')

		self.start = start
		self.end = end
		if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/pv"):
			os.makedirs(os.path.dirname(os.path.abspath(__file__))+"/pv")
		if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/.tmp"):
			os.makedirs(os.path.dirname(os.path.abspath(__file__))+"/.tmp")

	def run(self,artDict):
		for lang in artDict:
			try:
				languages.get(iso639_1_code=lang)
			except KeyError:
				raise KeyError('Language "'+lang+'" does not exist')

		current = datetime(self.start.year,self.start.month,self.start.day,self.start.hour,0,0)
		while current < self.end:
			results = processFile(current,artDict)
			makeOutput(current,results)

			current += timedelta(hours=1)

def downloadFile(dtobj,attempt):
	url = "http://dumps.wikimedia.org/other/pagecounts-raw/%(year)i/%(year)i-%(month)02i/pagecounts-%(year)i%(month)02i%(day)02i-%(hour)02i%(attempt)04i.gz" % {"year": dtobj.year, "month": dtobj.month, "day": dtobj.day, "hour": dtobj.hour, "attempt": attempt}
	try:
		test = urlopen(url)
		print "Downloading pagecounts-%(year)i%(month)02i%(day)02i-%(hour)02i%(attempt)04i.gz" % {"year": dtobj.year, "month": dtobj.month, "day": dtobj.day, "hour": dtobj.hour, "attempt": attempt}
		data = test.read()
		outFile = ".tmp/pagecounts-%(year)i%(month)02i%(day)02i-%(hour)02i%(attempt)04i.gz" % {"year": dtobj.year, "month": dtobj.month, "day": dtobj.day, "hour": dtobj.hour, "attempt": attempt}
		with open(outFile, "wb") as code:
		    code.write(data)
	except HTTPError as e:
		if attempt > 100:
			return ""
		else:
			sleep(2)
			outFile = downloadFile(dtobj,attempt+1)
	
	return outFile

def removeFile(filename):
	try:
		os.remove(filename)
	except IOError:
		pass

def processFile(dtobj,artDict):
	filename = downloadFile(dtobj,0)
	results = {}

	if filename != "":
		for lang in artDict:
			results[lang] = {}
			results[lang]["total"] = 0
		try:
			with gzip.open(filename,"rb") as test:
				for line in test:
					try:
						# FORMAT of line
						# lang page_title views bytes_transfered
						cols = line.strip('\n').split(' ')
						if cols[0] in artDict:
							results[cols[0]]["total"] += int(cols[2])
							if cols[1] in artDict[cols[0]]:
								if cols[1] in results[cols[0]]:
									results[cols[0]][cols[1]] += int(cols[2])
								else:
									results[cols[0]][cols[1]] = int(cols[2])
					except (ValueError,IndexError) as e:
						pass
		except IOError:
			pass

		removeFile(filename)
	print "Processed " + filename
	return results

def makeOutput(current,results):
	"""
	Outputs page-view counts to file. Lines follow the following format:
	timestamp	article_name	page-view count
	"""
	for lang in results:
		if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/pv/"+lang):
			os.makedirs(os.path.dirname(os.path.abspath(__file__))+"/pv/"+lang)
		for entry in results[lang]:
			if entry == "total":
				with open(os.path.dirname(os.path.abspath(__file__))+"/pv/"+lang+"_total.txt",'ab') as doc:
					doc.write(str(timegm(current.timetuple())) + "\t" + entry +"\t" + str(results[lang][entry]) + "\n")
			else:
				with open(os.path.dirname(os.path.abspath(__file__))+"/pv/"+lang+"/"+entry.replace('/','_').replace(':','_')+".txt",'ab') as doc:
					doc.write(str(timegm(current.timetuple())) + "\t" + entry +"\t" + str(results[lang][entry]) + "\n")