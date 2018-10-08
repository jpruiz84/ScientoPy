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

import csv
import paperUtils
import paperSave
import globalVar
import os
import argparse
import sys
import matplotlib.pyplot as plt
import graphUtils

# Parse arguments
parser = argparse.ArgumentParser(description="Pre process and remove duplicates documents from Scopus and WoS")

parser.add_argument("dataInFolder", help="Folder where the Scopus or WoS data is located")

parser.add_argument("--noRemDupl",
help="To do not remove the duplicated documents", action="store_false")

parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,
                    help="Start year to limit the pre process graph, and to extract the number of papers in year range")
parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,
                    help="End year year to limit the pre process graph, and to extract the number of papers in year range")

parser.add_argument("--savePlot", default="",  help='Save the pre processed graph to a file, ex: --savePlot "preProcessed.eps"')

args = parser.parse_args()


def grapPreprocess(plt, papersDict, fOriginal):
  topicResults = []

  yearArray = range(args.startYear, args.endYear + 1)

  # Create a dictonary in topicResults per element in topicList
  for topic in ["Scopus", "WoS"]:
    topicItem = {}
    topicItem["upperName"] = topic.upper()
    topicItem["name"] = topic
    topicItem["allTopics"] = topic
    topicItem["year"] = yearArray
    topicItem["PapersCountAccum"] = [0] * len(yearArray)
    topicItem["PapersCount"] = [0] * len(yearArray)
    topicItem["PapersTotal"] = 0
    topicResults.append(topicItem)

  # For each paper
  for paper in papersDict:
    # For each item in paper critera
    for item in paper["dataBase"].split(";"):
      # Strip paper item and upper
      item = item.strip()
      itemUp = item.upper()

      for topicItem in topicResults:
        subTopic = topicItem["allTopics"]
        if subTopic.upper() == itemUp:
          if int(paper["year"]) in yearArray:
            yearIndex = topicItem["year"].index(int(paper["year"]))
            topicItem["PapersCount"][yearIndex] += 1
            topicItem["PapersTotal"] += 1
            topicItem["name"] = item

  # Extract accumulative
  for topicItem in topicResults:
    papersAccumValue = 0
    for i in range(0, len(topicItem["PapersCount"])):
      papersAccumValue += topicItem["PapersCount"][i]
      topicItem["PapersCountAccum"][i] = papersAccumValue

  if(fOriginal == True):
    for topic in topicResults:
      if topic["name"] == "WoS":
        topic["name"] = "WoS original"
      if topic["name"] == "Scopus":
        topic["name"] = "Scopus original"
  else:
    for topic in topicResults:
      if topic["name"] == "WoS":
        topic["name"] = "WoS dup. rem."
      if topic["name"] == "Scopus":
        topic["name"] = "Scopus dup. rem."

  graphUtils.plot_time_line(plt,topicResults, fOriginal)

# *****************  Program start ********************************************************
print("\n\nScientoPy prerprocess")
print("======================\n")

# Check python version
if sys.version_info[0] < 3:
  print("ERROR, you are using Python 2, Python 3.X.X required")
  print("")
  exit()

# Create output folders if not exist
if not os.path.exists(globalVar.DATA_OUT_FOLDER):
  os.makedirs(globalVar.DATA_OUT_FOLDER)
if not os.path.exists(globalVar.GRAPHS_OUT_FOLDER):
  os.makedirs(globalVar.GRAPHS_OUT_FOLDER)
if not os.path.exists(globalVar.RESULTS_FOLDER):
  os.makedirs(globalVar.RESULTS_FOLDER)

# Init variables
paperDict = []
globalVar.loadedPapers = 0
globalVar.totalPapers = 0
globalVar.papersScopus = 0
globalVar.papersWoS = 0
globalVar.omitedPapers = 0

