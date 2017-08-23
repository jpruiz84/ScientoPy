import csv
import paperUtils
import paperSave
import globalVar
import os
import sys
import matplotlib.pyplot as plt
import math
import re


import argparse
parser = argparse.ArgumentParser()

parser.add_argument("criteria", choices=["authors", "source",  "subject",
"authorKeywords", "indexKeywords", "documentType", "dataBase", "country"], 
help="Search criteria, ex: ")

parser.add_argument("-t", "--topics", help='Topics to analize according to critera, ex: -t "internet of things,iot;bluetooth" ')


parser.add_argument("--startYear", type=int, default=2000,  help="Start year to limit the search")
parser.add_argument("--endYear", type=int, default=2016,  help="End year year to limit the search")

parser.add_argument("--savePlot", default="",  help="Save plot to a file")

parser.add_argument("--pYear", 
help="To present the results in percentage per year", action="store_true")

parser.add_argument("--yLog", 
help="Plot with Y axes on log scale", action="store_true")

parser.add_argument("--noPlot",
help="Analyze based on the last results", action="store_false")



args = parser.parse_args()
topicsFirst = args.topics.split(";")

topicList = []
for x in topicsFirst:
  topicList.append(x.split(","))
  
# Remove input start and end spaces 
for item1 in topicList:
  for item2 in item1:
    item2 = item2.strip()

INPUT_FILE = globalVar.DATA_OUT_FOLDER + "papersOutput.txt"

# Program start ********************************************************
 
 # Start paper list empty
papersDict = []
papersDictOut = []

# Open the storaged database and add to papersDict 
ifile = open(INPUT_FILE, "rb")
print("Reading file: %s" % (INPUT_FILE))
paperUtils.analyzeFileDict(ifile, papersDict)
ifile.close()

print("Scopus papers: %s" % globalVar.papersScopus)
print("WoS papers: %s" % globalVar.papersWoS)
print("Omited papers: %s" % globalVar.omitedPapers)
print("Total papers: %s" % len(papersDict))


# Create a yearArray
yearArray = range(args.startYear, args.endYear + 1)


yearPapers = {}
for i in range(args.startYear, args.endYear + 1):
  yearPapers[i] = 0
  
for paper in papersDict:
  if int(paper["year"]) in yearPapers.keys():
    yearPapers[int(paper["year"])] += 1 
    
# Create results data dictionary
topicResults = {}

for topics in topicList:
  topicResults[topics[0].upper()] = {}
  topicResults[topics[0].upper()]["year"] = yearArray
  topicResults[topics[0].upper()]["count"] = [0] * len(yearArray)
  topicResults[topics[0].upper()]["total"] = 0
  topicResults[topics[0].upper()]["name"] = topics[0]
  topicResults[topics[0].upper()]["papers"] = []
  
#print(topicResults)

# Find papers within the arguments
# run on papersDict
noIncludedInRange = 0
for paper in papersDict:
  # run on input arguments
  for item in paper[args.criteria].upper().split("; "):
    for topics in topicList:
      for topic in topics:
        if topic.upper() == item.upper(): 
          try:
            index = topicResults[topics[0].upper()]["year"].index(int(paper["year"]))
            topicResults[topics[0].upper()]["count"][index] += 1
            topicResults[topics[0].upper()]["total"] += 1
            topicResults[topics[0].upper()]["name"] = item
            topicResults[topics[0].upper()]["papers"].append(paper)
            papersDictOut.append(paper)
          except:
            noIncludedInRange += 1
            #print("Paper on year: %s" % paper.year)

#print(topicResults)


if args.pYear:
  for topics in topicList:
    for year, value in yearPapers.iteritems():
      index = topicResults[topics[0].upper()]["year"].index(year)
      if value != 0:
        topicResults[topics[0].upper()]["count"][index] /= (float(value)/100.0)


print("\nTop list:")
count = 0
for topics in topicList:
  print("%s. %s: %s" % (count + 1, 
  str(topics).translate(None, "'[]'"), topicResults[topics[0].upper()]["total"]))
  count += 1


if args.noPlot:
  count = 0
  legendArray=[]
  for topics in topicList:
    legendArray.append(topics[0])
      
    plt.plot(topicResults[topics[0].upper()]["year"], topicResults[topics[0].upper()]["count"], 
    linewidth=1.2, marker=globalVar.MARKERS[count], markersize=10, 
    zorder=(len(topicList) - count), color=globalVar.COLORS[count],markeredgewidth=0.0)
    
    count += 1
    
  plt.legend(legendArray, loc = 2)  
  plt.xlabel("Publication year")
  plt.ylabel("Number of documents")

if args.yLog:
  plt.yscale('log')

if args.pYear:
  plt.ylabel("% of documents per year")

plt.tight_layout()

if args.savePlot == "":
  plt.show()
else:
  plt.savefig(globalVar.GRAPHS_OUT_FOLDER + args.savePlot)
  
paperSave.saveTopResults(topicResults, args.criteria)
paperSave.saveResults(papersDictOut, 
globalVar.RESULTS_FOLDER + globalVar.OUTPUT_FILE_NAME)

paperSave.saveExtendedResults(topicResults, args.criteria)


