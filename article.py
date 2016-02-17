#!/usr/bin/python
from __future__ import division
from datetime import datetime
import calendar
import  os
from math import log, exp

import numpy as np
import scipy.optimize as opt

from util import redistribute, calc_difference, calc_average

class Article:
	'''Article with all required info'''

	def __init__(self,title,link,promo_date,promo_pattern):
		self.title = title
		self.link_title = link
		self.promo_date = datetime.strptime(promo_date,"%B %d, %Y")
		self.pattern = promo_pattern
		self.views = []
		self.red_views = []
		self.gamma = 0
		self.beta = 0
		self.est_params = []
		self.est_gamma_func = []
		self.max_length = 24*len(self.pattern.relativeDays)-1

	def get_views(self):
		if os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/pv/"+self.pattern.lang+"/"+self.link_title+".txt"):
			filename = "pv/"+self.pattern.lang+"/"+self.link_title+".txt"
			last_processed = calendar.timegm(self.promo_date.timetuple())
			with open(filename) as doc:
				for line in doc:
					cols = line.strip('\n').split("\t")
					timestamp = int(cols[0])
					hour_views = int(cols[2])

					if timestamp > last_processed:
						diff = timestamp-last_processed
						while diff > 3600:
							self.views.append(0)
							diff = diff - 3600
						self.views.append(hour_views)

					last_processed = timestamp

			while len(self.views) < self.max_length:
				self.views.append(0)

			self.norm_views = [self.views[x]/sum(self.views) for x in range(len(self.views))]

	def set_views(self,article_views):
		self.views = article_views

	def redistribute_views(self,ticks):
		self.red_views = redistribute(ticks,self.views)

	def get_estimate(self,ticks):
		max_length = len(self.views)
		log_estimate = np.zeros(max_length).tolist()
		
		if self.pattern.has_gamma:
			# log_estimate[:self.pattern.length*24] = [log(self.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
			log_estimate[self.pattern.start:self.pattern.length*24] = [log(self.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
			log_estimate[self.pattern.length*24:max_length] = [log(self.red_views[self.pattern.start])+log(self.gamma)+log(self.beta)*(x-1) for x in range(self.pattern.length*24,max_length)]
		else:
			log_estimate[self.pattern.start:self.pattern.start+self.pattern.length*24] = [log(self.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
		
		estimate = [exp(log_estimate[x]) for x in range(self.max_length)]	
		self.est_params = redistribute(ticks,estimate)

	def get_gamma_func_estimate(self,gamma_func,ticks):
		max_length = len(self.views)
		log_estimate = np.zeros(max_length).tolist()
		
		# log_estimate[:self.pattern.length*24] = [log(self.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
		log_estimate[self.pattern.start:self.pattern.length*24] = [log(self.red_views[self.pattern.start])+log(self.beta)*x for x in range(self.pattern.length*24)]
		log_estimate[self.pattern.length*24:self.max_length] = [log(self.red_views[self.pattern.start])+gamma_func[1]+log(self.red_views[self.pattern.start])*gamma_func[0]+log(self.beta)*(x-1) for x in range(self.pattern.length*24,self.max_length)]
		
		estimate = [exp(log_estimate[x]) for x in range(self.max_length)]
		self.est_gamma_func = redistribute(ticks,estimate)

	def get_param(self,num_vars=2,start=1):
		if num_vars == 2:
			params0 = [-.05,-1.5] # initial guess for the log of the parameters 
			output = opt.minimize(self.two_param_fit,params0)
			self.beta = exp(output.x[0])
			self.gamma = exp(output.x[1])
		elif num_vars == 1:
			param0 = -.05
			output = opt.minimize(self.one_param_fit,param0)
			self.beta = exp(output.x[0])

	def two_param_fit(self,params):
		log_estimate = np.zeros(len(self.views)).tolist()

		# log_estimate[:self.pattern.length*24] = [log(self.red_views[self.pattern.start])+params[0]*x for x in range(self.pattern.length*24)]
		log_estimate[self.pattern.start:self.pattern.length*24] = [log(self.red_views[self.pattern.start])+params[0]*x for x in range(self.pattern.length*24)]
		log_estimate[self.pattern.length*24:self.max_length] = [log(self.red_views[self.pattern.start])+params[1]+params[0]*(x-1) for x in range(self.pattern.length*24,self.max_length)]

		error = calc_difference(self.red_views,log_estimate)
		return error

	def one_param_fit(self,param):
		log_estimate = np.zeros(len(self.views)).tolist()
		
		log_estimate[self.pattern.start:self.pattern.start+self.pattern.length*24] = [log(self.red_views[self.pattern.start])+param*x for x in range(self.pattern.length*24)]

		error = calc_difference(self.red_views,log_estimate)
		return error

class Average(Article):
	'''Average article per promotion type (both total and normalized on max of article)'''

	def __init__(self,promo_pattern):
		Article.__init__(self,"Average article","av"+"_"+promo_pattern.title.replace(" ","_"),"January 1, 1999",promo_pattern)
		self.tot_views = np.zeros(self.max_length).tolist()
		self.tot_norm_views = np.zeros(self.max_length).tolist()
		self.num_added = 0

	def get_views(self):
		raise AttributeError("Average object has no attribute 'get_views', use calc_av_views instead after adding articles")
		
	def add_art(self,article):
		self.num_added += 1
		self.tot_views = [self.tot_views[x]+article.views[x] for x in range(len(article.views))]
		self.tot_norm_views = [self.tot_norm_views[x]+article.views[x]/sum(article.views) for x in range(len(article.views))]

	def calc_av_views(self):
		if self.num_added != 0:
			self.views = [self.tot_views[x]/self.num_added for x in range(len(self.tot_views))]
			self.norm_views = [self.tot_norm_views[x]/self.num_added for x in range(len(self.tot_views))]

class MainPage:
	'''Main page information, needed for analysis'''
	def __init__(self,lang,mp_title):
		self.hourly = []
		self.hourly_norm = []
		self.weekly = []
		self.weekly_norm = []
		self.yearly_cycles = {}
		self.monthly_cycles = {}
		self.lang = lang
		self.mp_title = mp_title

	def get_cycles(self):
		hourly_totals = np.zeros(24).tolist()
		hourly_norm_totals = np.zeros(24).tolist()
		hourly_num = np.zeros(24).tolist()
		weekly_totals = np.zeros(7*24).tolist()
		weekly_norm_totals = np.zeros(7*24).tolist()
		weekly_num = np.zeros(7*24).tolist()

		hour_norm = np.zeros(24).tolist()
		week_norm = np.zeros(7*24).tolist()

		if os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/pv/"+self.lang+"/"+self.mp_title+".txt"):
			filename = "pv/"+self.lang+"/"+self.mp_title+".txt"
			with open(filename) as doc:
				for line in doc:
					cols = line.strip('\n').split("\t")
					timestamp = int(cols[0])
					hour_views = int(cols[2])

					dt = datetime.utcfromtimestamp(timestamp)
					if dt.hour == 0 and sum(hour_norm) > 0:
						temp = [x/sum(hour_norm) for x in hour_norm]
						hour_norm = np.zeros(24).tolist()
						for x in range(len(temp)):
							hourly_norm_totals[x] += temp[x]

						if dt.weekday() == 0:
							temp_week = [x/sum(week_norm) for x in week_norm]
							week_norm = np.zeros(7*24).tolist()
							for x in range(len(temp_week)):
								weekly_norm_totals[x] += temp_week[x]

					hourly_totals[dt.hour] += hour_views
					hour_norm[dt.hour] = hour_views
					hourly_num[dt.hour] += 1
					
					weekly_totals[24*dt.weekday()+dt.hour] += hour_views
					week_norm[24*dt.weekday()+dt.hour] += hour_views
					weekly_num[24*dt.weekday()+dt.hour] += 1
		
		self.hourly = calc_average(hourly_totals,hourly_num)
		self.hourly_norm = calc_average(hourly_norm_totals,hourly_num)
		self.weekly = calc_average(weekly_totals,weekly_num)
		self.weekly_norm = calc_average(weekly_norm_totals,weekly_num)

	def get_yearly_cycles(self):
		temp = {}
		if os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/pv/"+self.lang+"/"+self.mp_title+".txt"):
			filename = "pv/"+self.lang+"/"+self.mp_title+".txt"
			with open(filename) as doc:
				for line in doc:
					cols = line.strip('\n').split("\t")
					timestamp = int(cols[0])
					hour_views = int(cols[2])

					dt = datetime.utcfromtimestamp(timestamp)

					if dt.year not in temp:
						temp[dt.year] = {}
						temp[dt.year]["hourly_totals"] = np.zeros(24).tolist()
						temp[dt.year]["hourly_num"] = np.zeros(24).tolist()
						temp[dt.year]["weekly_totals"] = np.zeros(7*24).tolist()
						temp[dt.year]["weekly_num"] = np.zeros(7*24).tolist()
					temp[dt.year]["hourly_totals"][dt.hour] += hour_views
					temp[dt.year]["hourly_num"][dt.hour] += 1
					
					temp[dt.year]["weekly_totals"][24*dt.weekday()+dt.hour] += hour_views
					temp[dt.year]["weekly_num"][24*dt.weekday()+dt.hour] += 1
					
		for year in temp:
			self.yearly_cycles[year] = {}		
			self.yearly_cycles[year]["hourly"] = calc_average(temp[year]["hourly_totals"],temp[year]["hourly_num"])
			self.yearly_cycles[year]["weekly"] = calc_average(temp[year]["weekly_totals"],temp[year]["weekly_num"])

	def get_monthly_cycles(self):
		temp = {}
		if os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/pv/"+self.lang+"/"+self.mp_title+".txt"):
			filename = "pv/"+self.lang+"/"+self.mp_title+".txt"
			with open(filename) as doc:
				for line in doc:
					cols = line.strip('\n').split("\t")
					timestamp = int(cols[0])
					hour_views = int(cols[2])

					dt = datetime.utcfromtimestamp(timestamp)

					if dt.strftime("%B_%Y") not in temp:
						temp[dt.strftime("%B_%Y")] = {}
						temp[dt.strftime("%B_%Y")]["hourly_totals"] = np.zeros(24).tolist()
						temp[dt.strftime("%B_%Y")]["hourly_num"] = np.zeros(24).tolist()
						temp[dt.strftime("%B_%Y")]["weekly_totals"] = np.zeros(7*24).tolist()
						temp[dt.strftime("%B_%Y")]["weekly_num"] = np.zeros(7*24).tolist()
					temp[dt.strftime("%B_%Y")]["hourly_totals"][dt.hour] += hour_views
					temp[dt.strftime("%B_%Y")]["hourly_num"][dt.hour] += 1
					
					temp[dt.strftime("%B_%Y")]["weekly_totals"][24*dt.weekday()+dt.hour] += hour_views
					temp[dt.strftime("%B_%Y")]["weekly_num"][24*dt.weekday()+dt.hour] += 1
					
		for month in temp:
			self.monthly_cycles[month] = {}		
			self.monthly_cycles[month]["hourly"] = calc_average(temp[month]["hourly_totals"],temp[month]["hourly_num"])
			self.monthly_cycles[month]["weekly"] = calc_average(temp[month]["weekly_totals"],temp[month]["weekly_num"])

	def set_hourly(self,page_view_cycle):
		self.hourly = page_view_cycle

	def set_weekly(self,weekly_page_view_cycle):
		self.weekly = weekly_page_view_cycle

class TotalPage:
	'''Total page views, needed for analysis'''
	def __init__(self,lang):
		self.hourly = []
		self.hourly_norm = []
		self.weekly = []
		self.weekly_norm = []
		self.yearly_cycles = {}
		self.monthly_cycles = {}
		self.lang = lang

	def get_cycles(self):
		hourly_totals = np.zeros(24).tolist()
		hourly_norm_totals = np.zeros(24).tolist()
		hourly_num = np.zeros(24).tolist()
		weekly_totals = np.zeros(7*24).tolist()
		weekly_norm_totals = np.zeros(7*24).tolist()
		weekly_num = np.zeros(7*24).tolist()

		hour_norm = np.zeros(24).tolist()
		week_norm = np.zeros(7*24).tolist()

		if os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/pv/"+self.lang+"_total.txt"):
			filename = "pv/"+self.lang+"_total.txt"
			with open(filename) as doc:
				for line in doc:
					cols = line.strip('\n').split("\t")
					timestamp = int(cols[0])
					hour_views = int(cols[2])

					dt = datetime.utcfromtimestamp(timestamp)
					if dt.hour == 0 and sum(hour_norm) > 0:
						temp = [x/sum(hour_norm) for x in hour_norm]
						hour_norm = np.zeros(24).tolist()
						for x in range(len(temp)):
							hourly_norm_totals[x] += temp[x]

						if dt.weekday() == 0:
							temp_week = [x/sum(week_norm) for x in week_norm]
							week_norm = np.zeros(7*24).tolist()
							for x in range(len(temp_week)):
								weekly_norm_totals[x] += temp_week[x]

					hourly_totals[dt.hour] += hour_views
					hour_norm[dt.hour] = hour_views
					hourly_num[dt.hour] += 1
					
					weekly_totals[24*dt.weekday()+dt.hour] += hour_views
					week_norm[24*dt.weekday()+dt.hour] += hour_views
					weekly_num[24*dt.weekday()+dt.hour] += 1
		
		self.hourly = calc_average(hourly_totals,hourly_num)
		self.hourly_norm = calc_average(hourly_norm_totals,hourly_num)
		self.weekly = calc_average(weekly_totals,weekly_num)
		self.weekly_norm = calc_average(weekly_norm_totals,weekly_num)

	def get_yearly_cycles(self):
		temp = {}
		if os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/pv/"+self.lang+"_total.txt"):
			filename = "pv/"+self.lang+"_total.txt"
			with open(filename) as doc:
				for line in doc:
					cols = line.strip('\n').split("\t")
					timestamp = int(cols[0])
					hour_views = int(cols[2])

					dt = datetime.utcfromtimestamp(timestamp)

					if dt.year not in temp:
						temp[dt.year] = {}
						temp[dt.year]["hourly_totals"] = np.zeros(24).tolist()
						temp[dt.year]["hourly_num"] = np.zeros(24).tolist()
						temp[dt.year]["weekly_totals"] = np.zeros(7*24).tolist()
						temp[dt.year]["weekly_num"] = np.zeros(7*24).tolist()
					temp[dt.year]["hourly_totals"][dt.hour] += hour_views
					temp[dt.year]["hourly_num"][dt.hour] += 1
					
					temp[dt.year]["weekly_totals"][24*dt.weekday()+dt.hour] += hour_views
					temp[dt.year]["weekly_num"][24*dt.weekday()+dt.hour] += 1
					
		for year in temp:
			self.yearly_cycles[year] = {}		
			self.yearly_cycles[year]["hourly"] = [temp[year]["hourly_totals"][x]/temp[year]["hourly_num"][x] for x in range(len(temp[year]["hourly_totals"]))]
			self.yearly_cycles[year]["weekly"] = [temp[year]["weekly_totals"][x]/temp[year]["weekly_num"][x] for x in range(len(temp[year]["weekly_totals"]))]

	def get_monthly_cycles(self):
		temp = {}
		if os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/pv/"+self.lang+"_total.txt"):
			filename = "pv/"+self.lang+"_total.txt"
			with open(filename) as doc:
				for line in doc:
					cols = line.strip('\n').split("\t")
					timestamp = int(cols[0])
					hour_views = int(cols[2])

					dt = datetime.utcfromtimestamp(timestamp)

					if dt.strftime("%B_%Y") not in temp:
						temp[dt.strftime("%B_%Y")] = {}
						temp[dt.strftime("%B_%Y")]["hourly_totals"] = np.zeros(24).tolist()
						temp[dt.strftime("%B_%Y")]["hourly_num"] = np.zeros(24).tolist()
						temp[dt.strftime("%B_%Y")]["weekly_totals"] = np.zeros(7*24).tolist()
						temp[dt.strftime("%B_%Y")]["weekly_num"] = np.zeros(7*24).tolist()
					temp[dt.strftime("%B_%Y")]["hourly_totals"][dt.hour] += hour_views
					temp[dt.strftime("%B_%Y")]["hourly_num"][dt.hour] += 1
					
					temp[dt.strftime("%B_%Y")]["weekly_totals"][24*dt.weekday()+dt.hour] += hour_views
					temp[dt.strftime("%B_%Y")]["weekly_num"][24*dt.weekday()+dt.hour] += 1
					
		for month in temp:
			self.monthly_cycles[month] = {}		
			self.monthly_cycles[month]["hourly"] = [temp[month]["hourly_totals"][x]/temp[month]["hourly_num"][x] for x in range(len(temp[month]["hourly_totals"]))]
			self.monthly_cycles[month]["weekly"] = [temp[month]["weekly_totals"][x]/temp[month]["weekly_num"][x] for x in range(len(temp[month]["weekly_totals"]))]

	def set_hourly(self,page_view_cycle):
		self.hourly = page_view_cycle

	def set_weekly(self,weekly_page_view_cycle):
		self.weekly = weekly_page_view_cycle