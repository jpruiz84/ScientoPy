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


class PreProcessClass:

    def __init__(self, from_gui=False):
        self.dataInFolder = ''
        self.noRemDupl = False
        self.savePlot = ''
        self.graphTitle = ''

        self.fromGui = from_gui
        self.preProcessBrief = {}

    def preprocess(self, args=''):

        if args == '':
            args = self

        # *****************  Program start ********************************************************
        print("\n\nScientoPy prerprocess")
        print("======================\n")

        globalVar.progressPer = 0
        globalVar.progressText = 'Reading input files'

        # Check python version
        if sys.version_info[0] < 3:
            print("ERROR, you are using Python 2, Python 3.X.X required")
            print("")
            globalVar.progressPer = 101
            return 0

        # Create output folders if not exist
        if not os.path.exists(os.path.join(globalVar.DATA_OUT_FOLDER)):
            os.makedirs(os.path.join(globalVar.DATA_OUT_FOLDER))
        if not os.path.exists(os.path.join(globalVar.GRAPHS_OUT_FOLDER)):
            os.makedirs(os.path.join(globalVar.GRAPHS_OUT_FOLDER))
        if not os.path.exists(os.path.join(globalVar.RESULTS_FOLDER)):
            os.makedirs(os.path.join(globalVar.RESULTS_FOLDER))

        # Init variables
        paperDict = []
        globalVar.loadedPapers = 0
        globalVar.totalPapers = 0
        globalVar.papersScopus = 0
        globalVar.papersWoS = 0
        globalVar.omitedPapers = 0

        
        self.preProcessBrief["totalLoadedPapers"] = 0
        self.preProcessBrief["omittedPapers"] = 0
        self.preProcessBrief["papersAfterRemOmitted"] = 0
        self.preProcessBrief["loadedPapersScopus"] = 0
        self.preProcessBrief["loadedPapersWoS"] = 0

        # After duplication removal filter
        self.preProcessBrief["totalAfterRemDupl"] = 0
        self.preProcessBrief["removedTotalPapers"] = 0
        self.preProcessBrief["removedPapersScopus"] = 0
        self.preProcessBrief["removedPapersWoS"] = 0
        self.preProcessBrief["papersScopus"] = 0
        self.preProcessBrief["papersWoS"] = 0
        self.preProcessBrief["percenRemPapersScopus"] = 0
        self.preProcessBrief["percenRemPapersWos"] = 0

        files_to_read = len(os.listdir(os.path.join(args.dataInFolder, '')))
        print("Files to read: %d" % files_to_read)

        files_counter = 0
        # Read files from the dataInFolder
        for file in os.listdir(os.path.join(args.dataInFolder, '')):
            files_counter += 1
            globalVar.progressPer = int(float(files_counter) / float(files_to_read) * 100)
            if file.endswith(".csv") or file.endswith(".txt"):
                print("Reading file: %s" % (os.path.join(args.dataInFolder, '') + file))
                ifile = open(os.path.join(args.dataInFolder, '') + file, "r", encoding='utf-8')
                paperUtils.openFileToDict(ifile, paperDict)

        # If not documents found
        if (globalVar.loadedPapers == 0):
            print("ERROR: 0 documents found from " + os.path.join(args.dataInFolder, ''))
            print("")
            globalVar.progressPer = 101
            return

        globalVar.OriginalTotalPapers = len(paperDict)

        self.preProcessBrief["totalLoadedPapers"] = globalVar.loadedPapers
        self.preProcessBrief["omittedPapers"] = globalVar.omitedPapers
        self.preProcessBrief["papersAfterRemOmitted"] = globalVar.OriginalTotalPapers

        self.preProcessBrief["loadedPapersScopus"] = globalVar.papersScopus
        self.preProcessBrief["loadedPapersWoS"] = globalVar.papersWoS

        # Open the file to write the preprocessing log in CSV
        logFile = open(os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.PREPROCESS_LOG_FILE),
                       'w', encoding='utf-8')
        fieldnames = ["Info", "Number", "Percentage", "Source"] + globalVar.INCLUDED_TYPES + ["Total"]
        logWriter = csv.DictWriter(logFile, fieldnames=fieldnames, dialect=csv.excel, lineterminator='\n')
        logWriter.writeheader()

        logWriter.writerow({'Info': '***** Original data *****'})
        logWriter.writerow({'Info': 'Loaded papers', 'Number': str(globalVar.loadedPapers)})

        logWriter.writerow({'Info': 'Omitted papers by document type',
                            'Number': ("%d" % (globalVar.omitedPapers)),
                            'Percentage': ("%.1f%%" % (100.0 * globalVar.omitedPapers / globalVar.loadedPapers))})

        logWriter.writerow(
            {'Info': 'Total papers after omitted papers removed', 'Number': str(globalVar.OriginalTotalPapers)})
        logWriter.writerow({'Info': 'Loaded papers from WoS',
                            'Number': ("%d" % (globalVar.papersWoS)),
                            'Percentage': ("%.1f%%" % (100.0 * globalVar.papersWoS / globalVar.OriginalTotalPapers))})
        logWriter.writerow({'Info': 'Loaded papers from Scopus',
                            'Number': ("%d" % (globalVar.papersScopus)),
                            'Percentage': (
                                        "%.1f%%" % (100.0 * globalVar.papersScopus / globalVar.OriginalTotalPapers))})

        print("Loaded papers: %s" % len(paperDict))
        print("Omitted papers: %s" % globalVar.omitedPapers)
        print("total papers: %s" % globalVar.OriginalTotalPapers)
        print("WoS papers: %s" % globalVar.papersWoS)
        print("Scopus papers: %s" % globalVar.papersScopus)
        paperUtils.sourcesStatics(paperDict, logWriter)

        # Removing duplicates
        if not args.noRemDupl:
            paperDict = paperUtils.removeDuplicates(paperDict, logWriter, self.preProcessBrief)

        # if not remove duplicates
        else:
            self.preProcessBrief["totalAfterRemDupl"] = self.preProcessBrief["papersAfterRemOmitted"]
            self.preProcessBrief["removedPapersScopus"] = 0
            self.preProcessBrief["removedPapersWoS"] = 0
            self.preProcessBrief["papersScopus"] = self.preProcessBrief["loadedPapersScopus"]
            self.preProcessBrief["papersWoS"] = self.preProcessBrief["loadedPapersWoS"]

        # Filter papers with invalid year
        papersDictYear = list(filter(lambda x: x["year"].isdigit(), paperDict))

        # To avoid by zero division
        if self.preProcessBrief["totalAfterRemDupl"] > 0:
            percentagePapersWos = 100.0 * self.preProcessBrief["papersWoS"] / self.preProcessBrief["totalAfterRemDupl"]
            percentagePapersScopus = 100.0 * self.preProcessBrief["papersScopus"] / self.preProcessBrief["totalAfterRemDupl"]
        else:
            percentagePapersWos = 0
            percentagePapersScopus = 0

        logWriter.writerow({'Info': 'Papers from WoS',
                            'Number': ("%d" % (self.preProcessBrief["papersWoS"])),
                            'Percentage': ("%.1f%%" % (percentagePapersWos))})
        logWriter.writerow({'Info': 'Papers from Scopus',
                            'Number': ("%d" % (self.preProcessBrief["papersScopus"])),
                            'Percentage': ("%.1f%%" % (percentagePapersScopus))})

        # Statics after removing duplicates
        if not args.noRemDupl:
            logWriter.writerow({'Info': ''})
            logWriter.writerow({'Info': 'Statics after duplication removal filter'})
            paperUtils.sourcesStatics(paperDict, logWriter)

        # Save final results
        paperSave.saveResults(paperDict,
                              os.path.join(globalVar.DATA_OUT_FOLDER,
                                           globalVar.OUTPUT_FILE_NAME))

        # Close log file
        logFile.close()

        print("\nPreprocess finished.")

        globalVar.totalPapers = len(paperDict)
        globalVar.progressPer = 101


    def graphBrief(self, args=''):

        if args == '':
            args = self

        graphUtils.grapPreprocess(plt, self.preProcessBrief)

        if args.graphTitle:
            plt.title(args.graphTitle)

        # Saving graph
        plt.tight_layout()

        if args.savePlot == "":
            if self.fromGui:
                plt.show(block=False)
            else:
                plt.show(block=True)
        else:
            plt.savefig(os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot),
                        bbox_inches='tight', pad_inches=0.01)
            print("Plot saved on: " + os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot))

        if args.savePlot == "":
            if self.fromGui:
                plt.show()