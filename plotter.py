#!/usr/bin/python
from math import ceil,floor, exp, log

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as mplcm
import matplotlib.colors as colors
from numpy import median, percentile, zeros
from scipy.stats import pearsonr

from util import cumsum, get_ylims

def plot_day(plotinfo,axisinfo,fileformat="pdf",ylims=(None,None)):
	if ylims[0]:
		axisinfo["ylim"]["start"] = ylims[0]
	if ylims[1]:
		axisinfo["ylim"]["end"] = ylims[1]

	cm = plt.get_cmap('jet')
	cNorm  = colors.Normalize(vmin=0, vmax=len(plotinfo)-1)
	scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
	xticks = ["" for i in range(24)]
	for i in range(8):
		xticks[3*i] = str(3*i)+"h"

	fig = plt.figure(figsize=(11.7, 8.3))
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
	ax = fig.add_subplot(111)
	ax.set_color_cycle([scalarMap.to_rgba(i) for i,entry in enumerate(plotinfo)])
	# ax.set_xlabel(r'',size=28)
	ax.set_ylabel(axisinfo["ylabel"],size=28)

	for entry in sorted(plotinfo):
		plt.plot(plotinfo[entry]["x"], plotinfo[entry]["y"], plotinfo[entry]["line_style"], label=plotinfo[entry]["label"], lw = 2)

	ax.set_xlim(0,23)
	ax.set_ylim(axisinfo["ylim"]["start"],axisinfo["ylim"]["end"])
	plt.xticks(range(24), xticks, rotation=0, size=22)
	plt.yticks(size=22)

	ax.legend(loc=0, ncol=1)
	plt.savefig("plots/"+axisinfo["filename"]+"."+fileformat, dpi=600, facecolor='w', edgecolor='w',orientation='landscape', papertype='A4')
	# plt.draw()
	# plt.show()
	plt.close(fig)

def plot_week(plotinfo,axisinfo,fileformat="pdf",ylims=(None,None)):
	if ylims[0]:
		axisinfo["ylim"]["start"] = ylims[0]
	if ylims[1]:
		axisinfo["ylim"]["end"] = ylims[1]

	cm = plt.get_cmap('jet')
	cNorm  = colors.Normalize(vmin=0, vmax=len(plotinfo)-1)
	scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
	xticks = ["" for i in range(7*24)]
	xticks[0] = "Mon"
	xticks[24] = "Tue"
	xticks[48] = "Wed"
	xticks[72] = "Thu"
	xticks[96] = "Fri"
	xticks[120] = "Sat"
	xticks[144] = "Sun"
	for i in range(7):
		xticks[i*24+12] = "12h"

	fig = plt.figure(figsize=(11.7, 8.3))
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
	ax = fig.add_subplot(111)
	ax.set_color_cycle([scalarMap.to_rgba(i) for i,entry in enumerate(plotinfo)])
	# ax.set_xlabel(r'',size=28)
	ax.set_ylabel(axisinfo["ylabel"],size=28)
	ax.fill_between(range(24), 0, axisinfo["ylim"]["end"], color='0.75')
	ax.fill_between(range(48,72), 0, axisinfo["ylim"]["end"], color='0.75')
	ax.fill_between(range(96,120), 0, axisinfo["ylim"]["end"], color='0.75')
	ax.fill_between(range(144,168), 0, axisinfo["ylim"]["end"], color='0.75')

	for entry in sorted(plotinfo):
		plt.plot(plotinfo[entry]["x"], plotinfo[entry]["y"], plotinfo[entry]["line_style"], label=plotinfo[entry]["label"], lw = 2)
	
	ax.set_xlim(0,167)
	ax.set_ylim(axisinfo["ylim"]["start"],axisinfo["ylim"]["end"])
	plt.xticks(range(7*24), xticks, rotation="horizontal", size=22)
	plt.yticks(size=22)
	
	ax.legend(loc=0, ncol=1)
	plt.savefig("plots/"+axisinfo["filename"]+"."+fileformat, dpi=600, facecolor='w', edgecolor='w',orientation='landscape', papertype='A4')
	# plt.draw()
	# plt.show()
	plt.close(fig)

