import csv
import globalVar
import os

def saveResults(paperDict, outFileName):

  if globalVar.SAVE_RESULTS_ON == "SCOPUS_FIELDS":

    print("Saving results on: %s, with Scopus fields" % outFileName)

    ofile = open(outFileName, 'w', encoding='utf-8')

    # WoS Fieldnames
    fieldnames = ["Authors", "Title", "Year", "Source title", "Volume", "Issue", "Art. No.", "Page start",
                  "Page end", "Page count", "Cited by", "DOI", "Link", "Affiliations", "Authors with affiliations",
                  "Abstract", "Author Keywords", "Index Keywords", "bothKeywords", "Correspondence Address", "Editors",
                  "Publisher", "ISSN", "ISBN", "CODEN", "PubMed ID", "Language of Original Document",
                  "Abbreviated Source Title", "Document Type", "Source", "EID", "Subject", "duplicatedIn",
                  "country", "emailHost", "institution", "institutionWithCountry"]



    writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel_tab)

    writer.writeheader()

    for paperOut in paperDict:

      paperDicWrite = {}

      paperDicWrite["Authors"] = paperOut["author"]
      paperDicWrite["Title"] = paperOut["title"]
      paperDicWrite["Year"] = paperOut["year"]
      paperDicWrite["Source title"] = paperOut["sourceTitle"]
      paperDicWrite["Volume"] = paperOut["volume"]
      paperDicWrite["Issue"] = paperOut["issue"]
      paperDicWrite["Art. No."] = paperOut["artNo"]
      paperDicWrite["Page start"] = paperOut["pageSart"]
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
      paperDicWrite["duplicatedIn"] = paperOut["duplicatedIn"]
      paperDicWrite["country"] = paperOut["country"]
      paperDicWrite["emailHost"] = paperOut["emailHost"]
      paperDicWrite["institution"] = paperOut["institution"]
      paperDicWrite["institutionWithCountry"] = paperOut["institutionWithCountry"]
      paperDicWrite["bothKeywords"] = paperOut["bothKeywords"]

      writer.writerow(paperDicWrite)

    ofile.close()

  elif globalVar.SAVE_RESULTS_ON == "WOS_FIELDS":

    print("Saving results on: %s, with WoS fields" % outFileName)

    ofile = open(outFileName, 'w', encoding='utf-8')

    # WoS Fieldnames
    fieldnames = ["PT", "AU", "BA", "BE", "GP", "AF", "BF", "CA", "TI",
                  "SO", "SE", "BS", "LA", "DT", "CT", "CY", "CL", "SP", "HO", "DE",
                  "ID", "AB", "C1", "RP", "EM", "RI", "OI", "FU", "FX", "CR", "NR",
                  "TC", "Z9", "U1", "U2", "PU", "PI", "PA", "SN", "EI", "BN", "J9",
                  "JI", "PD", "PY", "VL", "IS", "PN", "SU", "SI", "MA", "BP", "EP",
                  "AR", "DI", "D2", "PG", "WC", "SC", "GA", "UT", "PM", "OA", "HC",
                  "HP", "DA", "duplicatedIn", "country"]

    writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel_tab)

    writer.writeheader()

    for paperOut in paperDict:
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

      paperDicWrite["duplicatedIn"] = paperOut["duplicatedIn"]
      paperDicWrite["country"] = paperOut["country"]

      writer.writerow(paperDicWrite)

    ofile.close()

  else:
    print("ERROR, no SAVE_RESULTS_ON selected on globalVar.py")


def saveTopResults(topicResults, criterionIn):

  # Upper first character
  criterion = criterionIn[0].upper() + criterionIn[1:]

  fileName = os.path.join(globalVar.RESULTS_FOLDER, criterion + ".tsv")
  ofile = open(fileName, 'w', encoding='utf-8')

  fieldnames = ["Pos.", criterion, "Total", "hIndex"] + list(topicResults[0]["year"])

  writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel_tab)
  writer.writeheader()

  sortedResults = sorted(topicResults, key=lambda x: x["PapersTotal"], reverse=True)

  count = 1
  for value in sortedResults:
    dictWriter = {}
    dictWriter["Pos."] = str(count)
    dictWriter[criterion] = value["name"]
    dictWriter["Total"] = value["PapersTotal"]
    dictWriter["hIndex"] = value["hIndex"]
    for yearItem in value["year"]:
      index = value["year"].index(yearItem)
      dictWriter[yearItem] = value["PapersCount"][index]

    count += 1
    writer.writerow(dictWriter)

  ofile.close()

  print("Saved top results on: %s" % fileName)


def saveExtendedResults(topicResults, criterionIn):

  # Upper first character
  criterion = criterionIn[0].upper() + criterionIn[1:]

  fileName = os.path.join(globalVar.RESULTS_FOLDER, criterion + "_extended.tsv")
  ofile = open(fileName, 'w', encoding='utf-8')

  fieldnames = ["Pos.", "Topic " + criterion, "Total", "Cited by", "EID", "EID2", "Year", "Title", "Authors",
                "Author keywords", "Both keywords", "Abstract", "Country", "Document type"]

  writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel_tab)
  writer.writeheader()

  sortedResults = sorted(topicResults, key=lambda x: x["PapersTotal"], reverse=True)

  count = 1
  for value in sortedResults:
    dictWriter = {}
    dictWriter["Pos."] = str(count)
    dictWriter["Topic " + criterion] = value["name"]
    dictWriter["Total"] = value["PapersTotal"]

    count += 1
    writer.writerow(dictWriter)

    # Sort papers by cited by count
    papersIn = value["papers"]
    papersIn = sorted(papersIn, key=lambda x: int(x["citedBy"]), reverse=True)

    for paper in papersIn:
      dictWriter = {}
      dictWriter["Title"] = paper["title"]
      dictWriter["Year"] = paper["year"]
      dictWriter["Authors"] = paper["author"]
      dictWriter["Country"] = paper["country"]
      dictWriter["Author keywords"] = paper["authorKeywords"]
      dictWriter["Both keywords"] = paper["bothKeywords"]
      dictWriter["Abstract"] = paper["abstract"]
      dictWriter["Document type"] = paper["documentType"]
      dictWriter["Cited by"] = paper["citedBy"]
      dictWriter["EID"] = paper["eid"]
      dictWriter["EID2"] = paper["duplicatedIn"]
      writer.writerow(dictWriter)

  ofile.close()

  print("Saved extended top results on: %s" % fileName)

def saveTopCited(papersDic):

  fileName = os.path.join(globalVar.RESULTS_FOLDER, "topCitedPapers.tsv")
  ofile = open(fileName, 'w', encoding='utf-8')

  fieldnames = ["Pos.", "Year", "Cited by", "Cited by scaled", "Title", "Authors", "Author keywords"]

  writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel_tab)
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
