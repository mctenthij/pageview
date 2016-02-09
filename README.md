# Wikipedia page view scraper

pageview is a library for extracting and processing page view data from the wikimedia dumps[1].

The current version includes a downloader and an analyser for page-view information, based on [2].

### Language
Python 2.7

### Dependencies
For downloading page view data: dateutils, dateparser, pycountry
For analysis of page view data: numpy, scipy, matplotlib, pycountry

### Author
Marijn ten Thij

### References
[1] dumps.wikimedia.org/other/pagecounts-raw/
[2] Modelling page-view dynamics on Wikipedia, ten Thij et al. (ECCS 2013), http://arxiv.org/abs/1212.5943