def plot_pattern(plotinfo,axisinfo):
	fig = plt.figure(figsize=(11.7, 8.3))
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
	ax = fig.add_subplot(111)
	ax.set_title(axisinfo['title'],size=28)
	# ax.set_xlabel(axisinfo["xlabel"],size=28)
	ax.set_ylabel(axisinfo["ylabel"],size=28)
	i=0
	while i < len(axisinfo["xticks"]):
		if axisinfo["ylim"]["start"] < 0:
			ax.fill_between(range(24+48*i,48*(i+1)), axisinfo["ylim"]["start"], axisinfo["ylim"]["end"], color='0.75')
		else:
			ax.fill_between(range(24+48*i,48*(i+1)), 0, axisinfo["ylim"]["end"], color='0.75')
		i+=1

	for entry in sorted(plotinfo):
		plt.plot(plotinfo[entry]["x"], plotinfo[entry]["y"], plotinfo[entry]["line_style"], color=plotinfo[entry]["line_color"], label=plotinfo[entry]["label"], lw = 2)
	
	if axisinfo["xlim"]["start"] < 0:
		ax.set_xlim(axisinfo["xlim"]["start"],axisinfo["xlim"]["end"])
	else:
		ax.set_xlim(0,axisinfo["xlim"]["end"])
	
	ax.set_ylim(axisinfo["ylim"]["start"],axisinfo["ylim"]["end"])
	# if axisinfo["ylim"]["start"] < 0:
	# 	ax.set_ylim(axisinfo["ylim"]["start"],axisinfo["ylim"]["end"])
	# else:
	# 	ax.set_ylim(0,axisinfo["ylim"]["end"])
	
	plt.xticks(xrange(len(axisinfo["xticks"])), axisinfo["xticks"], rotation="horizontal", size=22)
	plt.yticks(size=22)
	ax.legend(loc=0, ncol=1)
	plt.savefig("plots/"+axisinfo["filename"]+".pdf", dpi=600, facecolor='w', edgecolor='w',orientation='landscape', papertype='A4')
	# plt.draw()
	# plt.show()
	plt.close(fig)

def plot_articles(average,articles,pattern,plotfolder,plot_all):
	plot_art(average,pattern,plotfolder)

	if plot_all:
		for art in articles:
			try:
				plot_art(art,pattern,plotfolder)
			except UnicodeDecodeError:
				print art.title
		
def plot_art(art,pattern,plotfolder):
	xticks = ["" for _ in art.views]
	i = 0
	while i < len(art.views):
		xticks[i] = str(i%24)+"h"
		i+=6

	max_length = len(art.views)
	log_estimate = zeros(max_length).tolist()
	
	if art.pattern.has_gamma:
		log_estimate[art.pattern.start:art.pattern.length*24] = [log(art.red_views[art.pattern.start])+log(art.beta)*x for x in range(art.pattern.length*24)]
		log_estimate[art.pattern.length*24:max_length] = [log(art.red_views[art.pattern.start])+log(art.gamma)+log(art.beta)*(x-1) for x in range(art.pattern.length*24,max_length)]
	else:
		log_estimate[art.pattern.start:art.pattern.start+art.pattern.length*24] = [log(art.red_views[art.pattern.start])+log(art.beta)*x for x in range(art.pattern.length*24)]
	
	estimate = [exp(log_estimate[x]) for x in range(max_length)]

	plotinfo = {"normal": {}, "estimate": {}, "model": {}}
	plotinfo["normal"]["x"] = xrange(len(art.views))
	plotinfo["normal"]["y"] = art.views
	plotinfo["normal"]["line_style"] = '-'
	plotinfo["normal"]["line_color"] = 'blue'
	plotinfo["normal"]["label"] = "Page-views"
	plotinfo["model"]["x"] = xrange(len(art.views))
	plotinfo["model"]["y"] = estimate
	plotinfo["model"]["line_style"] = '--'
	plotinfo["model"]["line_color"] = 'green'
	plotinfo["model"]["label"] = "Model"
	plotinfo["estimate"]["x"] = xrange(len(art.views))
	plotinfo["estimate"]["y"] = art.est_params
	plotinfo["estimate"]["line_style"] = '--'
	plotinfo["estimate"]["line_color"] = 'red'
	if pattern.has_gamma:
		plotinfo["estimate"]["label"] = r"Estimated views ($\beta,\gamma$)"
		plotinfo["gamma"] = {}
		plotinfo["gamma"]["x"] = xrange(len(art.views))
		plotinfo["gamma"]["y"] = art.est_gamma_func
		plotinfo["gamma"]["line_style"] = '--'
		plotinfo["gamma"]["line_color"] = 'black'
		plotinfo["gamma"]["label"] = r"Estimated views ($\beta,\gamma(v_1)$)"
	else:
		plotinfo["estimate"]["label"] = r"Estimated views ($\beta$)"

	axisinfo = {"filename": plotfolder+art.link_title, "ylabel": r'Number of page-views', "xticks": xticks, "title": "Hourly progression of "+art.title, "xlim": {"start": 0, "end": len(xticks)}, "ylim": get_ylims(plotinfo)}
	plot_pattern(plotinfo,axisinfo)

	plotinfo = {"cumsum": {}}
	plotinfo["cumsum"]
	plotinfo["cumsum"]["x"] = xrange(len(art.views))
	plotinfo["cumsum"]["y"] = cumsum(art.views)
	plotinfo["cumsum"]["line_style"] = '-'
	plotinfo["cumsum"]["line_color"] = 'blue'
	plotinfo["cumsum"]["label"] = "Cumulative views"		

	axisinfo = {"filename": plotfolder+"cum_"+art.link_title, "ylabel": r'Cumulative number of page-views', "xticks": xticks, "title": "Cumulative progression of "+art.title, "xlim": {"start": 0, "end": len(xticks)}, "ylim": get_ylims(plotinfo)}
	plot_pattern(plotinfo,axisinfo)
	
	plotinfo = {"normalized": {}}
	plotinfo["normalized"]
	plotinfo["normalized"]["x"] = xrange(len(art.views))
	plotinfo["normalized"]["y"] = art.norm_views
	plotinfo["normalized"]["line_style"] = '-'
	plotinfo["normalized"]["line_color"] = 'blue'
	plotinfo["normalized"]["label"] = "Normalized views"

	axisinfo = {"filename": plotfolder+"norm_"+art.link_title, "ylabel": r'Number of page-views', "xticks": xticks, "title": "Hourly progression of "+art.title, "xlim": {"start": 0, "end": len(xticks)}, "ylim": {"start": 0, "end": ceil(max(plotinfo["normalized"]["y"])*100)/100}}
	plot_pattern(plotinfo,axisinfo)

