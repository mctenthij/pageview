#!/usr/bin/python
import csv
from datetime import datetime
import os

from scipy.io import loadmat
import numpy as np

from article import MainPage, TotalPage, Article, Average
from plotter import plot_twin_cycles, plot_yearly_cycles, plot_monthly_cycles, plot_pattern, plot_subplots, plot_day
from util import calc_average, get_ylims, cumsum, redistribute, rescale_time, rescale_to_normal
from simulator import Simulator
from analyser import Analyser
from pattern import PromotionPattern
from redistributor import Redistributor

def main():
	patterns = {
	"en": {"featured": '<dt><b>([\w\s]*?)</b></dt>\n</dl>\n[<div ]*[!:;,"#-=_.()%<>/\w\s\n]*[</div>\n]*<p>[\w\s"]*[<\w>]*[\w\s"]*<b>[<=:">\w\s]*<a href="/wiki/([!:,-_.()%/\w\s]*)" title="(.*?)">.*?</a>[</span>]*</b>',"history": '<b>[<=:\">\w\s]*<a href="/wiki/([!:,-.()%/\w\s]*)" title="(.*?)[" class="mw\-redirect]*">.*?</a>[</span>]*</b>'}, 
	"nl": {"featured": '<td valign="top"[ width="50%"]*>\n<center><big><a href="/wiki/Sjabloon:Uitgelicht_[\w\s_]*" title="Sjabloon:Uitgelicht [\w\s]*?">([\w\s]*?)</a></big></center>\n[<p><span ]*.*?[</span></p>\n]*<p>[<i>]*<a href="/wiki/([!:,-.()%/\w\s]*)" title="(.*?)[" class="mw\-redirect]*">.*?</span></a>[</i>]*</p>'}, 
	"de": {"featured": '<li>([0-9]*?.[0-9]*?.[0-9]*?) <a href="/wiki/([!:,-.()%/\w\s]*)" title="(.*?)[" class="mw\-redirect]*">.*?</a>[ (erneut)]*</li>'}, 
	"es": {"featured": '<td><a href="/wiki/([!:,-.()%/\w\s]*)" title="(.*?)">.*?</a>.*?</td>\n<td>.*?</td>\n<td>([\w\s]*?) - [\w\s]*?</td>'}
	}

	prom_en = PromotionPattern("Today's Featured Article",1,[0,-1,-2,-3],"en","Main_Page",patterns["en"]["featured"],has_gamma=True,archLink="http://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_article/{}",archLink_fmt="%B_%Y",archTime_fmt="%d %B")
	prom_nl = PromotionPattern("Uitgelicht",1,[0],"nl","Hoofdpagina",patterns["nl"]["featured"],has_gamma=False,archLink="http://nl.wikipedia.org/wiki/Wikipedia:Uitgelicht/{}",archLink_fmt="%B",archTime_fmt="%d %B")
	prom_de = PromotionPattern("Artikel des Tages",1,[0],"de","Wikipedia_Hauptseite",patterns["de"]["featured"],has_gamma=False,archLink="http://de.wikipedia.org/wiki/Wikipedia:Hauptseite/Artikel_des_Tages/Chronologie_{}",archLink_fmt="%Y",archTime_fmt="%d.%m.%Y")
	prom_es = PromotionPattern("Articulo destacado",4,range(-15,1),"es","Wikipedia_Portada",patterns["es"]["featured"],has_gamma=True,archLink="https://es.wikipedia.org/wiki/Wikipedia:Candidatos_a_art%C3%ADculos_destacados/Destacados_{}",archLink_fmt="%Y",archTime_fmt="%d de %B")
	prom_es2 = PromotionPattern("Articulo destacado",4,range(-15,1),"es","Wikipedia_Portada",patterns["es"]["featured"],start=6,has_gamma=True,archLink="https://es.wikipedia.org/wiki/Wikipedia:Candidatos_a_art%C3%ADculos_destacados/Destacados_{}",archLink_fmt="%Y",archTime_fmt="%d de %B")
	
	en = Simulator(datetime(2013,1,1,0),datetime(2015,7,1,0),prom_en,overall=True,boolplot=False)
	en.load_data()
	en.run()

	nl = Simulator(datetime(2015,1,1,0),datetime(2015,12,1,0),prom_nl,overall=True,boolplot=False)
	nl.load_data()
	nl.run()

	de = Simulator(datetime(2015,1,1,0),datetime(2015,12,1,0),prom_de,overall=True,boolplot=False)
	de.load_data()
	de.run()

	es = Simulator(datetime(2015,1,1,0),datetime(2015,12,1,0),prom_es,overall=True,boolplot=False)
	es.load_data()
	es.run()
	
	es2 = Simulator(datetime(2015,1,1,0),datetime(2015,12,1,0),prom_es2,overall=True,boolplot=False)
	es2.load_data()
	es2.run()

	# # Process old dataset, based on Matlab data files, and new dataset
	# process_old_data(en)
	
	# # Plot all cycles
	# compare_wikimedia_own()
	# languages_cycles()
	
	# # Pattern plots
	# average_patterns(en,nl,de,es)
	# example_progression(en,nl,de,es)
	# prediction_examples(en,nl,de,es)
	
	# en_total_cycle, en_total_pattern, en_total_cycle_axis, en_total_pattern_axis = redistribution_plots(en,cycle="total")
	# en_main_cycle, en_main_pattern, en_main_cycle_axis, en_main_pattern_axis = redistribution_plots(en,cycle="main")
	# nl_total_cycle, nl_total_pattern, nl_total_cycle_axis, nl_total_pattern_axis = redistribution_plots(nl,cycle="total")
	# nl_main_cycle, nl_main_pattern, nl_main_cycle_axis, nl_main_pattern_axis = redistribution_plots(nl,cycle="main")
	# de_total_cycle, de_total_pattern, de_total_cycle_axis, de_total_pattern_axis = redistribution_plots(de,cycle="total")
	# de_main_cycle, de_main_pattern, de_main_cycle_axis, de_main_pattern_axis = redistribution_plots(de,cycle="main")
	# es_total_cycle, es_total_pattern, es_total_cycle_axis, es_total_pattern_axis = redistribution_plots(es,cycle="total")
	# es_main_cycle, es_main_pattern, es_main_cycle_axis, es_main_pattern_axis = redistribution_plots(es,cycle="main")

	# subplotinfo = {1: en_total_cycle, 2: nl_total_cycle, 3: de_total_cycle, 4: es_total_cycle}
	# axisinfo = {"title": "", "filename": "redistributed_cycles_total", 1: en_total_cycle_axis, 2: nl_total_cycle_axis, 3: de_total_cycle_axis, 4: es_total_cycle_axis}
	# plot_subplots(subplotinfo,axisinfo,2,2,common_legend=True)

	# subplotinfo2 = {1: en_total_pattern, 2: nl_total_pattern, 3: de_total_pattern, 4: es_total_pattern}
	# axisinfo2 = {"title": "", "filename": "redistributed_patterns_total", 1: en_total_pattern_axis, 2: nl_total_pattern_axis, 3: de_total_pattern_axis, 4: es_total_pattern_axis}
	# plot_subplots(subplotinfo2,axisinfo2,2,2,common_legend=True)

	# subplotinfo3 = {1: en_main_cycle, 2: nl_main_cycle, 3: de_main_cycle, 4: es_main_cycle}
	# axisinfo3 = {"title": "", "filename": "redistributed_cycles_main", 1: en_main_cycle_axis, 2: nl_main_cycle_axis, 3: de_main_cycle_axis, 4: es_main_cycle_axis}
	# plot_subplots(subplotinfo3,axisinfo3,2,2,common_legend=True)

	# subplotinfo4 = {1: en_main_pattern, 2: nl_main_pattern, 3: de_main_pattern, 4: es_main_pattern}
	# axisinfo4 = {"title": "", "filename": "redistributed_patterns_main", 1: en_main_pattern_axis, 2: nl_main_pattern_axis, 3: de_main_pattern_axis, 4: es_main_pattern_axis}
	# plot_subplots(subplotinfo4,axisinfo4,2,2,common_legend=True)