# Read files from the dataInFolder
for file in os.listdir(os.path.join(args.dataInFolder, '')):
  if file.endswith(".csv") or file.endswith(".txt"):
    print("Reading file: %s" % (os.path.join(args.dataInFolder, '') + file))
    ifile = open(os.path.join(args.dataInFolder, '') + file, "r", encoding='utf-8')
    paperUtils.openFileToDict(ifile, paperDict)

# Filter papers with invalid year
paperDict = list(filter(lambda x: x["year"].isdigit(), paperDict))

# Open the file to write the preprocessing log in CSV
logFile = open(os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.PREPROCESS_LOG_FILE), 'w', encoding='utf-8')
fieldnames = ["Info", "Number", "Percentage" ,"Source"] + globalVar.INCLUDED_TYPES + ["Total"]
logWriter = csv.DictWriter(logFile, fieldnames=fieldnames, dialect=csv.excel_tab)
logWriter.writeheader()

globalVar.OriginalTotalPapers = len(paperDict)
logWriter.writerow({'Info': '***** Original data *****'})
logWriter.writerow({'Info': 'Loaded papers', 'Number' : str(globalVar.loadedPapers)})

logWriter.writerow({'Info': 'Omitted papers',
                    'Number': ("%d" % (globalVar.omitedPapers)),
                    'Percentage': ("%.1f%%" % (100.0 * globalVar.omitedPapers / globalVar.loadedPapers))})


logWriter.writerow({'Info': 'Total papers', 'Number' : str(globalVar.OriginalTotalPapers)})
logWriter.writerow({'Info': 'Papers from WoS',
                    'Number': ("%d" % (globalVar.papersWoS)),
                    'Percentage': ("%.1f%%" % (100.0 * globalVar.papersWoS / globalVar.OriginalTotalPapers))})
logWriter.writerow({'Info': 'Papers from Scopus',
                    'Number': ("%d" % (globalVar.papersScopus)),
                    'Percentage': ("%.1f%%" % (100.0 * globalVar.papersScopus / globalVar.OriginalTotalPapers))})




print("Loaded papers: %s" % len(paperDict))
print("Omited papers: %s" % globalVar.omitedPapers)
print("total papers: %s" % globalVar.OriginalTotalPapers)
print("WoS papers: %s" % globalVar.papersWoS)
print("Scopus papers: %s" % globalVar.papersScopus)
paperUtils.sourcesStatics(paperDict, logWriter)

grapPreprocess(plt, paperDict, True)

# Removing duplicates
if args.noRemDupl:
  paperDict = paperUtils.removeDuplicates(paperDict, logWriter)
  logWriter.writerow({'Info': ''})
  logWriter.writerow({'Info': 'After duplication removal'})
  paperUtils.sourcesStatics(paperDict, logWriter)

  grapPreprocess(plt, paperDict, False)

# Filter papers with invalid year
papersDictYear = list(filter(lambda x: x["year"].isdigit(), paperDict))
# Filter the papers outside the year range
papersDictYear = list(filter(lambda x: int(x["year"]) >= args.startYear, papersDictYear))
papersDictYear = list(filter(lambda x: int(x["year"]) <= args.endYear, papersDictYear))

totalPapersInRagne = len(papersDictYear)

print("Total papers in range (%s - %s): %s" %
      (args.startYear, args.endYear , totalPapersInRagne))

if(totalPapersInRagne > 0):
  totalPapersInRagnePercentaje = 100.0 * totalPapersInRagne / totalPapersInRagne
else:
  totalPapersInRagnePercentaje = 100.0

logWriter.writerow({'Info': "Total papers in range (%s - %s)" % (args.startYear, args.endYear),
                    'Number': ("%d" % (totalPapersInRagne)),
                    'Percentage': ("%.1f%%" % totalPapersInRagnePercentaje)})


# Save final results
paperSave.saveResults(paperDict,
os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME))

# Close log file
logFile.close()

# Saving graph
plt.tight_layout()

if args.savePlot == "":
  plt.show()
else:
  plt.savefig(os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot),
              bbox_inches='tight', pad_inches=0.01)
  print("Plot saved on: " + os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot))