def plot_errors(perc_errors,abs_errors,plotfolder,pattern):
	absinfo = {}
	percinfo = {}
	a = len(list(median(abs_errors["params"],axis=0)))
	xticks = ["" for _ in range(a)]
	i = 0
	while i < a:
		xticks[i] = str(i%24)+"h"
		i+=6
	
	if pattern.has_gamma:
		absinfo["abs_median_param"] = {"x": range(a), "y": list(median(abs_errors["params"],axis=0)), "line_style": "-", "line_color": "red", "label": r"median ($\beta$,$\gamma$)"}
		absinfo["abs_p25_param"] = {"x": range(a), "y": list(percentile(abs_errors["params"],25,axis=0)), "line_style": "--", "line_color": "red", "label": r"25-quantile ($\beta$,$\gamma$)"}
		absinfo["abs_p75_param"] = {"x": range(a), "y": list(percentile(abs_errors["params"],75,axis=0)), "line_style": "--", "line_color": "red", "label": r"75-quantile ($\beta$,$\gamma$)"}

		percinfo["perc_median_param"] = {"x": range(a), "y": list(median(perc_errors["params"],axis=0)), "line_style": "-", "line_color": "red", "label": r"median ($\beta$,$\gamma$)"}
		percinfo["perc_p25_param"] = {"x": range(a), "y": list(percentile(perc_errors["params"],25,axis=0)), "line_style": "--", "line_color": "red", "label": r"25-quantile ($\beta$,$\gamma$)"}
		percinfo["perc_p75_param"] = {"x": range(a), "y": list(percentile(perc_errors["params"],75,axis=0)), "line_style": "--", "line_color": "red", "label": r"75-quantile ($\beta$,$\gamma$)"}

		absinfo["abs_median_gamma"] = {"x": range(a), "y": list(median(abs_errors["gamma_func"],axis=0)), "line_style": "-", "line_color": "blue", "label": r"median ($\beta$, $\gamma(v_1)$)"}
		absinfo["abs_p25_gamma"] = {"x": range(a), "y": list(percentile(abs_errors["gamma_func"],25,axis=0)), "line_style": "--", "line_color": "blue", "label": r"25-quantile ($\beta$, $\gamma(v_1)$)"}
		absinfo["abs_p75_gamma"] = {"x": range(a), "y": list(percentile(abs_errors["gamma_func"],75,axis=0)), "line_style": "--", "line_color": "blue", "label": r"75-quantile ($\beta$, $\gamma(v_1)$)"}
		
		percinfo["perc_median_gamma"] = {"x": range(a), "y": list(median(perc_errors["gamma_func"],axis=0)), "line_style": "-", "line_color": "blue", "label": r"median ($\beta$, $\gamma(v_1)$)"}
		percinfo["perc_p25_gamma"] = {"x": range(a), "y": list(percentile(perc_errors["gamma_func"],25,axis=0)), "line_style": "--", "line_color": "blue", "label": r"25-quantile ($\beta$, $\gamma(v_1)$)"}
		percinfo["perc_p75_gamma"] = {"x": range(a), "y": list(percentile(perc_errors["gamma_func"],75,axis=0)), "line_style": "--", "line_color": "blue", "label": r"75-quantile ($\beta$, $\gamma(v_1)$)"}
	else:
		absinfo["abs_median_param"] = {"x": range(a), "y": list(median(abs_errors["params"],axis=0)), "line_style": "-", "line_color": "red", "label": r"median ($\beta$)"}
		absinfo["abs_p25_param"] = {"x": range(a), "y": list(percentile(abs_errors["params"],25,axis=0)), "line_style": "--", "line_color": "red", "label": r"25-quantile ($\beta$)"}
		absinfo["abs_p75_param"] = {"x": range(a), "y": list(percentile(abs_errors["params"],75,axis=0)), "line_style": "--", "line_color": "red", "label": r"75-quantile ($\beta$)"}

		percinfo["perc_median_param"] = {"x": range(a), "y": list(median(perc_errors["params"],axis=0)), "line_style": "-", "line_color": "red", "label": r"median ($\beta$)"}
		percinfo["perc_p25_param"] = {"x": range(a), "y": list(percentile(perc_errors["params"],25,axis=0)), "line_style": "--", "line_color": "red", "label": r"25-quantile ($\beta$)"}
		percinfo["perc_p75_param"] = {"x": range(a), "y": list(percentile(perc_errors["params"],75,axis=0)), "line_style": "--", "line_color": "red", "label": r"75-quantile ($\beta$)"}

	mins = []
	maxs = []
	for entry in absinfo:
		mins.append(min(absinfo[entry]["y"]))
		maxs.append(max(absinfo[entry]["y"]))
	abs_axisinfo = {"filename": plotfolder+pattern.title.replace(" ","_")+"_abs_error", "ylabel": "Error in page-view prediction", "xticks": xticks[:a], "title": "Plot of hourly error"}
	abs_axisinfo["ylim"] = {}
	abs_axisinfo["ylim"]["start"] = floor(float(min(mins))/100)*100
	abs_axisinfo["ylim"]["end"] = ceil(float(max(maxs))/100)*100
	abs_axisinfo["xlim"] = {}
	abs_axisinfo["xlim"]["start"] = 0
	abs_axisinfo["xlim"]["end"] = a

	plot_pattern(absinfo,abs_axisinfo)
	
	mins = []
	maxs = []
	for entry in percinfo:
		mins.append(min(percinfo[entry]["y"]))
		maxs.append(max(percinfo[entry]["y"]))
	axisinfo = {"filename": plotfolder+pattern.title.replace(" ","_")+"_perc_error", "ylabel": "Normalized error in page-view prediction", "xticks": xticks[:a], "title": "Plot of normalized hourly error"}
	axisinfo["ylim"] = {}
	axisinfo["ylim"]["start"] = floor(float(min(mins))*10)/10
	axisinfo["ylim"]["end"] = ceil(float(max(maxs))*10)/10
	axisinfo["xlim"] = {}
	axisinfo["xlim"]["start"] = 0
	axisinfo["xlim"]["end"] = a

	plot_pattern(percinfo,axisinfo)
	