def process_old_data(en):
	mp = MainPage("en","Main_Page")
	tp = TotalPage("en")

	matdata = loadmat("mat_data/hourly_weekly.mat")
	articledata = loadmat("mat_data/Total.mat")

	tp.set_weekly(list(np.mean(matdata["weekly_total"],axis=0)))
	mp.set_weekly(list(np.mean(matdata["weekly_main"],axis=0)*1000))
	
	tp.set_hourly(list(np.mean(matdata["hourly_total"],axis=0)))
	mp.set_hourly(list(np.mean(matdata["hourly_main"],axis=0)*1000))

	patterns = { "en": {"featured": '<dt><b>([\w\s]*?)</b></dt>\n</dl>\n[<div ]*[!:;,"#-=_.()%<>/\w\s\n]*[</div>\n]*<p>[\w\s"]*[<\w>]*[\w\s"]*<b>[<=:">\w\s]*<a href="/wiki/([!:,-_.()%/\w\s]*)" title="(.*?)">.*?</a>[</span>]*</b>'} }

	prom_en = PromotionPattern("Today's Featured Article",1,[0,-1,-2,-3],"en","Main_Page",patterns["en"]["featured"],has_gamma=True,archLink="http://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_article/{}",archLink_fmt="%B_%Y",archTime_fmt="%d %B")
	
	articles = []
	average = Average(prom_en)
	overall = False
	plotall = False
	(num_articles,length) = articledata["views"].shape
	
	for i in range(num_articles):
		art = Article(str(i),str(i),"January 1, 1999",prom_en)
		views = list(articledata["views"][i])
		art.set_views(views[1:]+[views[-1]])
		articles.append(art)
		average.add_art(art)

	average.calc_av_views()

	if overall:
		extra = "_overall"
	else:
		extra = "_single"

	plotdir = "TP_"+prom_en.lang+"_old_opt_c"+extra

	an = Analyser(articles,average,average.views,prom_en,tp.hourly,plotdir,None)
	if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/plots/"+plotdir):
		os.makedirs(os.path.dirname(os.path.abspath(__file__))+"/plots/"+plotdir)
	an.run(overall,plotall)
	print "analysis performed:", plotdir

	plotdir = "MP_"+prom_en.lang+"_old_opt_c"+extra

	an = Analyser(articles,average,average.views,prom_en,mp.hourly,plotdir,None)
	if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+"/plots/"+plotdir):
		os.makedirs(os.path.dirname(os.path.abspath(__file__))+"/plots/"+plotdir)
	an.run(overall,plotall)
	print "analysis performed:", plotdir

	en.run()

