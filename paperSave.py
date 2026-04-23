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
import globalVar
import os
import math
import sys


def _progress_printer(total, label="Saving"):
    """Return a `tick(i)` callback that prints a live percentage to stdout
    whenever i crosses a whole-percent boundary. The final 100% line ends
    with a newline so subsequent prints don't sit on the progress row.

    Also updates globalVar.progressPer so the GUI progress dialog moves in
    sync during this stage.
    """
    last_pct = [-1]

    def tick(i):
        if total <= 0:
            return
        pct = int((i + 1) * 100 / total)
        if pct == last_pct[0]:
            return
        last_pct[0] = pct
        globalVar.progressPer = pct
        end = "\n" if pct >= 100 else ""
        sys.stdout.write("\r  %s... %3d%% (%d/%d)%s" % (label, pct, i + 1, total, end))
        sys.stdout.flush()

    return tick


def saveResults(paperDict, outFileName):

  if globalVar.SAVE_RESULTS_ON == "SCOPUS_FIELDS":

    print("Saving results on: %s, with Scopus fields, total %d papers" % (outFileName, len(paperDict)))
    tick = _progress_printer(len(paperDict))

    ofile = open(outFileName, 'w', encoding='utf-8')

    # Scopus Fieldnames
    fieldnames = ["Authors", "Title", "Year", "Source title", "Volume", "Issue", "Art. No.", "Page start",
                  "Page end", "Page count", "Cited by", "DOI", "Link", "Affiliations", "Authors with affiliations",
                  "Abstract", "Author Keywords", "Index Keywords", "bothKeywords", "Correspondence Address", "Editors",
                  "Publisher Address", "Conference name", "Conference location", "Conference date",
                  "Publisher", "ISSN", "ISBN", "CODEN", "PubMed ID", "Language of Original Document",
                  "Abbreviated Source Title", "Document Type", "Source", "Subject", "EID", "duplicatedIn",
                  "country", "emailHost", "institution", "institutionWithCountry", "authorFull", "Open Access"]



    writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel, lineterminator='\n')

    writer.writeheader()

    for _i, paperOut in enumerate(paperDict):

      paperDicWrite = {}

      # Relpace ";" to "," to have the same Scopus format output
      paperDicWrite["Authors"] = paperOut["author"].replace(";", ",")

      paperDicWrite["Title"] = paperOut["title"]
      paperDicWrite["Year"] = paperOut["year"]
      paperDicWrite["Source title"] = paperOut["sourceTitle"]
      paperDicWrite["Volume"] = paperOut["volume"]
      paperDicWrite["authorFull"] = paperOut["authorFull"]
      paperDicWrite["Issue"] = paperOut["issue"]
      paperDicWrite["Art. No."] = paperOut["artNo"]
      paperDicWrite["Page start"] = paperOut["pageStart"]
      paperDicWrite["Page end"] = paperOut["pageEnd"]
      paperDicWrite["Page count"] = paperOut["pageCount"]
      paperDicWrite["Cited by"] = paperOut["citedBy"]
      paperDicWrite["DOI"] = paperOut["doi"]
      paperDicWrite["Link"] = paperOut["link"]
      paperDicWrite["Affiliations"] = paperOut["affiliations"]
      paperDicWrite["Authors with affiliations"] = paperOut["authorsWithAffiliations"]
      paperDicWrite["Abstract"] = paperOut["abstract"]
      paperDicWrite["Author Keywords"] = paperOut["authorKeywords"]
      paperDicWrite["Index Keywords"] = paperOut["indexKeywords"]
      paperDicWrite["Correspondence Address"] = paperOut["correspondenceAddress"]
      paperDicWrite["Editors"] = paperOut["editors"]

      paperDicWrite["Publisher Address"] = paperOut["publisherAddress"]
      paperDicWrite["Conference name"] = paperOut["conferenceTitle"]
      paperDicWrite["Conference location"] = paperOut["conferenceLocation"]
      paperDicWrite["Conference date"] = paperOut["conferenceDate"]

      paperDicWrite["Publisher"] = paperOut["publisher"]
      paperDicWrite["ISSN"] = paperOut["issn"]
      paperDicWrite["ISBN"] = paperOut["isbn"]
      paperDicWrite["CODEN"] = paperOut["coden"]
      paperDicWrite["PubMed ID"] = paperOut["pubMedId"]
      paperDicWrite["Language of Original Document"] = paperOut["languageOfOriginalDocument"]
      paperDicWrite["Abbreviated Source Title"] = paperOut["abbreviatedSourceTitle"]
      paperDicWrite["Document Type"] = paperOut["documentType"]
      paperDicWrite["Source"] = paperOut["source"]
      paperDicWrite["EID"] = paperOut["eid"]

      paperDicWrite["Subject"] = paperOut["subject"]
      paperDicWrite["duplicatedIn"] = ";".join(paperOut["duplicatedIn"])
      paperDicWrite["country"] = paperOut["country"]
      paperDicWrite["emailHost"] = paperOut["emailHost"]
      paperDicWrite["institution"] = paperOut["institution"]
      paperDicWrite["institutionWithCountry"] = paperOut["institutionWithCountry"]
      paperDicWrite["bothKeywords"] = paperOut["bothKeywords"]
      
      paperDicWrite["Open Access"] = paperOut["openAccess"]

      writer.writerow(paperDicWrite)
      tick(_i)

    ofile.close()

  elif globalVar.SAVE_RESULTS_ON == "WOS_FIELDS":

    print("Saving results on: %s, with WoS fields, total %d papers" % (outFileName, len(paperDict)))
    tick = _progress_printer(len(paperDict))

    ofile = open(outFileName, 'w', encoding='utf-8')

    # WoS Fieldnames
    fieldnames = ["PT", "AU", "BA", "BE", "GP", "AF", "BF", "CA", "TI",
                  "SO", "SE", "BS", "LA", "DT", "CT", "CY", "CL", "SP", "HO", "DE",
                  "ID", "AB", "C1", "RP", "EM", "RI", "OI", "FU", "FX", "CR", "NR",
                  "TC", "Z9", "U1", "U2", "PU", "PI", "PA", "SN", "EI", "BN", "J9",
                  "JI", "PD", "PY", "VL", "IS", "PN", "SU", "SI", "MA", "BP", "EP",
                  "AR", "DI", "D2", "PG", "WC", "SC", "GA", "UT", "PM", "OA", "HC",
                  "HP", "DA", "duplicatedIn", "country"]

    writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel, lineterminator='\n')

    writer.writeheader()

    for _i, paperOut in enumerate(paperDict):
      paperDicWrite = {}
      paperDicWrite["AU"] = paperOut["author"]
      paperDicWrite["TI"] = paperOut["title"]
      paperDicWrite["PY"] = paperOut["year"]
      paperDicWrite["SO"] = paperOut["source"]
      paperDicWrite["DI"] = paperOut["doi"]
      paperDicWrite["AB"] = paperOut["abstract"]
      paperDicWrite["DE"] = paperOut["authorKeywords"]
      paperDicWrite["ID"] = paperOut["indexKeywords"]
      paperDicWrite["DT"] = paperOut["documentType"]
      paperDicWrite["C1"] = paperOut["affiliations"]
      paperDicWrite["SC"] = paperOut["subject"]
      paperDicWrite["TC"] = paperOut["citedBy"]
      paperDicWrite["CR"] = paperOut["cr"]
      paperDicWrite["UT"] = paperOut["eid"]

      paperDicWrite["duplicatedIn"] = ";".join(paperOut["duplicatedIn"])
      paperDicWrite["country"] = paperOut["country"]

      paperDicWrite["OA"] = paperOut["openAccess"]

      writer.writerow(paperDicWrite)
      tick(_i)

    ofile.close()

  else:
    print("ERROR, no SAVE_RESULTS_ON selected on globalVar.py")


