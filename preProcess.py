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

parser.add_argument("--savePlot", default="",  help='Save the pre processed graph to a file, ex: --savePlot "preProcessed.eps"')

parser.add_argument("--graphTitle",
help="To put a title in the output graph", type=str)


args = parser.parse_args()


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


preProcessBrief = {}
preProcessBrief["totalLoadedPapers"] = 0
preProcessBrief["omittedPapers"] = 0
preProcessBrief["papersAfterRemOmitted"] = 0
preProcessBrief["loadedPapersScopus"] = 0
preProcessBrief["loadedPapersWoS"] = 0

# After duplication removal filter
preProcessBrief["totalAfterRemDupl"] = 0
preProcessBrief["removedTotalPapers"] = 0
preProcessBrief["removedPapersScopus"] = 0
preProcessBrief["removedPapersWoS"] = 0
preProcessBrief["papersScopus"] = 0
preProcessBrief["papersWoS"] = 0





# Read files from the dataInFolder
for file in os.listdir(os.path.join(args.dataInFolder, '')):
  if file.endswith(".csv") or file.endswith(".txt"):
    print("Reading file: %s" % (os.path.join(args.dataInFolder, '') + file))
    ifile = open(os.path.join(args.dataInFolder, '') + file, "r", encoding='utf-8')
    paperUtils.openFileToDict(ifile, paperDict)

# Filter papers with invalid year
paperDict = list(filter(lambda x: x["year"].isdigit(), paperDict))


if(globalVar.loadedPapers == 0):
  print("ERROR: 0 documents found from " + os.path.join(args.dataInFolder, ''))
  print("")
  exit()

globalVar.OriginalTotalPapers = len(paperDict)

preProcessBrief["totalLoadedPapers"] = globalVar.loadedPapers
preProcessBrief["omittedPapers"] = globalVar.omitedPapers
preProcessBrief["papersAfterRemOmitted"] = globalVar.OriginalTotalPapers

preProcessBrief["loadedPapersScopus"] = globalVar.papersScopus
preProcessBrief["loadedPapersWoS"] = globalVar.papersWoS






# Open the file to write the preprocessing log in CSV
logFile = open(os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.PREPROCESS_LOG_FILE), 'w', encoding='utf-8')
fieldnames = ["Info", "Number", "Percentage" ,"Source"] + globalVar.INCLUDED_TYPES + ["Total"]
logWriter = csv.DictWriter(logFile, fieldnames=fieldnames, dialect=csv.excel_tab)
logWriter.writeheader()


logWriter.writerow({'Info': '***** Original data *****'})
logWriter.writerow({'Info': 'Total loaded papers', 'Number' : str(globalVar.loadedPapers)})

logWriter.writerow({'Info': 'Omitted papers by document type',
                    'Number': ("%d" % (globalVar.omitedPapers)),
                    'Percentage': ("%.1f%%" % (100.0 * globalVar.omitedPapers / globalVar.loadedPapers))})


logWriter.writerow({'Info': 'Total papers after omitted papers removed', 'Number' : str(globalVar.OriginalTotalPapers)})
logWriter.writerow({'Info': 'Loaded papers from WoS',
                    'Number': ("%d" % (globalVar.papersWoS)),
                    'Percentage': ("%.1f%%" % (100.0 * globalVar.papersWoS / globalVar.OriginalTotalPapers))})
logWriter.writerow({'Info': 'Loaded papers from Scopus',
                    'Number': ("%d" % (globalVar.papersScopus)),
                    'Percentage': ("%.1f%%" % (100.0 * globalVar.papersScopus / globalVar.OriginalTotalPapers))})


print("Loaded papers: %s" % len(paperDict))
print("Omited papers: %s" % globalVar.omitedPapers)
print("total papers: %s" % globalVar.OriginalTotalPapers)
print("WoS papers: %s" % globalVar.papersWoS)
print("Scopus papers: %s" % globalVar.papersScopus)
paperUtils.sourcesStatics(paperDict, logWriter)


# Removing duplicates
if args.noRemDupl:
  paperDict = paperUtils.removeDuplicates(paperDict, logWriter, preProcessBrief)
  logWriter.writerow({'Info': ''})
  logWriter.writerow({'Info': 'Output papers after duplication removal filter'})
  paperUtils.sourcesStatics(paperDict, logWriter)

# if not remove duplicates
else:
    preProcessBrief["totalAfterRemDupl"] = preProcessBrief["papersAfterRemOmitted"]
    preProcessBrief["removedPapersScopus"] = 0
    preProcessBrief["removedPapersWoS"] = 0
    preProcessBrief["papersScopus"] = preProcessBrief["loadedPapersScopus"]
    preProcessBrief["papersWoS"] = preProcessBrief["loadedPapersWoS"]

# Filter papers with invalid year
papersDictYear = list(filter(lambda x: x["year"].isdigit(), paperDict))


logWriter.writerow({'Info': 'Papers from WoS',
                    'Number': ("%d" % (preProcessBrief["papersWoS"] ))})
logWriter.writerow({'Info': 'Papers from Scopus',
                    'Number': ("%d" % (preProcessBrief["papersScopus"] ))})

# Save final results
paperSave.saveResults(paperDict,
os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME))

# Close log file
logFile.close()


graphUtils.grapPreprocess(plt, preProcessBrief)

if args.graphTitle:
  plt.title(args.graphTitle)

# Saving graph
plt.tight_layout()

if args.savePlot == "":
  plt.show()
else:
  plt.savefig(os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot),
              bbox_inches='tight', pad_inches=0.01)
  print("Plot saved on: " + os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot))




