# The MIT License (MIT)
# Copyright (c) 2026 - Universidad del Cauca, Juan Ruiz-Rosero
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
import paperIO
import paperSave
import globalVar
import os
import argparse
import sys
import time
import matplotlib.pyplot as plt
import graphUtils


# Number of user-visible pipeline stages. Bumped if a new step is added.
_PIPELINE_STEPS = 4


def _announce_step(n, label, from_gui=False):
    """Print a [n/M] step header to the CLI and update globalVar so the GUI
    progress dialog shows the same text. Resets progressPer to 0 so each
    stage starts from a fresh bar.
    """
    text = "[%d/%d] %s" % (n, _PIPELINE_STEPS, label)
    bar = "-" * max(30, len(text))
    print("\n%s\n%s" % (text, bar))
    globalVar.progressText = text
    globalVar.progressPer = 0
    if from_gui:
        # Tiny yield so the GUI's 100 ms progress poll sees the new text
        # before the stage's heavy work starts.
        time.sleep(0.01)


class PreProcessClass:
    def __init__(self, from_gui=False):
        self.dataInFolder = ""
        self.noRemDupl = False
        self.savePlot = ""
        self.graphTitle = ""

        self.fromGui = from_gui
        self.preProcessBrief = {}

    def preprocess(self, args=""):
        globalVar.cancelProcess = False
        globalVar.progressPer = 0

        if args == "":
            args = self

        # *****************  Program start ********************************************************
        print("\n\nScientoPy prerprocess")
        print("======================\n")

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
        globalVar.omittedPapers = 0

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

        pipeline_t0 = time.time()

        # ── Step 1/4 ── Parallel CSV/TXT read + per-row normalization.
        _announce_step(1, "Loading papers", self.fromGui)
        step_t0 = time.time()
        paperIO.load_folder(args.dataInFolder, paperDict)
        step1_elapsed = time.time() - step_t0
        print(
            "  OK Loaded %d papers from %d files in %.1fs"
            % (len(paperDict), globalVar.loadedPapers, step1_elapsed)
        )

        if globalVar.cancelProcess:
            return

        # If not documents found
        if globalVar.loadedPapers == 0:
            print(
                "\nERROR: 0 documents found under " + args.dataInFolder
            )
            print("")
            globalVar.progressPer = 101
            return

        # ── Step 2/4 ── Scopus author-name disambiguation.
        _announce_step(2, "Disambiguating Scopus author names", self.fromGui)
        step_t0 = time.time()
        paperDict = paperUtils.disam_names_scopus(paperDict)
        globalVar.progressPer = 100
        print("  OK Done in %.1fs" % (time.time() - step_t0))

        globalVar.OriginalTotalPapers = len(paperDict)

        self.preProcessBrief["totalLoadedPapers"] = globalVar.loadedPapers
        self.preProcessBrief["omittedPapers"] = globalVar.omittedPapers
        self.preProcessBrief["papersAfterRemOmitted"] = globalVar.OriginalTotalPapers

        self.preProcessBrief["loadedPapersScopus"] = globalVar.papersScopus
        self.preProcessBrief["loadedPapersWoS"] = globalVar.papersWoS

        # Open the file to write the preprocessing log in CSV
        logFile = open(
            os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.PREPROCESS_LOG_FILE),
            "w",
            encoding="utf-8",
        )
        fieldnames = (
            ["Info", "Number", "Percentage", "Source"]
            + globalVar.INCLUDED_TYPES
            + ["Total"]
        )
        logWriter = csv.DictWriter(
            logFile, fieldnames=fieldnames, dialect=csv.excel, lineterminator="\n"
        )
        logWriter.writeheader()

        logWriter.writerow({"Info": "***** Original data *****"})
        logWriter.writerow(
            {"Info": "Loaded papers", "Number": str(globalVar.loadedPapers)}
        )

        logWriter.writerow(
            {
                "Info": "Omitted papers by document type",
                "Number": ("%d" % (globalVar.omittedPapers)),
                "Percentage": (
                    "%.1f%%" % (100.0 * globalVar.omittedPapers / globalVar.loadedPapers)
                ),
            }
        )

        logWriter.writerow(
            {
                "Info": "Total papers after omitted papers removed",
                "Number": str(globalVar.OriginalTotalPapers),
            }
        )

        if globalVar.OriginalTotalPapers > 0:
            logWriter.writerow(
                {
                    "Info": "Loaded papers from WoS",
                    "Number": ("%d" % (globalVar.papersWoS)),
                    "Percentage": (
                        "%.1f%%"
                        % (100.0 * globalVar.papersWoS / globalVar.OriginalTotalPapers)
                    ),
                }
            )
            logWriter.writerow(
                {
                    "Info": "Loaded papers from Scopus",
                    "Number": ("%d" % (globalVar.papersScopus)),
                    "Percentage": (
                        "%.1f%%"
                        % (
                            100.0
                            * globalVar.papersScopus
                            / globalVar.OriginalTotalPapers
                        )
                    ),
                }
            )

        print("Loaded papers: %s" % len(paperDict))
        print("Omitted papers: %s" % globalVar.omittedPapers)
        print("total papers: %s" % globalVar.OriginalTotalPapers)
        print("WoS papers: %s" % globalVar.papersWoS)
        print("Scopus papers: %s" % globalVar.papersScopus)
        paperUtils.sourcesStatics(paperDict, logWriter)

        # ── Step 3/4 ── Duplicate removal.
        if not args.noRemDupl:
            _announce_step(3, "Removing duplicates", self.fromGui)
            step_t0 = time.time()
            # Parallelize the per-paper titleB / firstAuthorLastName
            # normalization across cores so removeDuplicates only has to
            # sort + sweep.
            paperIO.compute_dedup_keys_parallel(paperDict)
            paperDict = paperUtils.removeDuplicates(
                paperDict, logWriter, self.preProcessBrief
            )
            print("  OK Done in %.1fs" % (time.time() - step_t0))
        # if not remove duplicates
        else:
            _announce_step(3, "Skipping duplicate removal (--noRemDupl)", self.fromGui)
            globalVar.progressPer = 100
            self.preProcessBrief["totalAfterRemDupl"] = self.preProcessBrief[
                "papersAfterRemOmitted"
            ]
            self.preProcessBrief["removedPapersScopus"] = 0
            self.preProcessBrief["removedPapersWoS"] = 0
            self.preProcessBrief["papersScopus"] = self.preProcessBrief[
                "loadedPapersScopus"
            ]
            self.preProcessBrief["papersWoS"] = self.preProcessBrief["loadedPapersWoS"]

        # Filter papers with invalid year
        papersDictYear = list(filter(lambda x: x["year"].isdigit(), paperDict))

        # To avoid by zero division
        if self.preProcessBrief["totalAfterRemDupl"] > 0:
            percentagePapersWos = (
                100.0
                * self.preProcessBrief["papersWoS"]
                / self.preProcessBrief["totalAfterRemDupl"]
            )
            percentagePapersScopus = (
                100.0
                * self.preProcessBrief["papersScopus"]
                / self.preProcessBrief["totalAfterRemDupl"]
            )
        else:
            percentagePapersWos = 0
            percentagePapersScopus = 0

        logWriter.writerow(
            {
                "Info": "Papers from WoS",
                "Number": ("%d" % (self.preProcessBrief["papersWoS"])),
                "Percentage": ("%.1f%%" % (percentagePapersWos)),
            }
        )
        logWriter.writerow(
            {
                "Info": "Papers from Scopus",
                "Number": ("%d" % (self.preProcessBrief["papersScopus"])),
                "Percentage": ("%.1f%%" % (percentagePapersScopus)),
            }
        )

        # Statics after removing duplicates
        if not args.noRemDupl:
            logWriter.writerow({"Info": ""})
            logWriter.writerow({"Info": "Statics after duplication removal filter"})
            paperUtils.sourcesStatics(paperDict, logWriter)

        # ── Step 4/4 ── Persist the canonical corpus. Legacy CSV is no
        # longer produced automatically; users can re-materialize it via
        # exportPapers.py --source preprocessed --format scopus (or wos).
        _announce_step(4, "Saving preprocessed corpus", self.fromGui)
        step_t0 = time.time()
        parquet_path = os.path.join(
            globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_PARQUET
        )
        paperIO.write_preprocessed(paperDict, parquet_path)
        globalVar.progressPer = 100
        print(
            "  OK Wrote %d papers to %s (%.1fs)"
            % (len(paperDict), parquet_path, time.time() - step_t0)
        )

        # Close log file
        logFile.close()

        total_elapsed = time.time() - pipeline_t0
        print("\n" + "=" * 50)
        print("Preprocess finished in %.1fs - %d papers ready" % (total_elapsed, len(paperDict)))
        print("=" * 50)

        globalVar.totalPapers = len(paperDict)
        globalVar.progressText = "Done"
        globalVar.progressPer = 101

    def graphBrief(self, args=""):
        if args == "":
            args = self

        graphUtils.graphPreprocess(plt, self.preProcessBrief)

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
            plt.savefig(
                os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot),
                bbox_inches="tight",
                pad_inches=0.01,
            )
            print(
                "Plot saved on: "
                + os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot)
            )
