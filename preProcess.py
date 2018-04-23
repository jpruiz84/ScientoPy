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

parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,  help="Start year to limit the pre process graph")
parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,  help="End year year to limit the pre process graph")

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

# Program start ********************************************************
print("\n\nScientoPy prerprocess")
print("======================\n")

if sys.version_info[0] > 2:
  print("ERROR, you are using Python 3, Python 2.7.XX required")
  print("")
  exit()


# Create output folders if not exist
if not os.path.exists(globalVar.DATA_OUT_FOLDER):
    os.makedirs(globalVar.DATA_OUT_FOLDER)
 
# Init variables
paperDict = []
globalVar.papersScopus = 0
globalVar.papersWoS = 0
globalVar.omitedPapers = 0


# Read files from the dataInFolder
for file in os.listdir(os.path.join(args.dataInFolder, '')):
  if file.endswith(".csv") or file.endswith(".txt"):
    print("Reading file: %s" % (os.path.join(args.dataInFolder, '') + file))
    ifile = open(os.path.join(args.dataInFolder, '') + file, "r")
    paperUtils.openFileToDict(ifile, paperDict)

# Open the file to write the preprocessing log in CSV
logFile = open(os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.PREPROCESS_LOG_FILE), 'w')
fieldnames = ["Info", "Number", "Source"] + globalVar.INCLUDED_TYPES + ["Total"]
logWriter = csv.DictWriter(logFile, fieldnames=fieldnames, dialect=csv.excel_tab)
logWriter.writeheader()

logWriter.writerow({'Info': '***** Original data *****'})
logWriter.writerow({'Info': 'Total papers', 'Number' : str(len(paperDict))})
logWriter.writerow({'Info': 'Omited papers', 'Number' : str(globalVar.omitedPapers)})

print("Total papers: %s" % len(paperDict))
print("Scopus papers: %s" % globalVar.papersScopus)
print("WoS papers: %s" % globalVar.papersWoS)
print("Omited papers: %s" % globalVar.omitedPapers)
paperUtils.sourcesStatics(paperDict, logWriter)

grapPreprocess(plt, paperDict, True)

# Removing duplicates
if args.noRemDupl:
  paperDict = paperUtils.removeDuplicates(paperDict, logWriter)
  logWriter.writerow({'Info': ''})
  logWriter.writerow({'Info': '***** Statics after duplication removal *****'})
  logWriter.writerow({'Info': 'Total papers', 'Number' : str(len(paperDict))})
  paperUtils.sourcesStatics(paperDict, logWriter)

  grapPreprocess(plt, paperDict, False)

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




