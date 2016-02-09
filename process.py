#!/usr/bin/python
from datetime import datetime
import argparse

from retrieve import Retriever
from simulator import Simulator
from pattern import PromotionPattern

parser = argparse.ArgumentParser(description="Process pageview data from Wikimedia dumps.")
parser.add_argument("-d", "--download", action="store_true", help="Specify if data needs to be downloaded")
parser.add_argument("-i", "--interval", type=str, help="Specify the start and end date (format: yyyy-mm-dd)", required=True, nargs=2)
parser.add_argument("-s", "--simulate", action="store_true", help="Run the predictions of the page-views for the indicated languages")
parser.add_argument("-y", "--years", type=str, nargs="*", help="Specify the year cycles that should be used (format: yyyy)", default=[])
parser.add_argument("-m", "--months", type=str, nargs="*", help="Specify the monthly cycles that should be used (format: yyyy-mm)", default=[])
parser.add_argument("-c", "--correction", type=str, nargs="*", help="Specify the values for c that should be used in the time correction", default=[])
parser.add_argument("-l", "--languages", type=str, nargs="*", help="Specify the languages that should be processed", default=["en"])
parser.add_argument("-p", "--plotall", action="store_true", help="Make plots of all articles")
parser.add_argument("-a", "--overall", action="store_true", help="Estimate a single value for parameters and use those estimates on all articles")

args = parser.parse_args()
start = datetime.strptime(args.interval[0],"%Y-%m-%d")
end = datetime.strptime(args.interval[1],"%Y-%m-%d")

regpatterns = {
"en": {"featured": '<dt><b>([\w\s]*?)</b></dt>\n</dl>\n[<div ]*[!:;,"#-=_.()%<>/\w\s\n]*[</div>\n]*<p>[\w\s"]*[<\w>]*[\w\s"]*<b>[<=:">\w\s]*<a href="/wiki/([!:,-_.()%/\w\s]*)" title="(.*?)">.*?</a>[</span>]*</b>',"history": '<b>[<=:\">\w\s]*<a href="/wiki/([!:,-.()%/\w\s]*)" title="(.*?)[" class="mw\-redirect]*">.*?</a>[</span>]*</b>'}, 
"nl": {"featured": '<td valign="top"[ width="50%"]*>\n<center><big><a href="/wiki/Sjabloon:Uitgelicht_[\w\s_]*" title="Sjabloon:Uitgelicht [\w\s]*?">([\w\s]*?)</a></big></center>\n[<p><span ]*.*?[</span></p>\n]*<p>[<i>]*<a href="/wiki/([!:,-.()%/\w\s]*)" title="(.*?)[" class="mw\-redirect]*">.*?</span></a>[</i>]*</p>'}, 
"de": {"featured": '<li>([0-9]*?.[0-9]*?.[0-9]*?) <a href="/wiki/([!:,-.()%/\w\s]*)" title="(.*?)[" class="mw\-redirect]*">.*?</a>[ (erneut)]*</li>'}, 
"es": {"featured": '<td><a href="/wiki/([!:,-.()%/\w\s]*)" title="(.*?)">.*?</a>.*?</td>\n<td>.*?</td>\n<td>([\w\s]*?) - [\w\s]*?</td>'}
}

patterns = {
"en": PromotionPattern("Today's Featured Article",1,[0,-1,-2,-3],"en","Main_Page",regpatterns["en"]["featured"],has_gamma=True,archLink="http://en.wikipedia.org/wiki/Wikipedia:Today%27s_featured_article/{}",archLink_fmt="%B_%Y",archTime_fmt="%d %B"), 
"nl": PromotionPattern("Uitgelicht",1,[0],"nl","Hoofdpagina",regpatterns["nl"]["featured"],has_gamma=False,archLink="http://nl.wikipedia.org/wiki/Wikipedia:Uitgelicht/{}",archLink_fmt="%B",archTime_fmt="%d %B"), 
"de": PromotionPattern("Artikel des Tages",1,[0],"de","Wikipedia_Hauptseite",regpatterns["de"]["featured"],has_gamma=False,archLink="http://de.wikipedia.org/wiki/Wikipedia:Hauptseite/Artikel_des_Tages/Chronologie_{}",archLink_fmt="%Y",archTime_fmt="%d.%m.%Y"), 
"es": PromotionPattern("Articulo destacado",4,range(-15,1),"es","Wikipedia_Portada",regpatterns["es"]["featured"],has_gamma=False,archLink="https://es.wikipedia.org/wiki/Wikipedia:Candidatos_a_art%C3%ADculos_destacados/Destacados_{}",archLink_fmt="%Y",archTime_fmt="%d de %B")
}

promPatterns = []
for lang in args.languages:
	promPatterns.append(patterns[lang])

if args.download:
	rt = Retriever(start,end,patterns=promPatterns)
	rt.getArticles()
	rt.run()

if args.simulate:
	cycles = []
	if args.years != []:
		for year in args.years:
			cycles.append(int(year))
	if args.months != []:
		for month in args.months:
			month_str = datetime.strftime(datetime.strptime(month,"%Y-%m"),"%B_%Y")
			cycles.append(month_str)

	c_values = []
	if args.correction != []:
		for value in args.correction:
			c_values.append(float(value))


	for promPattern in promPatterns:
		sim = Simulator(start,end,promPattern,args.overall,args.plotall)
		sim.load_data()
		sim.run(c_values=c_values,cycles=cycles)
		if args.plotall:
			sim.plot_data()

# process.py -i 2013-01-01 2015-07-01 -s -y 2014 -l en
# process.py -i 2015-01-01 2015-12-01 -s -l nl de es
# process.py -i 2015-01-01 2015-12-01 -d -l nl de es