def plot_cycles(cycles,prefix,yearly=False,monthly=False):
	weekly_plotinfo = {"normal": {}}
	weekly_plotinfo["normal"]["x"] = xrange(7*24)
	weekly_plotinfo["normal"]["y"] = cycles.weekly
	weekly_plotinfo["normal"]["line_style"] = '-'
	weekly_plotinfo["normal"]["line_color"] = 'blue'
	weekly_plotinfo["normal"]["label"] = "Total"

	weekly_axisinfo = {"filename": prefix+"weekly", "ylabel": r'Number of page-views', "ylim": get_ylims(weekly_plotinfo)}
	plot_week(weekly_plotinfo,weekly_axisinfo)

	daily_plotinfo = {"normal": {}}
	daily_plotinfo["normal"]["x"] = range(24)
	daily_plotinfo["normal"]["y"] = cycles.hourly
	daily_plotinfo["normal"]["line_style"] = '-'
	daily_plotinfo["normal"]["line_color"] = 'blue'
	daily_plotinfo["normal"]["label"] = "Total"
	
	daily_axisinfo = {"filename": prefix+"hourly", "ylabel": r'Number of page-views', "ylim": get_ylims(daily_plotinfo)}
	plot_day(daily_plotinfo,daily_axisinfo)

	if yearly:
		plot_yearly_cycles(cycles.yearly_cycles,prefix)
	if monthly:
		plot_monthly_cycles(cycles.monthly_cycles,prefix)

