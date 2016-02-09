#!/usr/bin/python
import re
from datetime import datetime
import locale

from pycountry import languages

from archive import Archive

class PromotionPattern:
	def __init__(self,title,length,relativeDays,lang,mp,pattern,has_gamma=True,start=0,archLink=None,archLink_fmt=None,archTime_fmt=None):
		""" Promotion pattern in a given Wiki

		title: Name of the Promotion pattern (type: str)
		length: Length of display during promotion (type: int)
		relativeDays:
		lang:
		mp: Name of language main page in pv database (e.g. Main_Page for en)
		pattern: Regular expression for promotion pattern (type: regex)
		has_gamma: True is there is a sharp decay in page view pattern (e.g. by Today's Featured article)
		start: The start time of the promotion pattern (e.g. 25 for On this Day)
		archive: Link to site with archive of promotion pattern (type: string)
		arch_fmt: strftime format of specified time in link to archive of promotion pattern
		"""
		self.title = title
		self.relativeDays = relativeDays
		self.length = length
		self.mp_title = mp
		self.has_gamma = has_gamma
		self.start = start
		try:
			languages.get(iso639_1_code=lang)
			self.lang = lang
		except KeyError:
			raise KeyError('Language "'+lang+'" does not exist')

		if archLink:
			self.scrapePattern = ScrapePattern(lang,pattern,archLink,archLink_fmt,archTime_fmt)

	def getArchive(self,start,end):
		self.arch = Archive(start,end,self.scrapePattern,self.title)
		self.arch.getArticles()

class ScrapePattern:
	def __init__(self,lang,pattern,archLink=None,archLink_fmt=None,archTime_fmt=None):
		try:
			re.compile(pattern)
			self.pattern = pattern
		except re.error:
			raise re.error
		self.lang = lang
		self.archLink = archLink
		self.archLink_fmt = archLink_fmt
		self.archTime_fmt = archTime_fmt

	def getArchiveLink(self,dt_obj):
		locale.setlocale(locale.LC_TIME,(self.lang,"UTF-8"))
		date_str = dt_obj.strftime(self.archLink_fmt)
		locale.resetlocale(locale.LC_TIME)
		return self.archLink.format(date_str)