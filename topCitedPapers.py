#!/usr/bin/env python3

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

import argparse
import sys

import globalVar
import networkAnalysis as na
import paperSave

parser = argparse.ArgumentParser(
    description="List the most cited documents of the preprocessed dataset",
    epilog="The table is saved as results/%s. The citations are the ones reported by "
           "Scopus or WoS when the dataset was downloaded." % globalVar.TOP_CITED_FILE,
)

parser.add_argument("-l", "--length", type=int, default=10,
                    help="Number of documents to list, default 10")

parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,
                    help="Start year to limit the search, default: " + str(globalVar.DEFAULT_START_YEAR))

parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,
                    help="End year to limit the search, default: " + str(globalVar.DEFAULT_END_YEAR))

parser.add_argument("-r", "--previousResults", action="store_true",
                    help="List the most cited documents among the ones found by the previous "
                         "scientoPy.py analysis, for example the documents of a topic or a country")


def topCited(length=10, startYear=globalVar.DEFAULT_START_YEAR,
             endYear=globalVar.DEFAULT_END_YEAR, previousResults=False):
    """Find the most cited documents and save them. Returns (headers, rows, path).

    Raises networkAnalysis.NetworkError when the dataset is missing, the
    year range is not valid or it has no documents.
    """
    if startYear > endYear:
        raise na.NetworkError("startYear (%d) > endYear (%d)" % (startYear, endYear))
    papers = na.load_papers(previousResults)
    headers, rows = paperSave.topCitedRows(papers, length, startYear, endYear)
    if not rows:
        raise na.NetworkError("No papers found in the range %d - %d" % (startYear, endYear))
    path = paperSave.saveTopCited(headers, rows)
    return headers, rows, path


def main():
    args = parser.parse_args()

    print("\n\nScientoPy top cited documents: %s" % globalVar.SCIENTOPY_VERSION)
    print("====================================\n")

    try:
        headers, rows, path = topCited(args.length, args.startYear, args.endYear,
                                       args.previousResults)
    except na.NetworkError as e:
        print("ERROR: %s" % e)
        sys.exit(1)

    col = {name: k for k, name in enumerate(headers)}
    print("")
    print('-' * 110)
    print("{:<5s}{:>9s}{:>10s}{:>6s}  {:<24s} {:<54s}".format(
        "Pos", "Cited by", "Per year", "Year", "Authors", "Title"))
    print('-' * 110)
    for row in rows:
        print("{:<5s}{:>9s}{:>10s}{:>6s}  {:<24s} {:<54s}".format(
            row[col["Pos."]], row[col["Cited by"]], row[col["Cited by per year"]],
            row[col["Year"]], row[col["Authors"]][:24], row[col["Title"]][:54]))
    print('-' * 110)


if __name__ == '__main__':
    main()
