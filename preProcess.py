import csv
import paperUtils
import paperSave
import globalVar
import os


DATAIN_FOLDER = "./dataInTest/"
#DATAIN_FOLDER = "./dataInVal/"
#DATAIN_FOLDER = "./dataIn/"
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

paperDict = sorted(paperDict, key=lambda x: x["authors"])
paperDict = sorted(paperDict, key=lambda x: x["year"])
paperDict = sorted(paperDict, key=lambda x: x["dataBase"], reverse=True)

# Removing duplicates
paperDict = paperUtils.removeDuplicates(paperDict)


print("\nSources statistics after removing duplications:")
globalVar.logFile.write("\nSources statics beffore removing duplications:")
paperUtils.sourcesStatics(paperDict)

paperSave.saveResults(paperDict, 
globalVar.DATA_OUT_FOLDER + globalVar.OUTPUT_FILE_NAME)

globalVar.logFile.close()

