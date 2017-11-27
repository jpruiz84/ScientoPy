import csv
import paperUtils
import paperSave
import globalVar
import os
import argparse


# Parse arguments
parser = argparse.ArgumentParser(description="Pre process and remove duplicates documents from Scopus and WoS")

parser.add_argument("dataInFolder", help="Folder where the Scopus or WoS data is located")

parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,
                    help="Start year to limit the pre processing data")

parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,
                    help="End year year to limit the pre rocessing data")

parser.add_argument("--noRemDupl",
help="To do not remove the duplicated documents", action="store_false")

args = parser.parse_args()


# Program start ********************************************************
 
# Init variables
paperDict = []
globalVar.papersScopus = 0
globalVar.papersWoS = 0
globalVar.omitedPapers = 0


# Read files from the dataInFolder
for file in os.listdir(os.path.join(args.dataInFolder, '')):
  if file.endswith(".csv") or file.endswith(".txt"):
    print("Reading file: %s" % (os.path.join(args.dataInFolder, '') + file))
    ifile = open(os.path.join(args.dataInFolder, '') + file, "rb")
    paperUtils.analyzeFileDict(ifile, paperDict)

# Removed paper out of the including period time
paperOutOfSelectedTime = 0
for paper in paperDict:
  if (int(paper["year"]) < args.startYear) or \
  (int(paper["year"]) > args.endYear):
    paperDict.remove(paper)
    #paperUtils.printPaper(paper)
    paperOutOfSelectedTime += 1



# Open the file to write the preprocessing log in CSV
logFile = open(os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.PREPROCESS_LOG_FILE), 'w')
fieldnames = ["Info", "Number", "Source"] + globalVar.INCLUDED_TYPES + ["Total"]
logWriter = csv.DictWriter(logFile, fieldnames=fieldnames, dialect=csv.excel_tab)
logWriter.writeheader()

logWriter.writerow({'Info': '***** Original data *****'})
logWriter.writerow({'Info': 'Papers out of selected time', 'Number' : str(paperOutOfSelectedTime)})
logWriter.writerow({'Info': 'Total papers', 'Number' : str(len(paperDict))})
logWriter.writerow({'Info': 'Omited papers', 'Number' : str(globalVar.omitedPapers)})

print("Papers out of selected time: " + str(paperOutOfSelectedTime))
print("Total papers: %s" % len(paperDict))
print("Scopus papers: %s" % globalVar.papersScopus)
print("WoS papers: %s" % globalVar.papersWoS)
print("Omited papers: %s" % globalVar.omitedPapers)

paperUtils.sourcesStatics(paperDict, logWriter)

# Removing duplicates
if args.noRemDupl:
  paperDict = paperUtils.removeDuplicates(paperDict, logWriter)

  logWriter.writerow({'Info': ''})
  logWriter.writerow({'Info': '***** Statics after duplication removal *****'})
  logWriter.writerow({'Info': 'Total papers', 'Number' : str(len(paperDict))})
  paperUtils.sourcesStatics(paperDict, logWriter)

# Save final results
paperSave.saveResults(paperDict,
os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME))

# Close log file
logFile.close()

