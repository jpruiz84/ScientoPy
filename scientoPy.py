# !/usr/bin/python3

# The MIT License (MIT)
# Copyright (c) 2018 - Universidad del Cauca, Juan Ruiz-Rosero
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

import globalVar
import argparse
from ScientoPyClass import ScientoPyClass

parser = argparse.ArgumentParser(description="Analyze the topics inside a criterion")

parser.add_argument("-c","--criterion", choices=globalVar.validCriterion, default= "authorKeywords",
help="Select the criterion to analyze the topics")

parser.add_argument("-g","--graphType", choices=globalVar.validGrapTypes, default= "bar_trends",
help="Select the graph type to plot")

parser.add_argument("-l", "--length", type=int, default=10, help="Length of the top topics to analyze, default 10")

parser.add_argument("-s", "--skipFirst", type=int, default=0,  help="To filter the \
first top elements. Ex: to filter the first 2 elements on the list use -s 2")

parser.add_argument("-t", "--topics", help='Specific topics to analyze according to critera,\n\r'
                                           'group topics with "," and divide the topics with ";" \n\r'
                                           'Ex: authorKeywords -t "internet of things, iot; bluetooth" \n\r'
                                           'asterisk wildcard ex: authorKeywords -t "device*"')

parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,
                    help="Start year to limit the search, default: " + str(globalVar.DEFAULT_START_YEAR))
parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,
                    help="End year year to limit the search, default: " + str(globalVar.DEFAULT_END_YEAR))

parser.add_argument("--savePlot", default="",  help='Save plot to a file. Ex: --savePlot "topKeywords.eps"')

parser.add_argument("--pYear", 
help="To present the results in percentage per year instead of documents per year", action="store_true")

parser.add_argument("--yLog", 
help="Plot Y axes in log scale", action="store_true")

parser.add_argument("--noPlot",
help="Do not plot the results, use for large amount of topics", action="store_true")

parser.add_argument("--agrForGraph",
help="To use average growth rate (AGR) instead average documents per year (ADY) in parametric and parametric 2 graphs",
                    action="store_true")

parser.add_argument("--wordCloudMask", default="",  help='PNG mask image to use for wordCloud')

parser.add_argument("--windowWidth",
help="Window width in years for average growth rate and average documents per year, minimum 1",
                    type=int, default=2)

parser.add_argument("-r", "--previousResults",
help="Analyze based on the previous results", action="store_true")

parser.add_argument("--onlyFirst",
help="Only look in the first elemet of the topic, for example to analyze only the first author name, "
     "country or institution", action="store_true")

parser.add_argument("--graphTitle",
help="To put a title in the output graph", type=str)

parser.add_argument("--plotWidth", type=int, default=globalVar.DEFAULT_PLOT_WIDTH,
                    help="Set the plot width size in inches, default: " + str(globalVar.DEFAULT_PLOT_WIDTH))

parser.add_argument("--plotHeight", type=int, default=globalVar.DEFAULT_PLOT_HEIGHT,
                    help="Set the plot heigth size in inches, default: " + str(globalVar.DEFAULT_PLOT_HEIGHT))

parser.add_argument("--trend",
help="Get and graph the top trending topics, with the highest average growth rate", action="store_true")

parser.add_argument("-f", "--filter", help='Filter to be applied on a sub topic.'
  'Example to extract instituions from United States: scientoPy.py institutionWithCountry -f "United States"')


# Parse arguments
args = parser.parse_args()

# Start scientoPy
scientoPy = ScientoPyClass()
scientoPy.scientoPy(args)
scientoPy.plotResults(args)