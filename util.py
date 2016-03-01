#!/usr/bin/python
from __future__ import division
from math import log, floor, ceil
from urllib2 import Request, urlopen

import numpy as np
from scipy.interpolate import interp1d

def loadUrl(adress):
	user_agent = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.63 Safari/534.3'
	headers = { 'User-Agent' : user_agent }
	req = Request(adress, None, headers)
	return urlopen(req)

def rescale_time(values):
	# equivalent to rescaleAK.m
	# switch from t to t*
	x = range(25)
	y = [0]+[i/sum(values)*24 for i in cumsum(values)]
	
	xtick = interp1d(y,x)(range(25))
	return xtick.tolist()

def rescale_to_normal(xtick):
	# from t* back to t
	xtick_back = rescale_time(np.diff(xtick))
	return xtick_back

def redistribute(xtick,views):
	xtick_long = make_long_xtick(xtick,views)

	xdata = xtick_long+[len(views)]
	ydata = [0]+cumsum(views)

	ynew = interp1d(xrange(len(ydata)),ydata)(xdata)
	red_data = np.diff(ynew)

	return red_data

def make_long_xtick(xtick,values):
	xtick_long = []
	while len(xtick_long) != len(values):
		idx = len(xtick_long)
		xtick_long.append(xtick[idx%24]+24*int(idx/24))
	return xtick_long

def cumsum(values):
	return list(cums(values))

def cums(values):
	total = 0;
	for x in values:
		total += x
		yield total

def calc_difference(a,b):
	diff = 0
	for idx,value in enumerate(a):
		if value == 0:
			diff += b[idx] ** 2
		else:
			diff += (log(value)-b[idx]) ** 2

	return diff

def compare(original,estimate):
	"""Calculate normalized and total error for estimate and original"""
	perc_error = []
	abs_error = []
	for idx,value in enumerate(original):
		abs_error.append(estimate[idx] - value)
		try:
			perc_error.append((estimate[idx] - value) / value)
		except ZeroDivisionError:
			perc_error.append((estimate[idx]))

	return perc_error, abs_error

def get_ylims(plotinfo):
	y_mins = []
	y_maxs = []
	for entry in plotinfo:
		y_mins.append(min(plotinfo[entry]["y"]))
		y_maxs.append(max(plotinfo[entry]["y"]))
	
	return {"start": floor((min(y_mins))/100)*100, "end": ceil((max(y_maxs))/100)*100}

def calc_average(totals,frequencies):
	result = []
	for idx,value in enumerate(totals):
		if frequencies[idx] == 0:
			result.append(0)
		else:
			result.append(value/frequencies[idx])

	return result