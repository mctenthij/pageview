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

	ynew = interp1d(range(len(ydata)),ydata)(xdata)
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
	for x in range(len(a)):
		if a[x] == 0:
			diff += b[x] ** 2
		else:
			diff += (log(a[x])-b[x]) ** 2

	return diff

def compare(original,estimate):
	"""Calculate normalized and total error for estimate and original"""
	perc_error = []
	abs_error = []
	for x in range(len(original)):
		abs_error.append(estimate[x] - original[x])
		try:
			perc_error.append(float(estimate[x] - original[x]) / original[x])
		except ZeroDivisionError:
			perc_error.append(float(estimate[x]))

	return perc_error, abs_error

def get_ylims(plotinfo):
	y_mins = []
	y_maxs = []
	for entry in plotinfo:
		y_mins.append(min(plotinfo[entry]["y"]))
		y_maxs.append(max(plotinfo[entry]["y"]))
	
	return {"start": floor(float(min(y_mins))/100)*100, "end": ceil(float(max(y_maxs))/100)*100}

def calc_average(totals,frequencies):
	result = []
	for x in range(len(totals)):
		if frequencies[x] == 0:
			result.append(0)
		else:
			result.append(totals[x]/frequencies[x])

	return result