def average_patterns(en,nl,de,es):
	matdata = loadmat("mat_data/Total.mat")

	xticks = ["" for i in range(len(en.average.views)+1)]
	i = 0
	while i < len(en.average.views):
		xticks[i] = str(i%24)+"h"
		i+=6

	plotinfo = {"new": {}, "old": {}}
	plotinfo["new"]["x"] = range(len(en.average.views))
	plotinfo["new"]["y"] = en.average.views
	plotinfo["new"]["line_style"] = '-'
	plotinfo["new"]["line_color"] = 'blue'
	plotinfo["new"]["label"] = "Average article: 2013-2015"
	plotinfo["old"]["x"] = range(len(list(np.mean(matdata["views"],axis=0))))
	plotinfo["old"]["y"] = list(np.mean(matdata["views"],axis=0))[1:]+[list(np.mean(matdata["views"],axis=0))[-1]]
	plotinfo["old"]["line_style"] = '-'
	plotinfo["old"]["line_color"] = 'black'
	plotinfo["old"]["label"] = "Average article: 2007-2010"

	axisinfo = {"filename": "av_promoted_english", "ylabel": r'Number of page-views', "xticks": xticks, "title": "", "xlim": {"start": min(range(len(xticks))), "end": max(range(len(xticks)))}, "ylim": get_ylims(plotinfo)}
	plot_pattern(plotinfo,axisinfo)

	plotinfo = {"main": {}, "total": {}}
	plotinfo["main"]["x"] = range(len(nl.average.views))
	plotinfo["main"]["y"] = nl.average.views
	plotinfo["main"]["line_style"] = '-'
	plotinfo["main"]["line_color"] = 'blue'
	plotinfo["main"]["label"] = "Average article: Dutch"
	plotinfo["total"]["x"] = range(len(de.average.views))
	plotinfo["total"]["y"] = de.average.views
	plotinfo["total"]["line_style"] = '-'
	plotinfo["total"]["line_color"] = 'black'
	plotinfo["total"]["label"] = "Average article: German"

	axisinfo = {"filename": "av_promoted_nl_de", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 0, "end": 1500}, "main": {"start": 0, "end": 120}}}
	plot_twin_cycles(plotinfo,axisinfo,"day")

	xticks = ["" for i in range(len(es.average.views)+1)]
	i = 0
	while i < len(es.average.views):
		xticks[i] = str(i%24)+"h"
		i+=24

	plotinfo = {"new": {}}
	plotinfo["new"]["x"] = range(len(es.average.views))
	plotinfo["new"]["y"] = es.average.views
	plotinfo["new"]["line_style"] = '-'
	plotinfo["new"]["line_color"] = 'blue'
	plotinfo["new"]["label"] = "Average article: Spanish"

	axisinfo = {"filename": "av_promoted_spanish", "ylabel": r'Number of page-views', "xticks": xticks, "title": "", "xlim": {"start": min(range(len(xticks))), "end": max(range(len(xticks)))}, "ylim": get_ylims(plotinfo)}
	plot_pattern(plotinfo,axisinfo)

def compare_wikimedia_own():
	mp = MainPage("en","Main_Page")
	mp.get_monthly_cycles()

	monthly_cycles = {}
	months = []
	with open("mat_data/wikimedia_patterns.csv") as csvfile:
		temp = {}	
		has_header = csv.Sniffer().has_header(csvfile.read(1024))
		csvfile.seek(0)
		csvread = csv.reader(csvfile,delimiter=';')
		if has_header:
			next(csvread)
		for row in csvread:
			dt = datetime.strptime(row[0]+" "+row[1],"%d-%m-%Y %H")
			hour_views = int(row[2])

			if dt.strftime("%B %Y")+" (WM)" not in temp:
				months.append(dt.strftime("%B %Y"))
				temp[dt.strftime("%B %Y")+" (WM)"] = {}
				temp[dt.strftime("%B %Y")+" (WM)"]["hourly_totals"] = np.zeros(24).tolist()
				temp[dt.strftime("%B %Y")+" (WM)"]["hourly_num"] = np.zeros(24).tolist()
				temp[dt.strftime("%B %Y")+" (WM)"]["weekly_totals"] = np.zeros(7*24).tolist()
				temp[dt.strftime("%B %Y")+" (WM)"]["weekly_num"] = np.zeros(7*24).tolist()
			temp[dt.strftime("%B %Y")+" (WM)"]["hourly_totals"][dt.hour] += hour_views
			temp[dt.strftime("%B %Y")+" (WM)"]["hourly_num"][dt.hour] += 1
			
			temp[dt.strftime("%B %Y")+" (WM)"]["weekly_totals"][24*dt.weekday()+dt.hour] += hour_views
			temp[dt.strftime("%B %Y")+" (WM)"]["weekly_num"][24*dt.weekday()+dt.hour] += 1

		for month in temp:
			monthly_cycles[month] = {}		
			monthly_cycles[month]["hourly"] = calc_average(temp[month]["hourly_totals"],temp[month]["hourly_num"])
			monthly_cycles[month]["weekly"] = calc_average(temp[month]["weekly_totals"],temp[month]["weekly_num"])

	for month in months:
		monthly_cycles[month] = mp.monthly_cycles[month.replace(" ","_")]

	for month in monthly_cycles:
		monthly_cycles[month]["hourly"] = [x/sum(monthly_cycles[month]["hourly"]) for x in monthly_cycles[month]["hourly"]]
		monthly_cycles[month]["weekly"] = [x/sum(monthly_cycles[month]["weekly"]) for x in monthly_cycles[month]["weekly"]]

	plot_monthly_cycles(monthly_cycles,"MP_",ylims=(0,0.1))