def saveTopResults(topicResults, criterionIn, plotName):

  Name = ''
  if plotName != '':
    Name = '_' + os.path.splitext(plotName)[0]

  # Upper first character
  criterion = criterionIn[0].upper() + criterionIn[1:]

  fileName = os.path.join(globalVar.RESULTS_FOLDER, criterion + Name + ".csv")
  ofile = open(fileName, 'w', encoding='utf-8')

  fieldnames = ["Pos.", criterion, "Total", "AGR", "ADY", "PDLY", "hIndex"] + list(topicResults[0]["year"])

  writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel, lineterminator='\n')
  writer.writeheader()

  sortedResults = sorted(topicResults, key=lambda x: x["PapersTotal"], reverse=True)

  count = 1
  for value in sortedResults:
    dictWriter = {}
    dictWriter["Pos."] = str(count)
    dictWriter[criterion] = value["name"]
    dictWriter["Total"] = value["PapersTotal"]
    dictWriter["AGR"] = value["agr"]
    dictWriter["ADY"] = value["AverageDocPerYear"]
    dictWriter["PDLY"] = value["PerInLastYears"]
    dictWriter["hIndex"] = value["hIndex"]
    for yearItem in value["year"]:
      index = value["year"].index(yearItem)
      if math.isnan(value["PapersCount"][index]):
        dictWriter[yearItem] = 0
      else:
        dictWriter[yearItem] = value["PapersCount"][index]

    count += 1
    writer.writerow(dictWriter)

  ofile.close()

  print("Saved top results on: %s" % fileName)
  return fileName


EXT_FIELDNAMES = [
  "Pos.", "Topic ", "Total", "Cited by", "EID", "Year", "Title",
  "Abstract", "Document type", "Authors", "Author keywords",
  "Both keywords", "Country", "EID2",
]