def plot_yearly_cycles(yearly_cycles,prefix,ylims=(None,None)):
	weekly_plotinfo = {}
	daily_plotinfo = {}
	
	for year in yearly_cycles.keys():
		weekly_plotinfo[year] = {}
		weekly_plotinfo[year]["x"] = range(7*24)
		weekly_plotinfo[year]["y"] = yearly_cycles[year]["weekly"]
		weekly_plotinfo[year]["line_style"] = "-"
		weekly_plotinfo[year]["label"] = "Total: " + str(year)
		
		daily_plotinfo[year] = {}
		daily_plotinfo[year]["x"] = range(24)
		daily_plotinfo[year]["y"] = yearly_cycles[year]["hourly"]
		daily_plotinfo[year]["line_style"] = "-"
		daily_plotinfo[year]["label"] = "Total: " + str(year)
	
	weekly_axisinfo = {"filename": prefix+"per_year_weekly", "ylabel": r'Number of page-views', "ylim": get_ylims(weekly_plotinfo)}
	plot_week(weekly_plotinfo,weekly_axisinfo,ylims=ylims)	
	
	daily_axisinfo = {"filename": prefix+"per_year_hourly", "ylabel": r'Number of page-views', "ylim": get_ylims(daily_plotinfo)}
	plot_day(daily_plotinfo,daily_axisinfo,ylims=ylims)

def plot_monthly_cycles(monthly_cycles,prefix,ylims=(None,None)):
	weekly_plotinfo = {}
	daily_plotinfo = {}
	
	for month in monthly_cycles.keys():
		weekly_plotinfo[month] = {}
		weekly_plotinfo[month]["x"] = range(7*24)
		weekly_plotinfo[month]["y"] = monthly_cycles[month]["weekly"]
		weekly_plotinfo[month]["line_style"] = "-"
		weekly_plotinfo[month]["label"] = "Total: " + month
		
		daily_plotinfo[month] = {}
		daily_plotinfo[month]["x"] = range(24)
		daily_plotinfo[month]["y"] = monthly_cycles[month]["hourly"]
		daily_plotinfo[month]["line_style"] = "-"
		daily_plotinfo[month]["label"] = "Total: " + month
	
	weekly_axisinfo = {"filename": prefix+"per_month_weekly", "ylabel": r'Number of page-views', "ylim": get_ylims(weekly_plotinfo)}
	plot_week(weekly_plotinfo,weekly_axisinfo,ylims=ylims)	
	
	daily_axisinfo = {"filename": prefix+"per_month_hourly", "ylabel": r'Number of page-views', "ylim": get_ylims(daily_plotinfo)}
	plot_day(daily_plotinfo,daily_axisinfo,ylims=ylims)

def plot_twin_cycles(plotinfo,axisinfo,timeLength,fileformat="pdf"):
	cm = plt.get_cmap('jet')
	cNorm  = colors.Normalize(vmin=0, vmax=len(plotinfo)-1)
	scalarMap = mplcm.ScalarMappable(norm=cNorm, cmap=cm)
	if timeLength == "day":
		xticks = ["" for i in range(24)]
		for i in range(8):
			xticks[3*i] = str(3*i)+"h"
	elif timeLength == "week":
		xticks = ["" for i in range(7*24)]
		xticks[0] = "Mon"
		xticks[24] = "Tue"
		xticks[48] = "Wed"
		xticks[72] = "Thu"
		xticks[96] = "Fri"
		xticks[120] = "Sat"
		xticks[144] = "Sun"
		for i in range(7):
			xticks[i*24+12] = "12h"

	fig = plt.figure(figsize=(11.7, 8.3))
	ax = fig.add_subplot(111)
	if timeLength == "day":
		# ax.set_title(r"Daily average",size=28)
		ax.set_xlim(0,23)
		plt.xticks(range(24), xticks, rotation=0, size=22)
	elif timeLength == "week":
		# ax.set_title(r"Weekly average",size=28)
		ax.fill_between(range(24), 0, axisinfo["ylim"]["total"]["end"], color='0.75')
		ax.fill_between(range(48,72), 0, axisinfo["ylim"]["total"]["end"], color='0.75')
		ax.fill_between(range(96,120), 0, axisinfo["ylim"]["total"]["end"], color='0.75')
		ax.fill_between(range(144,168), 0, axisinfo["ylim"]["total"]["end"], color='0.75')
		ax.set_xlim(0,167)
		plt.xticks(range(7*24), xticks, rotation="horizontal", size=22)
	
	# ax.set_xlabel(r'',size=28)
	ax.set_ylabel(axisinfo["ylabel"],size=28)
	ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

	main = ax.plot(plotinfo["main"]["x"], plotinfo["main"]["y"], "-k", label=plotinfo["main"]["label"], lw = 2)
	ax.set_ylim(axisinfo["ylim"]["main"]["start"],axisinfo["ylim"]["main"]["end"])

	ax2 = ax.twinx()
	total = ax2.plot(plotinfo["total"]["x"], plotinfo["total"]["y"], "-b", label=plotinfo["total"]["label"], lw = 2)

	ax2.set_ylabel(axisinfo["ylabel"],size=28,color="b")
	ax2.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
	ax2.set_ylim(axisinfo["ylim"]["total"]["start"],axisinfo["ylim"]["total"]["end"])
	for tl in ax.get_yticklabels():
		tl.set_fontsize(22)
	for tl in ax2.get_yticklabels():
		tl.set_color('b')
		tl.set_fontsize(22)
	
	lns = main+total
	labels = [l.get_label() for l in lns]

	ax.legend(lns,labels,loc=0, ncol=1)
	plt.savefig("plots/"+axisinfo["filename"]+"."+fileformat, dpi=600, facecolor='w', edgecolor='w',orientation='landscape', papertype='A4')
	# plt.draw()
	# plt.show()
	plt.close(fig)