def languages_cycles():
	mp = MainPage("en","Main_Page")
	tp = TotalPage("en")
	mp.get_cycles()
	mp.get_yearly_cycles()
	tp.get_cycles()
	tp.get_yearly_cycles()

	matdata = loadmat("mat_data/hourly_weekly.mat")

	MP_cycles = mp.yearly_cycles
	TP_cycles = tp.yearly_cycles
	for year in mp.yearly_cycles:
		cycle_hm = mp.yearly_cycles[year]["hourly"]
		cycle_wm = mp.yearly_cycles[year]["weekly"]
		cycle_ht = tp.yearly_cycles[year]["hourly"]
		cycle_wt = tp.yearly_cycles[year]["weekly"]
		MP_cycles[year] = {"hourly": [cycle_hm[x]/sum(cycle_hm) for x in range(len(cycle_hm))], "weekly": [cycle_wm[x]/sum(cycle_wm) for x in range(len(cycle_wm))]}
		TP_cycles[year] = {"hourly": [cycle_ht[x]/sum(cycle_ht) for x in range(len(cycle_ht))], "weekly": [cycle_wt[x]/sum(cycle_wt) for x in range(len(cycle_wt))]}

	yw_comb = [(2007,0,23),(2008,23,389),(2009,389,754),(2010,754,844)]
	for (year,start,end) in yw_comb:
		cycle_hm = list(np.mean(matdata["hourly_main"][range(start,end)],axis=0)*1000)
		cycle_ht = list(np.mean(matdata["hourly_total"][range(start,end)],axis=0)*1000)
		MP_cycles[year] = {"hourly": [cycle_hm[x]/sum(cycle_hm) for x in range(len(cycle_hm))], "weekly": list(np.zeros(168))}
		TP_cycles[year] = {"hourly": [cycle_ht[x]/sum(cycle_ht) for x in range(len(cycle_ht))], "weekly": list(np.zeros(168))}
	
	plot_yearly_cycles(TP_cycles,"TP_",ylims=(0.02,0.07))
	plot_yearly_cycles(MP_cycles,"MP_",ylims=(0.02,0.07))

	# MP_cycles[2007] = {"hourly": list(np.mean(matdata["hourly_main"][range(0,23)],axis=0)*1000), "weekly": list(np.zeros(168))}
	# MP_cycles[2008] = {"hourly": list(np.mean(matdata["hourly_main"][range(23,389)],axis=0)*1000), "weekly": list(np.zeros(168))}
	# MP_cycles[2009] = {"hourly": list(np.mean(matdata["hourly_main"][range(389,754)],axis=0)*1000), "weekly": list(np.zeros(168))}
	# MP_cycles[2010] = {"hourly": list(np.mean(matdata["hourly_main"][range(754,844)],axis=0)*1000), "weekly": list(np.zeros(168))}

	# TP_cycles[2007] = {"hourly": list(np.mean(matdata["hourly_total"][range(0,23)],axis=0)), "weekly": list(np.zeros(168))}
	# TP_cycles[2008] = {"hourly": list(np.mean(matdata["hourly_total"][range(23,389)],axis=0)), "weekly": list(np.zeros(168))}
	# TP_cycles[2009] = {"hourly": list(np.mean(matdata["hourly_total"][range(389,754)],axis=0)), "weekly": list(np.zeros(168))}
	# TP_cycles[2010] = {"hourly": list(np.mean(matdata["hourly_total"][range(754,844)],axis=0)), "weekly": list(np.zeros(168))}

	# plot_yearly_cycles(TP_cycles,"TP_",ylims=(0,16e6))
	# plot_yearly_cycles(MP_cycles,"MP_")

	weekly_plotinfo = {"main": {}, "total": {}}
	weekly_plotinfo["total"]["x"] = range(7*24)
	weekly_plotinfo["total"]["y"] = tp.weekly
	weekly_plotinfo["total"]["label"] = "Total Page-views"
	weekly_plotinfo["main"]["x"] = range(7*24)
	weekly_plotinfo["main"]["y"] = mp.weekly
	weekly_plotinfo["main"]["label"] = "Main Page-views"

	weekly_axisinfo = {"filename": "weekly_pattern_new", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 7.e6, "end": 13.5e6}, "main": {"start": 4e5, "end": 6.5e5}}}
	plot_twin_cycles(weekly_plotinfo,weekly_axisinfo,"week")

	daily_plotinfo = {"main": {}, "total": {}}
	daily_plotinfo["total"]["x"] = range(24)
	daily_plotinfo["total"]["y"] = tp.hourly
	daily_plotinfo["total"]["label"] = "Total Page-views"
	daily_plotinfo["main"]["x"] = range(24)
	daily_plotinfo["main"]["y"] = mp.hourly
	daily_plotinfo["main"]["label"] = "Main Page-views"

	daily_axisinfo = {"filename": "daily_pattern_new", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 8.e6, "end": 12.5e6}, "main": {"start": 4e5, "end": 6.5e5}}}
	plot_twin_cycles(daily_plotinfo,daily_axisinfo,"day")

	weekly_plotinfo = {"main": {}, "total": {}}
	weekly_plotinfo["total"]["x"] = range(7*24)
	weekly_plotinfo["total"]["y"] = list(np.mean(matdata["weekly_total"],axis=0))
	weekly_plotinfo["total"]["label"] = "Total Page-views"
	weekly_plotinfo["main"]["x"] = range(7*24)
	weekly_plotinfo["main"]["y"] = list(np.mean(matdata["weekly_main"],axis=0)*1000)
	weekly_plotinfo["main"]["label"] = "Main Page-views"

	weekly_axisinfo = {"filename": "weekly_pattern_old", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 1.3e6, "end": 1.9e6}, "main": {"start": 1e5, "end": 4e5}}}
	plot_twin_cycles(weekly_plotinfo,weekly_axisinfo,"week")

	daily_plotinfo = {"main": {}, "total": {}}
	daily_plotinfo["total"]["x"] = range(24)
	daily_plotinfo["total"]["y"] = list(np.mean(matdata["hourly_total"],axis=0))
	daily_plotinfo["total"]["label"] = "Total Page-views"
	daily_plotinfo["main"]["x"] = range(24)
	daily_plotinfo["main"]["y"] = list(np.mean(matdata["hourly_main"],axis=0)*1000)
	daily_plotinfo["main"]["label"] = "Main Page-views"

	daily_axisinfo = {"filename": "daily_pattern_old", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 1.4e6, "end": 1.8e6}, "main": {"start": 1.5e5, "end": 3.5e5}}}
	plot_twin_cycles(daily_plotinfo,daily_axisinfo,"day")

	mp_nl = MainPage("nl","Hoofdpagina")
	mp_nl.get_cycles()
	tp_nl = TotalPage("nl")
	tp_nl.get_cycles()
	mp_de = MainPage("de","Wikipedia_Hauptseite")
	mp_de.get_cycles()
	tp_de = TotalPage("de")
	tp_de.get_cycles()
	mp_es = MainPage("es","Wikipedia_Portada")
	mp_es.get_cycles()
	tp_es = TotalPage("es")
	tp_es.get_cycles()

	weekly_plotinfo = {"main": {}, "total": {}}
	weekly_plotinfo["total"]["x"] = range(7*24)
	weekly_plotinfo["total"]["y"] = tp_nl.weekly
	weekly_plotinfo["total"]["label"] = "Total Page-views"
	weekly_plotinfo["main"]["x"] = range(7*24)
	weekly_plotinfo["main"]["y"] = mp_nl.weekly
	weekly_plotinfo["main"]["label"] = "Main Page-views"

	weekly_axisinfo = {"filename": "nl_weekly_pattern_new", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 0.5e5, "end": 4.e5}, "main": {"start": 0, "end": 9.e3}}}
	plot_twin_cycles(weekly_plotinfo,weekly_axisinfo,"week")

	daily_plotinfo = {"main": {}, "total": {}}
	daily_plotinfo["total"]["x"] = range(24)
	daily_plotinfo["total"]["y"] = tp_nl.hourly
	daily_plotinfo["total"]["label"] = "Total Page-views"
	daily_plotinfo["main"]["x"] = range(24)
	daily_plotinfo["main"]["y"] = mp_nl.hourly
	daily_plotinfo["main"]["label"] = "Main Page-views"

	daily_axisinfo = {"filename": "nl_daily_pattern_new", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 0.5e5, "end": 3.5e5}, "main": {"start": 0, "end": 8.e3}}}
	plot_twin_cycles(daily_plotinfo,daily_axisinfo,"day")

	weekly_plotinfo = {"main": {}, "total": {}}
	weekly_plotinfo["total"]["x"] = range(7*24)
	weekly_plotinfo["total"]["y"] = tp_de.weekly
	weekly_plotinfo["total"]["label"] = "Total Page-views"
	weekly_plotinfo["main"]["x"] = range(7*24)
	weekly_plotinfo["main"]["y"] = mp_de.weekly
	weekly_plotinfo["main"]["label"] = "Main Page-views"

	weekly_axisinfo = {"filename": "de_weekly_pattern_new", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 0, "end": 2.5e6}, "main": {"start": 0.5e4, "end": 9e4}}}
	plot_twin_cycles(weekly_plotinfo,weekly_axisinfo,"week")

	daily_plotinfo = {"main": {}, "total": {}}
	daily_plotinfo["total"]["x"] = range(24)
	daily_plotinfo["total"]["y"] = tp_de.hourly
	daily_plotinfo["total"]["label"] = "Total Page-views"
	daily_plotinfo["main"]["x"] = range(24)
	daily_plotinfo["main"]["y"] = mp_de.hourly
	daily_plotinfo["main"]["label"] = "Main Page-views"

	daily_axisinfo = {"filename": "de_daily_pattern_new", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 0, "end": 2e6}, "main": {"start": 0.5e4, "end": 7e4}}}
	plot_twin_cycles(daily_plotinfo,daily_axisinfo,"day")

	weekly_plotinfo = {"main": {}, "total": {}}
	weekly_plotinfo["total"]["x"] = range(7*24)
	weekly_plotinfo["total"]["y"] = tp_es.weekly
	weekly_plotinfo["total"]["label"] = "Total Page-views"
	weekly_plotinfo["main"]["x"] = range(7*24)
	weekly_plotinfo["main"]["y"] = mp_es.weekly
	weekly_plotinfo["main"]["label"] = "Main Page-views"

	weekly_axisinfo = {"filename": "es_weekly_pattern_new", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 0, "end": 2.5e6}, "main": {"start": 0, "end": 3e4}}}
	plot_twin_cycles(weekly_plotinfo,weekly_axisinfo,"week")

	daily_plotinfo = {"main": {}, "total": {}}
	daily_plotinfo["total"]["x"] = range(24)
	daily_plotinfo["total"]["y"] = tp_es.hourly
	daily_plotinfo["total"]["label"] = "Total Page-views"
	daily_plotinfo["main"]["x"] = range(24)
	daily_plotinfo["main"]["y"] = mp_es.hourly
	daily_plotinfo["main"]["label"] = "Main Page-views"

	daily_axisinfo = {"filename": "es_daily_pattern_new", "ylabel": r'Number of page-views', "ylim": {"total": {"start": 0, "end": 2e6}, "main": {"start": 0, "end": 2.5e4}}}
	plot_twin_cycles(daily_plotinfo,daily_axisinfo,"day")


	old_hourly = list(np.mean(matdata["hourly_total"],axis=0))
	norm_en_old = [old_hourly[x]/sum(old_hourly) for x in range(len(old_hourly))]
	norm_en_new = [tp.hourly[x]/sum(tp.hourly) for x in range(len(tp.hourly))]
	norm_nl = [tp_nl.hourly[x]/sum(tp_nl.hourly) for x in range(len(tp_nl.hourly))]
	norm_de = [tp_de.hourly[x]/sum(tp_de.hourly) for x in range(len(tp_de.hourly))]
	norm_es = [tp_es.hourly[x]/sum(tp_es.hourly) for x in range(len(tp_es.hourly))]
	norm_es_rescaled = norm_es[6:]+norm_es[:6]

	daily_plotinfo = {"en": {}, "en2": {}, "nl": {}, "de": {}, "es": {}, "es2": {}}
	daily_plotinfo["en"]["x"] = range(24)
	daily_plotinfo["en"]["y"] = norm_en_old
	daily_plotinfo["en"]["label"] = "English (old)"
	daily_plotinfo["en"]["line_style"] = "-"
	daily_plotinfo["en2"]["x"] = range(24)
	daily_plotinfo["en2"]["y"] = norm_en_new
	daily_plotinfo["en2"]["label"] = "English (new)"
	daily_plotinfo["en2"]["line_style"] = "-"
	daily_plotinfo["nl"]["x"] = range(24)
	daily_plotinfo["nl"]["y"] = norm_nl
	daily_plotinfo["nl"]["label"] = "Dutch"
	daily_plotinfo["nl"]["line_style"] = "-"
	daily_plotinfo["de"]["x"] = range(24)
	daily_plotinfo["de"]["y"] = norm_de
	daily_plotinfo["de"]["label"] = "German"
	daily_plotinfo["de"]["line_style"] = "-"
	daily_plotinfo["es"]["x"] = range(24)
	daily_plotinfo["es"]["y"] = norm_es
	daily_plotinfo["es"]["label"] = "Spanish"
	daily_plotinfo["es"]["line_style"] = "-"
	daily_plotinfo["es2"]["x"] = range(24)
	daily_plotinfo["es2"]["y"] = norm_es_rescaled
	daily_plotinfo["es2"]["label"] = "Spanish (shifted 6 hours)"
	daily_plotinfo["es2"]["line_style"] = "-"
	daily_axisinfo = {"filename": "norm_compared", "ylabel": r'Number of page-views', "ylim": {"start": 0, "end": 0.08}}
	plot_day(daily_plotinfo,daily_axisinfo)

