#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import csv
import paperUtils
import paperSave
import globalVar
import os
import sys
import matplotlib.pyplot as plt
import math
import pprint


import argparse
parser = argparse.ArgumentParser()

parser.add_argument("criteria", choices=["authors", "source", "subject",
"authorKeywords", "indexKeywords", "documentType", "dataBase", "country"], 
help="Search criteria, ex: ")

parser.add_argument("-l", "--length", type=int, default=10, help="Length of the top items listed")

parser.add_argument("-s", "--start", type=int, default=0,  help="To filter the \
first element, ex to filter the first 2 elements on the list use -s 2")

parser.add_argument("--startYear", type=int, default=2000,  help="Start year to limit the search")
parser.add_argument("--endYear", type=int, default=2016,  help="End year year to limit the search")

parser.add_argument("--pYear", 
help="To present the results in percentage per year", action="store_true")

parser.add_argument("--yLog", 
help="Plot with Y axes on log scale", action="store_true")

parser.add_argument("--savePlot", default="",  help="Save plot to a file")

parser.add_argument("-r", "--lastResults",
help="Analyze based on the last results", action="store_false")

parser.add_argument("--noPlot",
help="Do not plot the resutls", action="store_false")

parser.add_argument("--useCitedBy",
help="Analyze top results based on times cited", action="store_true")

args = parser.parse_args()

if args.lastResults:
  INPUT_FILE = globalVar.DATA_OUT_FOLDER + "papersOutput.txt"
else:
  INPUT_FILE = globalVar.RESULTS_FOLDER + "papersOutput.txt"

# Program start ********************************************************
 
# Start paper list empty
papersDict = []

# Open the storaged database and add to papersDict 
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


yearPapers = {}
for i in range(args.startYear, args.endYear + 1):
  yearPapers[i] = 0
  
# Create a topic list
topicList = {}

# Find papers within the arguments
# run on papersDict
for paper in papersDict:
  if int(paper["year"]) in yearPapers.keys():
    yearPapers[int(paper["year"])] += 1 
    
  for item in paper[args.criteria].split("; "):
    if item == "":
      continue
    try:
      # filter not included years
      if int(paper["year"]) not in yearArray:
        continue
      if item.upper() in topicList:
        if not args.useCitedBy:
          topicList[item.upper()] += 1 
        else:
          topicList[item.upper()] += int(paper["citedBy"])
      else:
        if not args.useCitedBy:
          topicList[item.upper()] = 1 
        else:
          topicList[item.upper()] = int(paper["citedBy"])
    except:
      noWithCitedBy = 1

topTopcis = sorted(topicList.iteritems(), 
key=lambda x:-x[1])[int(args.start):int(args.length)]

count = 0
for x in topTopcis:
  count += 1
  print "{0}-> {1}: {2}".format(count,*x)
  
if args.start > 0:
  topTopicsFilterd = sorted(topicList.iteritems(), 
  key=lambda x:-x[1])[0:int(args.start)]
  print("\nTop topics before start:")
  count = 0
  for x in topTopicsFilterd:
    count += 1
    print "{0}-> {1}: {2}".format(count,*x)
    
  

# Create results data dictionary
topResults = {}
for topic in topTopcis:
  topicName = topic[0]
  topResults[topicName] = {}
  topResults[topicName]["year"] = yearArray
  topResults[topicName]["count"] = [0] * len(yearArray)
  topResults[topicName]["total"] = 0
  topResults[topicName]["name"] = 0
  topResults[topicName]["papers"] = []
  topResults[topicName]["hIndex"] = 0


# Find papers within the arguments
# run on papersDict
noIncludedInRange = 0
for paper in papersDict:
  # run on input arguments
  for item in paper[args.criteria].split("; "):
    for topic in topTopcis:
      if topic[0].upper() == item.upper():
        try:
          index = topResults[item.upper()]["year"].index(int(paper["year"]))
          if not args.useCitedBy:
            topResults[item.upper()]["count"][index] += 1
            topResults[item.upper()]["total"] += 1
          else:
            topResults[item.upper()]["count"][index] += int(paper["citedBy"])
            topResults[item.upper()]["total"] += int(paper["citedBy"])
          
          topResults[item.upper()]["name"] = item
          topResults[item.upper()]["papers"].append(paper)
        except:
          noIncludedInRange += 1
          #print("Paper on year: %s" % paper.year)

#print(topResults)

# Percentage per year
if args.pYear:
  for topic in topTopcis:
    for year, value in yearPapers.iteritems():
      index = topResults[topic[0].upper()]["year"].index(year)
      if value != 0:
        topResults[topic[0].upper()]["count"][index] /= (float(value)/100.0)


# h index **********************
for topic in topTopcis:
  topicName = topic[0]
  #print("\n" + topicName)

  # Sort papers by cited by count
  papersIn = topResults[topicName]["papers"]
  papersIn = sorted(papersIn, key=lambda x: int(x["citedBy"]), reverse = True)

  count = 1
  hIndex = 0
  for paper in papersIn:
    #print(str(count) + ". " + paper["citedBy"])
    if int(paper["citedBy"]) >= count:
      hIndex = count
    count += 1

  #print("hIndex: " + str(hIndex))
  topResults[topicName]["hIndex"] = hIndex


# Print top topics
print("\nTop topics:")
print("Pos. " + args.criteria + ", Total, h-index")
count = 0
for topic in topTopcis:
  print("%s. %s: %s, %s" % (count + 1,
  topResults[topic[0].upper()]["name"], topResults[topic[0].upper()]["total"],
                            str(topResults[topic[0].upper()]["hIndex"])))
  count += 1


if args.noPlot:
  count = 0
  legendArray=[]
  for topic in topTopcis:
    plt.plot(topResults[topic[0].upper()]["year"], topResults[topic[0].upper()]["count"], 
    linewidth=1.2, marker=globalVar.MARKERS[count], markersize=10, 
    zorder=(len(topicList) - count), color=globalVar.COLORS[count],markeredgewidth=0.0)
    
    data = topResults[topic[0].upper()]["name"]
    legendArray.append(data[:30] + (data[30:] and '..'))
    count += 1
    
  plt.legend(legendArray, loc = 0, fontsize=13)  
  plt.xlabel("Publication year")
  plt.ylabel("Number of documents")

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
    plt.savefig(globalVar.GRAPHS_OUT_FOLDER + args.savePlot,
    bbox_inches = 'tight', pad_inches = 0.01)

paperSave.saveTopResults(topResults, args.criteria)
paperSave.saveExtendedResults(topResults, args.criteria)