def plot_gamma_corr(articles,gamma_func,plotfolder):
	""" Plots related to the gamma function based on v_1 """
	gamma_list = []
	v1_list = []

	rej_gam_list = []
	rej_v1_list = []

	for art in articles:
		err = False
		try:
				log(art.gamma)
				log(art.views[0])
		except ValueError as e:
			if str(e) == "math domain error":
				err = True
			else:
				raise e
			
		if err:
			rej_gam_list.append(art.gamma)
			rej_v1_list.append(art.views[0])
		else:
			gamma_list.append(art.gamma)
			v1_list.append(art.views[0])

		# if -4 < log(art.gamma) < 0.3:
		# 	try:
		# 		if 5 < log(art.views[0]) < 10:
		# 			gamma_list.append(art.gamma)
		# 			v1_list.append(art.views[0])
		# 		else:
		# 			rej_gam_list.append(art.gamma)
		# 			rej_v1_list.append(art.views[0])
		# 	except ValueError:
		# 		pass
		# else:
		# 	rej_gam_list.append(art.gamma)
		# 	rej_v1_list.append(art.views[0])

	xval = [100*x for x in range(181)]
	xval[0] = 1
	yval = [exp(log(x)*gamma_func[0]+gamma_func[1]) for x in xval]

	r, prob = pearsonr(v1_list,gamma_list)
	suptitle = r'$v_1$ vs $\gamma$ (Pearson: %.4f)' % r

	corr_scatterinfo = {"good": {}, "rejected": {}}
	corr_scatterinfo["good"]["x"] = v1_list
	corr_scatterinfo["good"]["y"] = gamma_list
	corr_scatterinfo["good"]["markersize"] = 25
	corr_scatterinfo["good"]["color"] = 'blue'
	corr_scatterinfo["good"]["marker"] = 'o'
	corr_scatterinfo["good"]["label"] = 'article'
	corr_scatterinfo["rejected"]["x"] = rej_v1_list
	corr_scatterinfo["rejected"]["y"] = rej_gam_list
	corr_scatterinfo["rejected"]["markersize"] = 25
	corr_scatterinfo["rejected"]["color"] = 'red'
	corr_scatterinfo["rejected"]["marker"] = 's'
	corr_scatterinfo["rejected"]["label"] = 'out-lier'
	corr_plotinfo = {"line": {}}
	corr_plotinfo["line"]["x"] = xval
	corr_plotinfo["line"]["y"] = yval
	corr_plotinfo["line"]["line_color"] = 'black'
	corr_plotinfo["line"]["line_style"] =  '--'
	corr_plotinfo["line"]["label"] = r'$\gamma$-function'

	corr_axisinfo = {"filename": plotfolder+"prom_corr", "suptitle": suptitle, "ylim": {"log": {"start": 0.001, "end": 3}, "linear": {"start": 0, "end": 1.3}}, "xlim": {"log": {"start": 100, "end": 17000}, "linear": {"start": 100, "end": 17000}}}
	plot_scatter(corr_scatterinfo,corr_plotinfo,corr_axisinfo)
	plot_histogram(v1_list,100,plotfolder+"hist_peaks")

