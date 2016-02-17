# !/usr/bin/python
from math import log, exp

from scipy.optimize import fminbound
from numpy import zeros, polyfit

from util import rescale_time, rescale_to_normal, redistribute

class Redistributor:
	'''Redistributing time for analysis of page view data'''

	def __init__(self):
		self.c_opt = 0
		self.cycle = []
		self.views = []
		self.xtick = []
		self.xtick_back = []

	def run(self,views,cycle,pattern,c=None):
		self.pattern = pattern
		self.prom_length = len(pattern.relativeDays)
		self.set_views(views)
		self.set_cycle(cycle)
		if c == None:
			self.optimize_xtick() # calculate the optimal value of c to find the xticks for redistributed time.
		else:
			self.set_xtick(c)

	def set_cycle(self,cycle):
		self.cycle = cycle

	def set_views(self,views):
		self.views = views

	def set_xtick(self,c):
		adjusted_cycle = [self.cycle[x] - c*min(self.cycle) for x in range(len(self.cycle))]
		self.xtick = rescale_time(adjusted_cycle)
		self.xtick_back = rescale_to_normal(self.xtick)

	def optimize_xtick(self):
		self.find_opt_c()
		adjusted_cycle = [self.cycle[x] - self.c_opt*min(self.cycle) for x in range(len(self.cycle))]
		self.xtick = rescale_time(adjusted_cycle)
		self.xtick_back = rescale_to_normal(self.xtick)

	def find_opt_c(self):
		a = fminbound(self.opt_rescaling,0,1,full_output=True)
		self.c_opt = a[0]

	def get_estimate(self,c=None):
		if c == None:
			self.optimize_xtick()
			c = self.c_opt

		total_length = len(self.views)
		adjusted_cycle = [self.cycle[x] - c*min(self.cycle) for x in range(len(self.cycle))]
		xtick = rescale_time(adjusted_cycle);

		red_cycle = redistribute(xtick,self.views)
		estimate = zeros(total_length).tolist()
		
		if self.pattern.has_gamma:
			rang_p1 = range(self.pattern.start,24*self.pattern.length)
			p1 = polyfit(rang_p1,[log(red_cycle[x]) for x in rang_p1],1)
			rang_p2 = range(24*self.pattern.length,total_length)
			p2 = polyfit(rang_p2,[log(red_cycle[x]) for x in rang_p2],1)
			rang_p3 = range(24*self.pattern.length-1,24*self.pattern.length+1)
			p3 = polyfit(rang_p3,[log(red_cycle[x]) for x in rang_p3],1)

			for x in range(total_length):
				if x in rang_p1:
					estimate[x] = p1[1] + p1[0]*x
				if x in rang_p2:
					estimate[x] = p2[1] + p2[0]*x
		else:
			range_p1 = range(total_length)
			p1 = polyfit(range_p1,[log(red_cycle[x]) for x in range_p1],1)
			
			for x in range_p1:
				estimate[x] = p1[1] + p1[0]*x

		return [exp(x) for x in estimate]

	def opt_rescaling(self,c):
		total_length = len(self.views)
		adjusted_cycle = [self.cycle[x] - c*min(self.cycle) for x in range(len(self.cycle))]
		xtick = rescale_time(adjusted_cycle);

		red_cycle = redistribute(xtick,self.views)
		estimate = zeros(total_length).tolist()
		

		if self.pattern.has_gamma:
			rang_p1 = range(24*self.pattern.length)
			p1 = polyfit(rang_p1,[log(red_cycle[x]) for x in rang_p1],1)
			rang_p2 = range(24*self.pattern.length,total_length)
			p2 = polyfit(rang_p2,[log(red_cycle[x]) for x in rang_p2],1)
			rang_p3 = range(24*self.pattern.length-1,24*self.pattern.length+1)
			p3 = polyfit(rang_p3,[log(red_cycle[x]) for x in rang_p3],1)

			for x in range(total_length):
				if x in rang_p1:
					estimate[x] = p1[1] + p1[0]*x
				if x in rang_p2:
					estimate[x] = p2[1] + p2[0]*x
		else:
			range_p1 = range(total_length)
			p1 = polyfit(range_p1,[log(red_cycle[x]) for x in range_p1],1)
			
			for x in range_p1:
				estimate[x] = p1[1] + p1[0]*x

		error = sum([(red_cycle[x]-estimate[x]) ** 2 for x in range(24*self.prom_length-1)])
		return error