def example_progression(en,nl,de,es):
	subplotinfo = {}
	axisinfo = {'filename': "cumulative_patterns", "title": ""}

	xticks = ["" for i in range(len(en.average.norm_views)+1)]
	i = 0
	while i < len(en.average.norm_views):
		xticks[i] = str(i%24)+"h"
		i+=12

	plotinfo = {"en": {}}
	plotinfo["en"]["x"] = range(len(en.average.norm_views))
	plotinfo["en"]["y"] = cumsum(en.average.norm_views)
	plotinfo["en"]["line_style"] = '-'
	plotinfo["en"]["line_color"] = 'blue'
	plotinfo["en"]["label"] = "English"

	subplotinfo["en"] = plotinfo["en"]
	axisinfo["en"] = {"ylabel": r'Cumulative number of page-views', "xticks": xticks, "title": "", "xlim": {"start": min(range(len(xticks))), "end": max(range(len(xticks)))}, "ylim": {"start": 0, "end": 1}}

	xticks2 = ["" for i in range(len(nl.average.norm_views)+1)]
	i = 0
	while i < len(nl.average.norm_views):
		xticks2[i] = str(i%24)+"h"
		i+=6

	plotinfo = {"nl": {}}
	plotinfo["nl"]["x"] = range(len(nl.average.norm_views))
	plotinfo["nl"]["y"] = cumsum(nl.average.norm_views)
	plotinfo["nl"]["line_style"] = '-'
	plotinfo["nl"]["line_color"] = 'blue'
	plotinfo["nl"]["label"] = "Dutch"

	subplotinfo["nl"] = plotinfo["nl"]
	axisinfo["nl"] = {"ylabel": r'Cumulative number of page-views', "xticks": xticks2, "title": "", "xlim": {"start": min(range(len(xticks2))), "end": max(range(len(xticks2)))}, "ylim": {"start": 0, "end": 1}}

	plotinfo = {"de": {}}
	plotinfo["de"]["x"] = range(len(de.average.norm_views))
	plotinfo["de"]["y"] = cumsum(de.average.norm_views)
	plotinfo["de"]["line_style"] = '-'
	plotinfo["de"]["line_color"] = 'blue'
	plotinfo["de"]["label"] = "German"

	subplotinfo["de"] = plotinfo["de"]
	axisinfo["de"] = {"ylabel": r'Cumulative number of page-views', "xticks": xticks2, "title": "", "xlim": {"start": min(range(len(xticks2))), "end": max(range(len(xticks2)))}, "ylim": {"start": 0, "end": 1}}

	xticks3 = ["" for i in range(len(es.average.norm_views)+1)]
	i = 0
	while i < len(es.average.norm_views):
		xticks3[i] = str(i%24)+"h"
		i+=24

	plotinfo = {"es": {}}
	plotinfo["es"]["x"] = range(len(es.average.norm_views))
	plotinfo["es"]["y"] = cumsum(es.average.norm_views)
	plotinfo["es"]["line_style"] = '-'
	plotinfo["es"]["line_color"] = 'blue'
	plotinfo["es"]["label"] = "Spanish"

	subplotinfo["es"] = plotinfo["es"]
	axisinfo["es"] = {"ylabel": r'Cumulative number of page-views', "xticks": xticks3, "title": "", "xlim": {"start": min(range(len(xticks3))), "end": max(range(len(xticks3)))}, "ylim": {"start": 0, "end": 1}}
	
	plot_subplots(subplotinfo,axisinfo,2,2)