def plot_scatter(scatterinfo,plotinfo,axisinfo):
	fig = plt.figure(figsize=(11.7,8.3))
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
	fig.suptitle(axisinfo["suptitle"],size=28)

	ax = fig.add_subplot(211)
	ax.set_xlabel(r'$v_1$',size=28)
	ax.set_ylabel(r'$\gamma$',size=28)
	for entry in plotinfo:
		ax.plot(plotinfo[entry]["x"], plotinfo[entry]["y"], plotinfo[entry]["line_style"], color=plotinfo[entry]["line_color"], lw = 2)
	for entry in scatterinfo:
		ax.scatter(scatterinfo[entry]["x"], scatterinfo[entry]["y"], scatterinfo[entry]["markersize"], scatterinfo[entry]["color"],scatterinfo[entry]["marker"])
	ax.set_ylim(axisinfo["ylim"]["log"]["start"],axisinfo["ylim"]["log"]["end"])
	ax.set_xlim(axisinfo["xlim"]["log"]["start"],axisinfo["xlim"]["log"]["end"])
	ax.set_yscale('log')
	ax.set_xscale('log')

	ax1 = fig.add_subplot(212)
	ax1.set_xlabel(r'$v_1$',size=28)
	ax1.set_ylabel(r'$\gamma$',size=28)
	for entry in scatterinfo:
		ax1.scatter(scatterinfo[entry]["x"], scatterinfo[entry]["y"], scatterinfo[entry]["markersize"], scatterinfo[entry]["color"],scatterinfo[entry]["marker"], label=scatterinfo[entry]["label"])
	for entry in plotinfo:
		ax1.plot(plotinfo[entry]["x"], plotinfo[entry]["y"], plotinfo[entry]["line_style"], color=plotinfo[entry]["line_color"], label=plotinfo[entry]["label"], lw = 2)
	ax1.yaxis.set_ticks([float(x)/10 for x in range(14)])
	ax1.set_ylim(axisinfo["ylim"]["linear"]["start"],axisinfo["ylim"]["linear"]["end"])
	ax1.set_xlim(axisinfo["xlim"]["linear"]["start"],axisinfo["xlim"]["linear"]["end"])
	plt.xticks(size=22)
	plt.yticks(size=22)
	ax1.legend(loc=0,ncol=1,scatterpoints=1)
	plt.savefig("plots/"+axisinfo["filename"]+".pdf", dpi=600, facecolor='w', edgecolor='w',orientation='landscape', papertype='A4')
	# plt.draw()
	# plt.show()
	plt.close(fig)

def plot_histogram(data,bins,filename):
	fig = plt.figure(figsize=(11.7, 8.3))
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
	ax = fig.add_subplot(111)
	ax.set_title(r'Histogram of the first peaks in page-views',size=28)
	ax.set_xlabel(r'Number of page-views at time $t=1$ ($v_1$)',size=28)
	ax.set_ylabel(r'Number of articles',size=28)

	plt.hist(data,bins=bins)
	# plt.draw()
	plt.xticks(size=22)
	plt.yticks(size=22)
	plt.savefig("plots/"+filename+".pdf", dpi=600, facecolor='w', edgecolor='w',orientation='landscape', papertype='A4')
	# plt.show()
	plt.close(fig)

def plot_subplots(subplotinfo,axisinfo,x,y,common_legend=False):
	if x == 1 or y == 1:
		subplots_singlerow(subplotinfo,axisinfo,x,y,common_legend)
	else:
		subplots_multirow(subplotinfo,axisinfo,x,y,common_legend)
	