def extendedResultsRows(topicResults, criterionIn):
  """Return (headers, rows) for the extended-results table.

  Shared source of truth between the on-disk exporter (saveExtendedResults)
  and the GUI Extended Results tab, which now populates itself directly
  from the in-memory topicResults rather than a CSV round-trip.

  Row shape matches the legacy saveExtendedResults CSV:
    * For every topic: one header row (Pos, Topic, Total) with the rest blank.
    * Then one row per paper with Cited by / EID / Year / Title / Abstract /
      Document type / Authors / Author keywords / Both keywords / Country /
      EID2 (duplicated-in EIDs joined by ';').
  """
  criterion = criterionIn[0].upper() + criterionIn[1:]
  headers = [
    "Pos.", "Topic " + criterion, "Total", "Cited by", "EID", "Year", "Title",
    "Abstract", "Document type", "Authors", "Author keywords",
    "Both keywords", "Country", "EID2",
  ]
  idx = {h: i for i, h in enumerate(headers)}

  rows = []
  sortedResults = sorted(topicResults, key=lambda x: x["PapersTotal"], reverse=True)
  count = 1
  for value in sortedResults:
    row = [""] * len(headers)
    row[idx["Pos."]] = str(count)
    row[idx["Topic " + criterion]] = value["name"]
    row[idx["Total"]] = str(value["PapersTotal"])
    rows.append(row)
    count += 1

    papersIn = sorted(value["papers"], key=lambda x: int(x["citedBy"]), reverse=True)
    for paper in papersIn:
      row = [""] * len(headers)
      row[idx["Cited by"]] = str(paper["citedBy"])
      row[idx["EID"]] = paper["eid"]
      row[idx["Year"]] = paper["year"]
      row[idx["Title"]] = paper["title"]
      row[idx["Abstract"]] = paper["abstract"]
      row[idx["Document type"]] = paper["documentType"]
      row[idx["Authors"]] = paper["author"]
      row[idx["Author keywords"]] = paper["authorKeywords"]
      row[idx["Both keywords"]] = paper["bothKeywords"]
      row[idx["Country"]] = paper["country"]
      row[idx["EID2"]] = ";".join(paper["duplicatedIn"])
      rows.append(row)
  return headers, rows


def saveExtendedResults(topicResults, criterionIn, plotName, outPath=None):
  """Write the extended-results CSV from in-memory topicResults.

  Called explicitly — never during a normal analysis anymore. Triggered by:
    * the ``--saveExtended`` CLI flag on scientoPy.py
    * the GUI Export tab's "Extended results (last analysis)" source
    * exportPapers.py when the extended rows happen to be passed in

  ``outPath`` overrides the default ``results/<Criterion>[_plotname]_extended.csv``
  destination (used by the GUI Export tab so users can pick their own path).
  """
  if outPath is None:
    Name = ''
    if plotName != '':
      Name = '_' + os.path.splitext(plotName)[0]
    criterion = criterionIn[0].upper() + criterionIn[1:]
    outPath = os.path.join(globalVar.RESULTS_FOLDER, criterion + Name + "_extended.csv")

  # Make sure the destination folder exists (the CLI default is results/,
  # but GUI users may target export/... for the first time).
  os.makedirs(os.path.dirname(os.path.abspath(outPath)) or ".", exist_ok=True)

  headers, rows = extendedResultsRows(topicResults, criterionIn)
  tick = _progress_printer(len(rows), label="Saving extended")

  with open(outPath, 'w', encoding='utf-8') as ofile:
    writer = csv.writer(ofile, dialect=csv.excel, lineterminator='\n')
    writer.writerow(headers)
    for i, r in enumerate(rows):
      writer.writerow(r)
      tick(i)

  print("Saved extended top results on: %s" % outPath)
  return outPath

def saveTopCited(papersDic):

  fileName = os.path.join(globalVar.RESULTS_FOLDER, "topCitedPapers.csv")
  ofile = open(fileName, 'w', encoding='utf-8')

  fieldnames = ["Pos.", "Year", "Cited by", "Cited by scaled", "Title", "Authors", "Author keywords"]

  writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel, lineterminator='\n')
  writer.writeheader()

  count = 1
  for paper in papersDic:
    dictWriter = {}
    dictWriter["Pos."] = str(count)
    dictWriter["Year"] = paper["year"]
    dictWriter["Cited by"] = paper["citedBy"]
    dictWriter["Cited by scaled"] = int(paper["scaledCitedBy"])
    dictWriter["Title"] = paper["title"]
    dictWriter["Authors"] = paper["author"]
    dictWriter["Author keywords"] = paper["authorKeywords"].upper()
    writer.writerow(dictWriter)

    count += 1

  ofile.close()

  print("Saved top cited results on: %s" % fileName)

  return fileName
