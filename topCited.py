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

#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import paperUtils
import paperSave
import globalVar
import os
import math
import matplotlib.pyplot as plt
import numpy
import math


import argparse

parser = argparse.ArgumentParser(description="Get the top cited papers, by adding more value to"
                                             " newer ones by an exponential time scale curve")

parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,  help="Start year to limit the search")
parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,  help="End year year to limit the search")

parser.add_argument("--pYear", 
help="To present the results in percentage per year", action="store_true")

parser.add_argument("-l", "--length", type=int, default=20, help="Number of papers to list, default 20")

parser.add_argument("--yLog", 
help="Plot with Y axes on log scale", action="store_true")

parser.add_argument("--savePlot", default="",  help="Save plot to a file")

parser.add_argument("--yearWeight", type=float, default = 1,
help="Weight to add by year, in order to put more importance to newer papers, \n"
     " yearExpWeight = exp((year - startYear) * yearWeight), default 1")

parser.add_argument("-r", "--previousResults",
help="Analyze based on the previous results", action="store_false")

parser.add_argument("--noPlot",
help="Do not plot the results, use for large amount of topics", action="store_false")

args = parser.parse_args()


# Program start ********************************************************

# Create output folders if not exist
if not os.path.exists(globalVar.GRAPHS_OUT_FOLDER):
    os.makedirs(globalVar.GRAPHS_OUT_FOLDER)
if not os.path.exists(globalVar.RESULTS_FOLDER):
    os.makedirs(globalVar.RESULTS_FOLDER)

# Select the input file
if args.previousResults:
  INPUT_FILE = os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME)
else:
  INPUT_FILE = os.path.join(globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_NAME)

# Start paper list empty
papersDict = []

# Open the storage database and add to papersDict
ifile = open(INPUT_FILE, "rb")
print("Reading file: %s" % (INPUT_FILE))
paperUtils.analyzeFileDict(ifile, papersDict)
ifile.close()

#paperDict = sorted(papersDict, key=lambda x: x["citedBy"])

print("Scopus papers: %s" % globalVar.papersScopus)
print("WoS papers: %s" % globalVar.papersWoS)
print("Omited papers: %s" % globalVar.omitedPapers)
print("Total papers: %s" % len(papersDict))

# Create a yearArray
yearArray = range(args.startYear, args.endYear + 1)
yearCitations = {}
for i in range(args.startYear, args.endYear + 1):
    yearCitations[i] = 0
  

# Find citations per year
# run on papersDict
for paper in papersDict:
  if int(paper["year"]) in yearCitations.keys():
    yearCitations[int(paper["year"])] += int(paper["citedBy"])


# Find the scale per year
yearScale = {}
yearScaled = {}
for key in yearCitations:
  yearScale[key] = math.exp((key - args.startYear) * args.yearWeight)
  yearScaled[key] = yearCitations[key] * yearScale[key]


# Find citations per year
# run on papersDict
papersCitedDict = []
for paper in papersDict:
  if int(paper["year"]) in yearCitations.keys():
    paper["scaledCitedBy"] = int(paper["citedBy"]) * yearScale[int(paper["year"])]
    papersCitedDict.append(paper)


papersCitedDict = sorted(papersCitedDict, key=lambda x: int(x["scaledCitedBy"]), reverse=True)

print("No.\tYear\tCitat\tS_cita\tTitle")
for i in range(0, args.length):
    print("%d.\t%d\t%d\t%d\t%s" %
          (i + 1,
           int(papersCitedDict[i]["year"]),
           int(papersCitedDict[i]["citedBy"]),
           int(papersCitedDict[i]["scaledCitedBy"]),
           papersCitedDict[i]["title"]
           ))



# Plot
if args.noPlot:
  count = 0
  legendArray=[]

  plt.subplot(311)
  plt.plot(*zip(*sorted(yearCitations.items())),
  linewidth=1.2, marker=globalVar.MARKERS[count], markersize=10,
  color=globalVar.COLORS[count],markeredgewidth=0.0)
  plt.xlabel("Year")
  plt.ylabel("Total citations")

  plt.subplot(312)
  plt.plot(*zip(*sorted(yearScaled.items())),
  linewidth=1.2, marker=globalVar.MARKERS[count], markersize=10,
  color=globalVar.COLORS[count],markeredgewidth=0.0)
  plt.xlabel("Year")
  plt.ylabel("Total citations scaled")


  plt.subplot(313)
  plt.plot(*zip(*sorted(yearScale.items())),
  linewidth=1.2, marker=globalVar.MARKERS[count], markersize=10,
  color=globalVar.COLORS[count],markeredgewidth=0.0)
  plt.xlabel("Year")
  plt.ylabel("Scale per year")

  ax = plt.gca()
  ax.get_xaxis().get_major_formatter().set_useOffset(False)

  if args.pYear:
    plt.ylabel("% of documents per year")
    ax.set_ylim(ymin=0, ymax=115)
    
  if args.yLog:
    plt.yscale('log')
    
  plt.tight_layout()
    
  if args.savePlot == "":
    plt.show()
  else:
    plt.savefig(os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot),
    bbox_inches = 'tight', pad_inches = 0.01)

paperSave.saveTopCited(papersCitedDict)