def prediction_examples(en,nl,de,es):
	langs = [en,nl,de,es]

	for lang in langs:
		xticks = ["" for i in range(len(lang.average.views)+1)]
		i = 0
		while i < len(lang.average.views):
			xticks[i] = str(i%24)+"h"
			if lang.pattern.lang == "es":
				i+=24
			else:
				i+=6

		plotinfo = {"normal": {}, "estimate": {}, "redistributed": {}}
		plotinfo["normal"]["x"] = range(len(lang.average.views))
		plotinfo["normal"]["y"] = lang.average.views
		plotinfo["normal"]["line_style"] = '-'
		plotinfo["normal"]["line_color"] = 'black'
		plotinfo["normal"]["label"] = "Page views"
		plotinfo["estimate"]["x"] = range(len(lang.average.views))
		plotinfo["estimate"]["y"] = lang.average.est_params
		plotinfo["estimate"]["line_style"] = '--'
		plotinfo["estimate"]["line_color"] = 'red'
		plotinfo["redistributed"]["x"] = range(len(lang.average.red_views))
		plotinfo["redistributed"]["y"] = lang.average.red_views
		plotinfo["redistributed"]["line_style"] = '-'
		plotinfo["redistributed"]["line_color"] = 'blue'
		plotinfo["redistributed"]["label"] = "Redistributed page views"
		if lang.pattern.has_gamma:
			plotinfo["estimate"]["label"] = r"Estimated views ($\beta,\gamma$)"
			# plotinfo["gamma"] = {}
			# plotinfo["gamma"]["x"] = range(len(lang.average.views))
			# plotinfo["gamma"]["y"] = lang.average.est_gamma_func
			# plotinfo["gamma"]["line_style"] = '--'
			# plotinfo["gamma"]["line_color"] = 'black'
			# plotinfo["gamma"]["label"] = r"Estimated views ($\beta,\gamma(v_1)$)"
		else:
			plotinfo["estimate"]["label"] = r"Estimated views ($\beta$)"

		axisinfo = {"filename": lang.average.link_title, "ylabel": r'Number of page-views', "xticks": xticks, "title": "Hourly progression of "+lang.average.title, "xlim": {"start": min(range(len(xticks))), "end": max(range(len(xticks)))}, "ylim": get_ylims(plotinfo)}
		plot_pattern(plotinfo,axisinfo)

