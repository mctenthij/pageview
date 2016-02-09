#!/usr/bin/python
import os
from math import log, exp, ceil, floor

from scipy.optimize import minimize
from numpy import zeros, polyfit

from article import Article, Average, MainPage
import plotter as plt
from util import calc_difference, redistribute, compare
from redistributor import Redistributor

class Analyser:
	'''Analysing the page view data'''

	def __init__(self,articles,average,views,pattern,cycle,plotdir,c=None):
		self.plotfolder = plotdir + "/"
		self.articles = articles
		self.average = average
		self.errors = {}
		self.pattern = pattern
		self.red = Redistributor()
		self.red.run(views,cycle,pattern,c)
		self.beta = 0
		self.gamma = 0
		self.gamma_func = [0,0]
		self.logdict = {}

	def run(self,overall=True,plot=False):
		'''
		feat: True if featured articles have to be considered
		hist: True if on this day articles have to be considered
		overall: True if all articles have to be estimated using the same overall parameter values
		plot: True if all articles have to be plotted
		'''
		self.calc_red()
		self.calc_params()
		self.calc_estimates(overall)
		self.calc_plot_error()

		if self.pattern.has_gamma:
			plt.plot_gamma_corr(self.articles,self.gamma_func,self.plotfolder)

		plt.plot_articles(self.average,self.articles,self.pattern,self.plotfolder,plot)

		self.make_output(overall)

	def make_output(self,overall):
		with open("plots/"+self.plotfolder+"results.txt","wb") as result:
			if overall:
				result.write("optimal c:\t{0:.4f}\n".format(self.red.c_opt)) 
				result.write("Number of articles for {1}:\t{0}\n".format(len(self.articles),self.pattern.title))
				result.write("Parameter values for articles:\n")
				result.write("Beta:\t{0:.4f}\n".format(self.beta))
				if self.pattern.has_gamma:
					result.write("Gamma:\t{0:.4f}\n".format(self.gamma))
					result.write("Gamma func:\t[{0:.4f},{1:.4f}]\n".format(self.gamma_func[0],self.gamma_func[1]))
			else:
				result.write("optimal c:\t{0:.4f}\n".format(self.red.c_opt)) 
				result.write("Number of articles for {1}:\t{0}\n".format(len(self.articles),self.pattern.title))
				result.write("Parameter values for average article:\n")
				result.write("Beta:\t{0:.4f}\n".format(self.average.beta))
				if self.pattern.has_gamma:
					result.write("Gamma:\t{0:.4f}\n".format(self.average.gamma))
					result.write("Gamma func:\t[{0:.4f},{1:.4f}]\n".format(self.average.est_gamma_func[0],self.average.est_gamma_func[1]))

			result.write("\n\n")
			for title in self.logdict:
				for err in self.logdict[title]:
					result.write("{0} {1}\n".format(title,err))
					
	def calc_red(self):
		self.average.redistribute_views(self.red.xtick)
		for art in self.articles:
			art.redistribute_views(self.red.xtick)

			### MAKING SURE THAT ARTICLES WITH red_views[self.pattern.start] = 0.0 are deleted.
			try:
				log(art.red_views[self.pattern.start])
			except ValueError as e:
				if str(e) == "math domain error":
					self.catch_error(art,"calc_redistribution")
				else:
					print str(e)

		
	def calc_params(self):
		if self.pattern.has_gamma:
			num_vars = 2
		else:
			num_vars = 1
		
		self.average.get_param(num_vars)
		for art in self.articles:
			try:
				art.get_param(num_vars)
			except ValueError as e:
				if str(e) == "math domain error":
					self.catch_error(art,"calc_params")
				else:
					raise e
			except IndexError:
				art.redistribute_views(self.red.xtick)
				try:
					art.get_param(num_vars)
				except ValueError as e:
					if str(e) == "math domain error":
						self.catch_error(art,"calc_params")
					else:
						raise e

		self.get_param()
		if self.pattern.has_gamma:
			self.get_gamma_func()

	def calc_estimates(self,overall):
		if overall:
			self.get_estimate(self.average,self.red.xtick_back)
			if self.pattern.has_gamma:
				self.get_gamma_func_estimate(self.average,self.gamma_func,self.red.xtick_back)
			for art in self.articles:
				self.get_estimate(art,self.red.xtick_back)
				if self.pattern.has_gamma:
					self.get_gamma_func_estimate(art,self.gamma_func,self.red.xtick_back)

		else:
			self.average.get_estimate(self.red.xtick_back)
			if self.pattern.has_gamma:
				self.average.get_gamma_func_estimate(self.gamma_func,self.red.xtick_back)
			for art in self.articles:
				try:
					art.get_estimate(self.red.xtick_back)
					if self.pattern.has_gamma:
						art.get_gamma_func_estimate(self.gamma_func,self.red.xtick_back)
				except ValueError as e:
					if str(e) == "math domain error":
						self.catch_error(art,"calc_estimates")

	def calc_plot_error(self):
		perc_errors = {"gamma_func": [], "params": []}
		abs_errors = {"gamma_func": [], "params": []}
		for art in self.articles:
			try:
				perc_error,abs_error = compare(art.views,art.est_params)
				perc_errors["params"].append(perc_error)
				abs_errors["params"].append(abs_error)
				if self.pattern.has_gamma:
					perc_error,abs_error = compare(art.views,art.est_gamma_func)
					perc_errors["gamma_func"].append(perc_error)
					abs_errors["gamma_func"].append(abs_error)
			except IndexError:
				self.catch_error(art,"calc_error")

		plt.plot_errors(perc_errors,abs_errors,self.plotfolder,self.pattern)
		self.errors = {"normalized": perc_errors, "absolute": abs_errors}
		
	def get_gamma_func(self):
		gamma_list = []
		v1_list = []
		for art in self.articles:
			reason = ""
			try:
				log(art.gamma)
			except ValueError as e:
				if str(e) == "math domain error":
					reason = r"$\gamma$ equals 0"
			
			try:
				log(art.views[0])
			except ValueError as e:
				if str(e) == "math domain error":
					if art.views[0] == 0 and reason == "":
						reason = r"$v_1$ equals 0"
					else:
						reason = r"$\gamma$ and $v_1$ equal 0"

			if reason != "":
				if art.link_title in self.logdict:
					self.logdict[art.link_title].append("was not included in gamma function calculation ({}).".format(reason))
				else:
					self.logdict[art.link_title] = ["was not included in gamma function calculation ({}).".format(reason)]
			else:
				# if -4 < log(art.gamma) < 0.3:
				# 	if 5 < log(art.views[0]) < 10:
				gamma_list.append(log(art.gamma))
				v1_list.append(log(art.views[0]))

		if gamma_list:
				self.gamma_func = polyfit(v1_list,gamma_list,1).tolist();

	def get_param(self):
		'''Calculate parameters:
		'''
		if self.pattern.has_gamma:
			params0 = [-.05,-1.5] # initial guess for the log of the parameters 
			output = minimize(self.beta_gamma_fit,params0)
			self.beta = exp(output.x[0])
			self.gamma = exp(output.x[1])
		else:
			param0 = -.05
			output = minimize(self.beta_fit,param0)
			self.beta = exp(output.x[0])

	def beta_gamma_fit(self,params):
		error = 0
		for art in self.articles:
			max_length = len(art.views)
			log_estimate = zeros(max_length).tolist()
			# log_estimate[:self.pattern.length*24] = [log(art.red_views[self.pattern.start])+params[0]*x for x in range(self.pattern.length*24)]
			log_estimate[self.pattern.start:self.pattern.length*24] = [log(art.red_views[self.pattern.start])+params[0]*x for x in range(self.pattern.length*24)]
			log_estimate[self.pattern.length*24:max_length] = [log(art.red_views[self.pattern.start])+params[1]+params[0]*(x-1) for x in range(self.pattern.length*24,max_length)]

			error += calc_difference(art.red_views,log_estimate)

		return error

	def beta_fit(self,param):
		error = 0
		for art in self.articles:
			max_length = len(art.views)
			log_estimate = zeros(max_length).tolist()
			log_estimate[self.pattern.start:self.pattern.start+self.pattern.length*24] = [log(art.red_views[self.pattern.start])+param*x for x in range(self.pattern.length*24)]

			error += calc_difference(art.red_views,log_estimate)

		return error

	def get_estimate(self,art,ticks):
		max_length = len(art.views)
		log_estimate = zeros(max_length).tolist()

		if self.pattern.has_gamma:
			# log_estimate[:self.pattern.length*24] = [log(art.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
			log_estimate[self.pattern.start:self.pattern.length*24] = [log(art.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
			log_estimate[self.pattern.length*24:max_length] = [log(art.red_views[self.pattern.start])+log(self.gamma)+log(self.beta)*(x-1) for x in range(self.pattern.length*24,max_length)]
		else:
			log_estimate[self.pattern.start:self.pattern.start+self.pattern.length*24] = [log(art.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
		
		estimate = [exp(log_estimate[x]) for x in range(max_length)]	
		art.est_params = redistribute(ticks,estimate)

	def get_gamma_func_estimate(self,art,gamma_func,ticks):
		max_length = len(art.views)
		log_estimate = zeros(max_length).tolist()
		
		if self.pattern.has_gamma:
			# log_estimate[:self.pattern.length*24] = [log(art.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
			log_estimate[self.pattern.start:self.pattern.length*24] = [log(art.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
			log_estimate[self.pattern.length*24:max_length] = [log(art.red_views[self.pattern.start])+gamma_func[1]+log(art.red_views[self.pattern.start])*gamma_func[0]+log(self.beta)*(x-1) for x in range(self.pattern.length*24,max_length)]
		else:
			log_estimate = zeros(max_length).tolist()
			log_estimate[self.pattern.start:self.pattern.start+self.pattern.length*24] = [log(art.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
		
		estimate = [exp(log_estimate[x]) for x in range(max_length)]
		art.est_gamma_func = redistribute(ticks,estimate)

	def catch_error(self,art,location):
		if "plot" in location:
			if art.link_title in self.logdict:
				self.logdict[art.link_title].append("is not included plots.")
			else:
				self.logdict[art.link_title] = ["is not included plots."]
		else: 
			idx = self.articles.index(art)
			del self.articles[idx]
			if art.link_title in self.logdict:
				self.logdict[art.link_title].append("is deleted due to an error in function {}.".format(location))
			else:
				self.logdict[art.link_title] = ["is deleted due to an error in function {}.".format(location)]