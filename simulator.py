#!/usr/bin/python
import os

from archive import Archive
from article import Article, Average, MainPage, TotalPage
from analyser import Analyser
from plotter import plot_cycles

class Simulator:
	'''Loading/extracting needed page-view data'''
	def __init__(self,start,end,pattern,overall,boolplot):
		self.pattern = pattern
		self.articles = []
		self.average = Average(self.pattern)
		self.mp = MainPage(pattern.lang,pattern.mp_title)
		self.tp = TotalPage(pattern.lang)
		self.pattern.getArchive(start,end)
		self.boolplot = boolplot
		self.overall = overall

	def load_data(self):
		self.mp.get_cycles()
		self.mp.get_yearly_cycles()
		self.mp.get_monthly_cycles()
		self.tp.get_cycles()
		self.tp.get_yearly_cycles()
		self.tp.get_monthly_cycles()

		for art in self.pattern.arch.articles:
			try:
				art = Article(art,self.pattern.arch.articleTitleToURL[art],self.pattern.arch.articles[art],self.pattern)
				try:
					art.get_views()
					if art.views != []:
						self.average.add_art(art)
						if not len(art.views) > 24*len(self.pattern.relativeDays)-1:
							self.articles.append(art)
						else:
							print "Look at page views for ", art.title 
				except IndexError:
					print art.link_title
			except KeyError:
				pass

		self.average.calc_av_views()
		print "Number of articles for "+self.pattern.title+": ", self.average.num_added

	def plot_data(self,yearly=False,monthly=False):
		plot_cycles(self.tp,"TP_"+self.pattern.lang+"_",yearly,monthly)
		plot_cycles(self.mp,"MP_"+self.pattern.lang+"_",yearly,monthly)

	def run(self,c_values=[],cycles=[]):
		if self.overall:
			extra = "_start_"+str(self.pattern.start)+"_overall"
		else:
			extra = "_start_"+str(self.pattern.start)+"_single"
		if c_values == [] and cycles == []:
			self.run_analysis(self.mp.hourly,"MP_"+self.pattern.lang+"_opt_c"+extra)
			self.run_analysis(self.tp.hourly,"TP_"+self.pattern.lang+"_opt_c"+extra)
		elif c_values == []:
			for cycle in cycles:
				if type(cycle) == int:
					self.run_analysis(self.mp.yearly_cycles[cycle]["hourly"],"MP_"+self.pattern.lang+"_"+str(cycle)+"_opt_c"+extra)
					self.run_analysis(self.tp.yearly_cycles[cycle]["hourly"],"TP_"+self.pattern.lang+"_"+str(cycle)+"_opt_c"+extra)
				elif type(cycle) == str:
					self.run_analysis(self.mp.monthly_cycles[cycle]["hourly"],"MP_"+self.pattern.lang+"_"+cycle+"_opt_c"+extra)
					self.run_analysis(self.tp.monthly_cycles[cycle]["hourly"],"TP_"+self.pattern.lang+"_"+cycle+"_opt_c"+extra)
		elif cycles == []:
			for cval in c_values:
				self.run_analysis(self.mp.hourly,"MP_"+self.pattern.lang+"_c_"+str(cval).replace(".","-")+extra,cval)
				self.run_analysis(self.tp.hourly,"TP_"+self.pattern.lang+"_c_"+str(cval).replace(".","-")+extra,cval)
		else:
			for cval in c_values:
				for cycle in cycles:
					if type(cycle) == int:
						self.run_analysis(self.mp.yearly_cycles[cycle]["hourly"],"MP_"+self.pattern.lang+"_"+str(cycle)+"_c_"+str(cval).replace(".","-")+extra,cval)
						self.run_analysis(self.tp.yearly_cycles[cycle]["hourly"],"TP_"+self.pattern.lang+"_"+str(cycle)+"_c_"+str(cval).replace(".","-")+extra,cval)
					elif type(cycle) == str:
						self.run_analysis(self.mp.monthly_cycles[cycle]["hourly"],"MP_"+self.pattern.lang+"_"+cycle+"_c_"+str(cval).replace(".","-")+extra,cval)
						self.run_analysis(self.tp.monthly_cycles[cycle]["hourly"],"TP_"+self.pattern.lang+"_"+cycle+"_c_"+str(cval).replace(".","-")+extra,cval)

	def run_analysis(self,cycle,plotdir,c=None):
		an = Analyser(self.articles,self.average,self.average.views,self.pattern,cycle,plotdir,c)
		if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/plots/"+plotdir):
			os.makedirs(os.path.dirname(os.path.abspath(__file__))+"/plots/"+plotdir)
		an.run(self.overall,self.boolplot)
		print "analysis performed:", plotdir