def subplots_singlerow(subplotinfo,axisinfo,x,y,common_legend):
	fig, axarr = plt.subplots(x,y,figsize=(11.7, 8.3))
	
	keys = subplotinfo.keys()
	plt.title(axisinfo["title"],size=28)
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
	for i in range(max(x,y)):
		key = keys[i]
		labels = []
		lines = []
		try:
			axarr[i].set_title(axisinfo[key]["title"],size=12)
		except KeyError:
			pass
		try: 
			axarr[i].set_xlabel(axisinfo[key]["xlabel"],size=12)
		except KeyError:
			pass
		try:
			axarr[i].set_ylabel(axisinfo[key]["ylabel"],size=12)
		except KeyError:
			pass
		axarr[i].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
		if "scale" in axisinfo and axisinfo["scale"] == "log":
			axarr[i].set_yscale('log')
		else:
			k=0
			while k < len(axisinfo[key]["xticks"]):
				if axisinfo[key]["ylim"]["start"] < 0:
					axarr[i].fill_between(range(24+48*k,48*(k+1)), axisinfo[key]["ylim"]["start"], axisinfo[key]["ylim"]["end"], color='0.75')
				else:
					axarr[i].fill_between(range(24+48*k,48*(k+1)), 0, axisinfo[key]["ylim"]["end"], color='0.75')
				k+=1

		try:
			line, = axarr[i].plot(subplotinfo[key]["x"], subplotinfo[key]["y"], subplotinfo[key]["line_style"], color=subplotinfo[key]["line_color"], label=subplotinfo[key]["label"], lw = 2)
			lines.add(line)
			labels.add(subplotinfo[key]["label"].split(',')[0])
		except KeyError:
			for entry in subplotinfo[key]:
				line, = axarr[i].plot(subplotinfo[key][entry]["x"], subplotinfo[key][entry]["y"], subplotinfo[key][entry]["line_style"], color=subplotinfo[key][entry]["line_color"], label=subplotinfo[key][entry]["label"], lw = 2)
				lines.append(line)
				labels.append(subplotinfo[key][entry]["label"].split(',')[0])

		axarr[i].set_xlim(axisinfo[key]["xlim"]["start"],axisinfo[key]["xlim"]["end"])
		axarr[i].set_ylim(axisinfo[key]["ylim"]["start"],axisinfo[key]["ylim"]["end"])
		axarr[i].set_xticks(xrange(len(axisinfo[key]["xticks"])))
		axarr[i].set_xticklabels(axisinfo[key]["xticks"])
		if not common_legend:
			axarr[i].legend(loc=0, ncol=1,fontsize=12)
	if common_legend:
		fig.legend(lines,labels,loc='lower center', ncol=len(labels),fontsize=12)

	plt.savefig("plots/"+axisinfo["filename"]+".pdf", dpi=600, facecolor='w', edgecolor='w',orientation='landscape', papertype='A4')
	plt.close(fig)

def subplots_multirow(subplotinfo,axisinfo,x,y,common_legend):
	fig, axarr = plt.subplots(x,y,figsize=(11.7, 8.3))
	
	keys = subplotinfo.keys()
	plt.title(axisinfo["title"],size=28)
	plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
	for i in range(x):

		for j in range(y):
			key = keys[i*x+j]
			labels = []
			lines = []
			try:
				axarr[i,j].set_title(axisinfo[key]["title"],size=12)
			except KeyError:
				pass
			try: 
				axarr[i,j].set_xlabel(axisinfo[key]["xlabel"],size=12)
			except KeyError:
				pass
			try:
				axarr[i,j].set_ylabel(axisinfo[key]["ylabel"],size=12)
			except KeyError:
				pass
			axarr[i,j].ticklabel_format(style='sci', axis='y', scilimits=(0,0))
			if "scale" in axisinfo and axisinfo["scale"] == "log":
				axarr[i,j].set_yscale('log')
			else:
				try:
					k=0
					while k < len(axisinfo[key]["xticks"]):
						if axisinfo[key]["ylim"]["start"] < 0:
							axarr[i,j].fill_between(range(24+48*k,48*(k+1)), axisinfo[key]["ylim"]["start"], axisinfo[key]["ylim"]["end"], color='0.75')
						else:
							axarr[i,j].fill_between(range(24+48*k,48*(k+1)), 0, axisinfo[key]["ylim"]["end"], color='0.75')
						k+=1
				except KeyError:
					pass

			try:
				line, = axarr[i,j].plot(subplotinfo[key]["x"], subplotinfo[key]["y"], subplotinfo[key]["line_style"], color=subplotinfo[key]["line_color"], label=subplotinfo[key]["label"], lw = 2)
				lines.add(line)
				labels.add(subplotinfo[key]["label"].split(',')[0])
			except KeyError:
				for entry in subplotinfo[key]:
					line, = axarr[i,j].plot(subplotinfo[key][entry]["x"], subplotinfo[key][entry]["y"], subplotinfo[key][entry]["line_style"], color=subplotinfo[key][entry]["line_color"], label=subplotinfo[key][entry]["label"], lw = 2)
					lines.append(line)
					labels.append(subplotinfo[key][entry]["label"].split(',')[0])
			
			axarr[i,j].set_xlim(axisinfo[key]["xlim"]["start"],axisinfo[key]["xlim"]["end"])
			axarr[i,j].set_ylim(axisinfo[key]["ylim"]["start"],axisinfo[key]["ylim"]["end"])
			axarr[i,j].set_xticks(xrange(len(axisinfo[key]["xticks"])))
			axarr[i,j].set_xticklabels(axisinfo[key]["xticks"])
			
			if not common_legend:
				axarr[i,j].legend(loc=0, ncol=1,fontsize=12)
	if common_legend:
		fig.legend(lines,labels,loc='lower center', ncol=len(labels),fontsize=12)

	plt.savefig("plots/"+axisinfo["filename"]+".pdf", dpi=600, facecolor='w', edgecolor='w',orientation='landscape', papertype='A4')
	plt.close(fig)