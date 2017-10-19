import csv
import paperUtils
import paperSave
import globalVar
import os
import argparse
parser = argparse.ArgumentParser()


parser.add_argument("--startYear", type=int, default=2000,  help="Start year to limit the search")
parser.add_argument("--endYear", type=int, default=2016,  help="End year year to limit the search")

args = parser.parse_args()



#DATAIN_FOLDER = "./dataInTest/"
#DATAIN_FOLDER = "./dataInVal/"
DATAIN_FOLDER = "./dataIn/"
#DATAIN_FOLDER = "./dataInA/"




# Program start ********************************************************
 
print("\n\r\n\r")
print("************************************************************")
print("************************************************************")
print("\n\r")

paperDict = []

globalVar.papersScopus = 0
globalVar.papersWoS = 0
globalVar.omitedPapers = 0


# Read files in the DATAIN_FOLDER
for file in os.listdir(DATAIN_FOLDER):
  if file.endswith(".csv") or file.endswith(".txt"):
    print("Reading file: %s" % (DATAIN_FOLDER + file))
    ifile = open(DATAIN_FOLDER + file, "rb")
    paperUtils.analyzeFileDict(ifile, paperDict)

# Removed paper out of the including period time
countOutTimeRemoved = 0
for paper in paperDict:
  if (int(paper["year"]) < args.startYear) or \
  (int(paper["year"]) > args.endYear):
    paperDict.remove(paper)
    #paperUtils.printPaper(paper)
    countOutTimeRemoved += 1

print("countOutTimeRemoved: " + str(countOutTimeRemoved))


globalVar.logFile = open(
globalVar.DATA_OUT_FOLDER + globalVar.PREPROCESS_LOG_FILE, 'w')


print("Scopus papers: %s" % globalVar.papersScopus)
print("WoS papers: %s" % globalVar.papersWoS)
print("Omited papers: %s" % globalVar.omitedPapers)
print("Total papers: %s" % len(paperDict))


globalVar.logFile.write("Scopus papers: %s\n" % globalVar.papersScopus)
globalVar.logFile.write("WoS papers: %s\n" % globalVar.papersWoS)
globalVar.logFile.write("Omited papers: %s\n" % globalVar.omitedPapers)
globalVar.logFile.write("Total papers: %s\n" % len(paperDict))


print("\nSources statics before removing duplications:")
globalVar.logFile.write("\nSources statics beffore removing duplications:")
paperUtils.sourcesStatics(paperDict)

# Removing duplicates
paperDict = paperUtils.removeDuplicates(paperDict)


    


print("\nSources statistics after removing duplications:")
globalVar.logFile.write("\nSources statics beffore removing duplications:")
paperUtils.sourcesStatics(paperDict)

paperSave.saveResults(paperDict, 
globalVar.DATA_OUT_FOLDER + globalVar.OUTPUT_FILE_NAME)

globalVar.logFile.close()

