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
parser = argparse.ArgumentParser(description="Analyze the topics inside a criterion")

parser.add_argument("criterion", choices=["authors", "source",  "subject",
"authorKeywords", "indexKeywords", "documentType", "dataBase", "country"], 
help="Select the criterion to analyze the topics")

parser.add_argument("-t", "--topics", help='Topics to analyze according to critera, '
                                           'ex: authorKeywords -t "internet of things,iot;bluetooth" ')

parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,  help="Start year to limit the search")
parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,  help="End year year to limit the search")

parser.add_argument("--savePlot", default="",  help='Save plot to a file, ex: --savePlot "topKeywords.eps"')

parser.add_argument("--pYear", 
help="To present the results in percentage per year", action="store_true")

parser.add_argument("--yLog", 
help="Plot with Y axes on log scale", action="store_true")

parser.add_argument("--noPlot",
help="Do not plot the results, use for large amount of topics", action="store_false")

# Program start ********************************************************

args = parser.parse_args()

# Divide the topics by ;
topicsFirst = args.topics.split(";")

topicList = []
for x in topicsFirst:
  topicList.append(x.split(","))
  
# Remove input start and end spaces 
for item1 in topicList:
  for item2 in item1:
    item2 = item2.strip()

INPUT_FILE = os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME)


# Start paper list empty
papersDict = []
papersDictOut = []

# Open the storage database and add to papersDict
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
  
# Find the number of total papers per year
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
  topicResults[topics[0].upper()]["hIndex"] = []
  
#print(topicResults)

# Find papers within the arguments
# run on papersDict
noIncludedInRange = 0
for paper in papersDict:
  # run on input arguments
  for item in paper[args.criterion].upper().split("; "):
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


# h index **********************
for topic in topicList:
  topicName = topic[0].upper()
  #print("\n" + topicName)

  # Sort papers by cited by count
  papersIn = topicResults[topicName]["papers"]
  papersIn = sorted(papersIn, key=lambda x: int(x["citedBy"]), reverse = True)

  count = 1
  hIndex = 0
  for paper in papersIn:
    #print(str(count) + ". " + paper["citedBy"])
    if int(paper["citedBy"]) >= count:
      hIndex = count
    count += 1

  #print("hIndex: " + str(hIndex))
    topicResults[topicName]["hIndex"] = hIndex

print("\nTop list:")
count = 0
for topics in topicList:
  print("%s. %s: %s" % (count + 1, 
  str(topics).translate(None, "'[]'"), topicResults[topics[0].upper()]["total"]))
  count += 1

# Plot
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
  plt.savefig(os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot),
  bbox_inches = 'tight', pad_inches = 0.01)
  
paperSave.saveTopResults(topicResults, args.criterion)
paperSave.saveResults(papersDictOut, os.path.join(globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_NAME))
paperSave.saveExtendedResults(topicResults, args.criterion)


