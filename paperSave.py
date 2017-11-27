import csv
import globalVar
import os

def saveResults(paperDict, outFileName):

  print("Saving results on: %s" % outFileName)

  ofile = open(outFileName, 'w')

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
    paperDicWrite["AU"] = paperOut["authors"]
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
  
def saveTopResults(resultsDict, criterionIn):
  
  # Upper first character
  criterion = criterionIn[0].upper() + criterionIn[1:]

  fileName = os.path.join(globalVar.RESULTS_FOLDER, criterion + ".csv")
  ofile = open(fileName, 'w')
  
  fieldnames = ["Pos.", criterion, "Total", "hIndex"] + resultsDict[resultsDict.keys()[0]]["year"]
  
  writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel_tab)
  writer.writeheader()
  
  sortedResults = sorted(resultsDict.iteritems(), key=lambda (k,v): (-v["total"],k))
  
  count = 1
  for item in sortedResults:
    key = item[0]
    value = item[1]
    dictWriter = {}
    dictWriter["Pos."] = str(count)
    dictWriter[criterion] = value["name"]
    dictWriter["Total"] = value["total"]
    dictWriter["hIndex"] = value["hIndex"]
    for yearItem in value["year"]:
      index = value["year"].index(yearItem)
      dictWriter[yearItem] = value["count"][index]
  
    count += 1
    writer.writerow(dictWriter)

  ofile.close()
  
  print("\nSaved top results on: %s" % fileName)
  
  
def saveExtendedResults(resultsDict, criterionIn):
  
  # Upper first character
  criterion = criterionIn[0].upper() + criterionIn[1:]
  
  fileName = os.path.join(globalVar.RESULTS_FOLDER, criterion + "_extended.csv")
  ofile = open(fileName, 'w')
  
  fieldnames = ["Pos.", "Topic " + criterion, "Total", "Cited by", "EID", "EID2", "Year", "Title", "Authors", "Author keywords", "Country", "Document type"]
  
  writer = csv.DictWriter(ofile, fieldnames=fieldnames, dialect=csv.excel_tab)
  writer.writeheader()
  
  sortedResults = sorted(resultsDict.iteritems(), key=lambda (k,v): (-v["total"],k))
  
  count = 1
  for itemR in sortedResults:
    key = itemR[0]
    value = itemR[1]
    dictWriter = {}
    dictWriter["Pos."] = str(count)
    dictWriter["Topic " + criterion] = value["name"]
    dictWriter["Total"] = value["total"]

    count += 1
    writer.writerow(dictWriter)

    # Sort papers by cited by count
    papersIn = value["papers"]
    papersIn = sorted(papersIn, key=lambda x: int(x["citedBy"]), reverse=True)

    for paper in papersIn:
      dictWriter = {}
      dictWriter["Title"] = paper["title"]
      dictWriter["Year"] = paper["year"]
      dictWriter["Authors"] = paper["authors"]
      dictWriter["Country"] = paper["country"]
      dictWriter["Author keywords"] = paper["authorKeywords"].upper()
      dictWriter["Document type"] = paper["documentType"]
      dictWriter["Cited by"] = paper["citedBy"]
      dictWriter["EID"] = paper["eid"]
      dictWriter["EID2"] = paper["duplicatedIn"]
      writer.writerow(dictWriter)

  ofile.close()
  
  print("\nSaved extended top results on: %s" % fileName)