def redistribution_plots(sim,cycle="total"):
	if cycle == "total":
		cycle_orig = sim.tp.hourly
	elif cycle == "main":
		cycle_orig = sim.mp.hourly
	
	xtick = rescale_time(cycle_orig)
	cycle_red = redistribute(xtick,cycle_orig)

	xtick_back = rescale_to_normal(xtick)
	cycle_back = redistribute(xtick_back,cycle_red)

	ylimDict = {"de": {"total": {"start": 0, "end": 2e6}, "main": {"start": 0.5e4, "end": 7e4}}, 
	"nl": {"total": {"start": 0.5e5, "end": 3.5e5}, "main": {"start": 0, "end": 8.e3}}, 
	"es": {"total": {"start": 0, "end": 2e6}, "main": {"start": 0, "end": 2.5e4}}, 
	"en": {"total": {"start": 8.e6, "end": 12.5e6}, "main": {"start": 4e5, "end": 6.5e5}}}
			
	xticks = ["" for _ in range(24)]
	i = 0
	while i < 24:
		xticks[i] = str(i%24)+"h"
		i+=3

	plotinfo = {"normal": {}, "estimate": {}, "redistributed": {}}
	plotinfo["normal"]["x"] = range(24)
	plotinfo["normal"]["y"] = cycle_orig
	plotinfo["normal"]["line_style"] = '-'
	plotinfo["normal"]["line_color"] = 'black'
	plotinfo["normal"]["label"] = r"original cycle"
	plotinfo["redistributed"]["x"] = range(24)
	plotinfo["redistributed"]["y"] = cycle_red
	plotinfo["redistributed"]["line_style"] = '-'
	plotinfo["redistributed"]["line_color"] = 'blue'
	plotinfo["redistributed"]["label"] = r"redistributed cycle"
	plotinfo["estimate"]["x"] = range(24)
	plotinfo["estimate"]["y"] = cycle_back
	plotinfo["estimate"]["line_style"] = '--'
	plotinfo["estimate"]["line_color"] = 'red'
	plotinfo["estimate"]["label"] = r"cycle after reversing redistribution"

	axisinfo = {"filename": "red_cycle_"+cycle+"_"+sim.pattern.lang, "ylabel": r'Number of page-views', "xticks": xticks, "title": sim.pattern.lang, "xlim": {"start": min(range(len(xticks))), "end": max(range(len(xticks)))}, "ylim": ylimDict[sim.pattern.lang][cycle]}
	plot_pattern(plotinfo,axisinfo)
	
	red = Redistributor()
	red.run(sim.average.views,cycle_orig,sim.pattern)
	red_y = redistribute(red.xtick,sim.average.views)
	y_estimate = red.get_estimate()

	plot_length = len(sim.average.views)
	xticks = ["" for _ in range(plot_length)]
	i = 0
	while i < plot_length:
		xticks[i] = str(i%24)+"h"
		if sim.pattern.lang == "es":
			i+=24
		elif sim.pattern.lang == "en":
			i+=12
		else:
			i+=3

	plotinfo2 = {"normal": {}, "estimate": {}, "redistributed": {}}
	plotinfo2["normal"]["x"] = range(plot_length)
	plotinfo2["normal"]["y"] = sim.average.views
	plotinfo2["normal"]["line_style"] = '-'
	plotinfo2["normal"]["line_color"] = 'black'
	plotinfo2["normal"]["label"] = r"original data"
	plotinfo2["estimate"]["x"] = range(plot_length)
	plotinfo2["estimate"]["y"] = y_estimate
	plotinfo2["estimate"]["line_style"] = '--'
	plotinfo2["estimate"]["line_color"] = 'red'
	plotinfo2["estimate"]["label"] = r"$e^{g(t)}$"
	plotinfo2["redistributed"]["x"] = range(plot_length)
	plotinfo2["redistributed"]["y"] = red_y
	plotinfo2["redistributed"]["line_style"] = '-'
	plotinfo2["redistributed"]["line_color"] = 'blue'
	plotinfo2["redistributed"]["label"] = r"redistributed, optimal c={:.3f}".format(red.c_opt)

	axisinfo2 = {"filename": "redistributed_"+cycle+"_"+sim.pattern.lang, "ylabel": r'Number of page-views', "xticks": xticks, "title": sim.pattern.lang, "xlim": {"start": min(range(len(xticks))), "end": max(range(len(xticks)))}, "ylim": get_ylims(plotinfo2)}
	plot_pattern(plotinfo2,axisinfo2)

	return plotinfo, plotinfo2, axisinfo, axisinfo2

if __name__ == '__main__':
	main()