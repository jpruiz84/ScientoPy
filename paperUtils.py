import csv
import globalVar
import re
import json
import unicodedata

def strip_accents(s):
   return ''.join(c for c in unicodedata.normalize('NFD', s)
                  if unicodedata.category(c) != 'Mn')


def analyzeFileDict(ifile, papersDict):
  firstLineTell = ifile.tell()
  firstLine = ifile.readline()
  ifile.seek(firstLineTell)

  if "\t" in firstLine:
    reader = csv.reader(ifile, delimiter='\t')
  else:
    reader = csv.reader(ifile, delimiter=',')

  header = 0
  rownum = 0
  for row in reader:
    # Save header row.
    if rownum == 0:
      header = row
    else:
      colnum = 0
      paperIn = {}

      # Init key elements as zero
      paperIn["authors"] = ""
      paperIn["title"] = ""
      paperIn["year"] = ""
      paperIn["source"] = ""
      paperIn["doi"] = ""

      paperIn["volume"] = ""
      paperIn["issue"] = ""
      paperIn["artNo"] = ""
      paperIn["pageSart"] = ""
      paperIn["pageEnd"] = ""
      paperIn["pageCount"] = ""
      paperIn["link"] = ""
      paperIn["affiliations"] = ""
      paperIn["authorsWithAffiliations"] = ""
      paperIn["correspondenceAddress"] = ""
      paperIn["editors"] = ""
      paperIn["publisher"] = ""
      paperIn["issn"] = ""
      paperIn["isbn"] = ""
      paperIn["coden"] = ""
      paperIn["pubMedId"] = ""
      paperIn["languageOfOriginalDocument"] = ""
      paperIn["abbreviatedSourceTitle"] = ""

      paperIn["abstract"] = ""
      paperIn["authorKeywords"] = ""
      paperIn["indexKeywords"] = ""
      paperIn["documentType"] = ""
      paperIn["affiliations"] = ""
      paperIn["cr"] = ""
      paperIn["eid"] = ""
      paperIn["dataBase"] = ""
      paperIn["country"] = ""
      paperIn["subject"] = ""
      paperIn["sourceTitle"] = ""

      paperIn["orcid"] = ""
      paperIn["citedReferences"] = ""

      paperIn["citedBy"] = ""
      paperIn["duplicatedIn"] = ""

      for col in row:
        if colnum >= len(header):
          break

        headerCol = header[colnum].decode("ascii", errors="ignore").encode()

        # Scopus fields
        if headerCol == "Authors": paperIn["authors"] = col.replace(",", ";")
        if headerCol == "Title": paperIn["title"] = col
        if headerCol == "Year": paperIn["year"] = col
        if headerCol == "Source title": paperIn["sourceTitle"] = col
        if headerCol == "Volume": paperIn["volume"] = col
        if headerCol == "Issue": paperIn["issue"] = col
        if headerCol == "Art. No.": paperIn["artNo"] = col
        if headerCol == "Page start": paperIn["pageSart"] = col
        if headerCol == "Page end": paperIn["pageEnd"] = col
        if headerCol == "Page count": paperIn["pageCount"] = col
        if headerCol == "Cited by": paperIn["citedBy"] = col
        if headerCol == "DOI": paperIn["doi"] = col
        if headerCol == "Link": paperIn["link"] = col
        if headerCol == "Affiliations": paperIn["affiliations"] = col
        if headerCol == "Authors with affiliations": paperIn["authorsWithAffiliations"] = col
        if headerCol == "Abstract": paperIn["abstract"] = col
        if headerCol == "Author Keywords": paperIn["authorKeywords"] = col
        if headerCol == "Index Keywords": paperIn["indexKeywords"] = col
        if headerCol == "Correspondence Address": paperIn["correspondenceAddress"] = col
        if headerCol == "Editors": paperIn["editors"] = col
        if headerCol == "Publisher": paperIn["publisher"] = col
        if headerCol == "ISSN": paperIn["issn"] = col
        if headerCol == "ISBN": paperIn["isbn"] = col
        if headerCol == "CODEN": paperIn["coden"] = col
        if headerCol == "PubMed ID": paperIn["pubMedId"] = col
        if headerCol == "Language of Original Document": paperIn["languageOfOriginalDocument"] = col
        if headerCol == "Abbreviated Source Title": paperIn["abbreviatedSourceTitle"] = col
        if headerCol == "Document Type": paperIn["documentType"] = col
        if headerCol == "Source": paperIn["source"] = col
        if headerCol == "EID": paperIn["eid"] = col

        # WoS fields
        #if headerCol == "PT": paperIn[""] = col
        if headerCol == "AU": paperIn["authors"] = col
        #if headerCol == "BA": paperIn[""] = col
        if headerCol == "BE": paperIn["editors"] = col
        #if headerCol == "GP": paperIn[""] = col
        #if headerCol == "AF": paperIn[""] = col   # Authors full name
        #if headerCol == "BF": paperIn[""] = col
        #if headerCol == "CA": paperIn[""] = col   # Group authors
        if headerCol == "TI": paperIn["title"] = col
        if headerCol == "SO": paperIn["sourceTitle"] = col
        #if headerCol == "SE": paperIn[""] = col   # Book Series Title
        #if headerCol == "BS": paperIn[""] = col   # Book Series subtitle
        if headerCol == "LA": paperIn["languageOfOriginalDocument"] = col
        if headerCol == "DT": paperIn["documentType"] = col
        #if headerCol == "CT": paperIn[""] = col   # Conference Title
        #if headerCol == "CY": paperIn[""] = col   # Conference Date
        #if headerCol == "CL": paperIn[""] = col   # Conference Location
        #if headerCol == "SP": paperIn[""] = col    # conference Sponsor
        #if headerCol == "HO": paperIn[""] = col
        if headerCol == "DE": paperIn["authorKeywords"] = col
        if headerCol == "ID": paperIn["indexKeywords"] = col
        if headerCol == "AB": paperIn["abstract"] = col
        if headerCol == "C1": paperIn["affiliations"] = col
        #if headerCol == "RP": paperIn[""] = col
        if headerCol == "EM": paperIn["correspondenceAddress"] = col
        #if headerCol == "RI": paperIn[""] = col
        if headerCol == "OI": paperIn["orcid"] = col
        #if headerCol == "FU": paperIn[""] = col
        #if headerCol == "FX": paperIn[""] = col
        if headerCol == "CR": paperIn["citedReferences"] = col
        #if headerCol == "NR": paperIn[""] = col
        if headerCol == "TC": paperIn["citedBy"] = col
        #if headerCol == "Z9": paperIn[""] = col
        #if headerCol == "U1": paperIn[""] = col
        #if headerCol == "U2": paperIn[""] = col
        if headerCol == "PU": paperIn["publisher"] = col
        #if headerCol == "PI": paperIn[""] = col
        #if headerCol == "PA": paperIn[""] = col
        if headerCol == "SN": paperIn["issn"] = col
        #if headerCol == "EI": paperIn[""] = col
        if headerCol == "BN": paperIn["isbn"] = col
        if headerCol == "J9": paperIn["abbreviatedSourceTitle"] = col
        #if headerCol == "JI": paperIn[""] = col
        #if headerCol == "PD": paperIn[""] = col
        if headerCol == "PY": paperIn["year"] = col
        if headerCol == "VL": paperIn["volume"] = col
        if headerCol == "IS": paperIn["issue"] = col
        #if headerCol == "PN": paperIn[""] = col
        #if headerCol == "SU": paperIn[""] = col
        #if headerCol == "SI": paperIn[""] = col
        #if headerCol == "MA": paperIn[""] = col
        if headerCol == "BP": paperIn["pageSart"] = col
        if headerCol == "EP": paperIn["pageEnd"] = col
        if headerCol == "AR": paperIn["artNo"] = col
        if headerCol == "DI": paperIn["doi"] = col
        #if headerCol == "D2": paperIn[""] = col
        if headerCol == "PG": paperIn["pageCount"] = col
        #if headerCol == "WC": paperIn["subject"] = col
        if headerCol == "SC": paperIn["subject"] = col
        #if headerCol == "GA": paperIn[""] = col
        if headerCol == "UT": paperIn["eid"] = col
        if headerCol == "PM": paperIn["pubMedId"] = col
        #if headerCol == "OA": paperIn[""] = col
        #if headerCol == "HC": paperIn[""] = col
        #if headerCol == "HP": paperIn[""] = col
        #if headerCol == "DA": paperIn[""] = col

        # Own fields
        if headerCol == "duplicatedIn": paperIn["duplicatedIn"] = col
        if headerCol == "country": paperIn["country"] = col

        colnum += 1

      # If cited by is emtpy add 0
      if paperIn["citedBy"] == "":
        paperIn["citedBy"] = "0"

      # Remove dots from authors
      paperIn["authors"] = paperIn["authors"].replace(".", "")

      # Remove coma from authors
      paperIn["authors"] = paperIn["authors"].replace(",", "")

      # Remove accents in authors
      paperIn["authors"] = strip_accents(unicode(paperIn["authors"], "utf-8"))
      paperIn["authors"] = paperIn["authors"].encode('utf-8')

      # Omit papers without title
      if paperIn["title"] == "":
        print("No title, continue")
        continue

      if paperIn["eid"].startswith("WOS"):
        paperIn["dataBase"] = "WoS"
        paperIn["source"] = "WoS"
        globalVar.papersWoS += 1

      if paperIn["eid"].startswith("2-"):
        paperIn["dataBase"] = "Scopus"
        globalVar.papersScopus += 1

      if paperIn["country"] == "":
        # Get the first author affiliations, and extract the last item as contry
        firstAf = re.split("; (?=[^\]]*(?:\[|$))", paperIn["affiliations"])[0]
        paperIn["country"] = re.split(", (?=[^\]]*(?:\[|$))", firstAf)[-1]

        if "CHINA".upper() in paperIn["country"].upper():
          paperIn["country"] = "China"

        if "USA".upper() in paperIn["country"].upper():
          paperIn["country"] = "United States"

        if "ENGLAND".upper() in paperIn["country"].upper():
          paperIn["country"] = "United Kingdom"
        if "SCOTLAND".upper() in paperIn["country"].upper():
          paperIn["country"] = "United Kingdom"
        if "WALES".upper() in paperIn["country"].upper():
          paperIn["country"] = "United Kingdom"

        if "U ARAB EMIRATES".upper() in paperIn["country"].upper():
          paperIn["country"] = "United Arab Emirates"

        if "RUSSIA".upper() in paperIn["country"].upper():
          paperIn["country"] = "Russian Federation"

        if "VIET NAM".upper() in paperIn["country"].upper():
          paperIn["country"] = "Vietnam"

        if "TRINID & TOBAGO".upper() in paperIn["country"].upper():
          paperIn["country"] = "Trinidad and Tobago"

      # If an author instead a country
      if paperIn["country"].endswith('.'):
        paperIn["country"] = "No country"

      # printPaper(paperIn)

      # Filter papers that are not in document tipe list
      if any(pType.upper() in paperIn["documentType"].upper().split("; ") \
             for pType in globalVar.INCLUDED_TYPES):
        papersDict.append(paperIn)
      else:
        globalVar.omitedPapers += 1
    rownum += 1

  ifile.close()

def getPapersLinkFromFile(ifile, papersDict):

  firstLineTell = ifile.tell()
  firstLine = ifile.readline()
  ifile.seek(firstLineTell)

  if "\t" in firstLine:
    reader = csv.reader(ifile, delimiter='\t')
  else:
    reader = csv.reader(ifile,delimiter=',')

  header = 0
  rownum = 0
  for row in reader:
    # Save header row.
    if rownum == 0:
      header = row
    else:
      colnum = 0
      paperIn = {}
      
      # Init key elements as zero        
      paperIn["Link"] = ""
      
      for col in row:
        #if colnum >= len(header):
        #  break

        #headerCol = header[colnum].decode("ascii", errors="ignore").encode()
        
        # Scopus fields
        if col.startswith("https://www.scopus.com"):
          paperIn["Link"] = col

        colnum += 1

      if paperIn["Link"] != "":
        papersDict.append(paperIn)

    rownum += 1

  ifile.close()
  

def printPaper(paper):
  print('Authors: %s' % (paper["authors"]))
  print('Title: %s' % (paper["title"]))
  print('Year: %s' % (paper["year"]))
  print('Source: %s' % (paper["source"]))
  print('DOI: %s' % (paper["doi"]))
  #print('Abstract: %s' % (paper["abstract"]))
  print('Author Key: %s' % (paper["authorKeywords"]))
  print('Index Key: %s' % (paper["indexKeywords"]))
  print('eid: %s' % (paper["eid"]))
  print('Data base: %s' % (paper["dataBase"]))
  print('Affilations:')
  
  for af in re.split("; (?=[^\]]*(?:\[|$))",paper["affiliations"]):
    print("- " + af)
  print('Country: %s' % (paper["country"]))
  print('Document type: %s' % (paper["documentType"]))
  print('Cited by: %s' % (paper["citedBy"]))
  print('\n')
  
  

  
def removeDuplicates(paperDict, logWriter):
  duplicatedPapersCount = 0
  removedPapersScopus = 0
  removedPapersWoS = 0
  duplicatedWithDifferentCitedBy = 0
  originalPapersCount = len(paperDict)
  noAuthors = 0

  # Remove part of the title inside parentisis or square brakets
  # Some journals put this the original language tile in the brakets
  # Remove whitespace at the end of the tile
  for paper in paperDict:
    paper["titleB"] = re.sub("[\(\[].*?[\)\]]", "", paper["title"].upper()).rstrip()

  # Short by database, to put WoS first over Scopus, reverse True
  paperDict = sorted(paperDict, key=lambda x: x["dataBase"], reverse=True)
  paperDict = sorted(paperDict, key=lambda x: x["titleB"])
 
  print("Removing duplicates...")
  print len(paperDict)

  # Run on paper list
  for i in range(0, len(paperDict)):


    match = True
    while(match):
      
      if i >= (len(paperDict) - 1):
        match = False
        continue

      match = paperDict[i]["authors"].split(" ")[0].upper() == paperDict[i+1]["authors"].split(" ")[0].upper()
      match &=  paperDict[i]["titleB"] == paperDict[i+1]["titleB"]

      
      # If the criterion match
      if(match == True):
        print("\nPaper %s duplicated with %s" %  (i, i+1))
        
        print("Dup A: %s, %s" % (paperDict[i]["title"], paperDict[i]["year"]))
        print("Authors: %s, Database: %s, Cited by: %s" %
        (paperDict[i]["authors"], paperDict[i]["dataBase"], paperDict[i]["citedBy"]))
        
        print("Dup B: %s, %s" % (paperDict[i+1]["title"], paperDict[i+1]["year"]))
        print("Authors: %s, Database: %s, Cited by: %s" %
        (paperDict[i+1]["authors"], paperDict[i+1]["dataBase"], paperDict[i+1]["citedBy"]))
        
        if paperDict[i+1]["dataBase"] == "WoS":
          removedPapersWoS += 1

        if paperDict[i+1]["dataBase"] == "Scopus":
          removedPapersScopus += 1
          
        # Remove paper j
        print("Removing: %s" % paperDict[i+1]["dataBase"])
        paperDict[i]["duplicatedIn"] = paperDict[i+1]["eid"]

        # Find how many duplicated documents has different cited by
        if int(paperDict[i]["citedBy"]) != int(paperDict[i + 1]["citedBy"]):
          duplicatedWithDifferentCitedBy += 1

        # If the cited by count from the paper to remove is bigger than the cited by count for
        # the paper to keep, set the cited by count with the bigger one
        if int(paperDict[i + 1]["citedBy"]) > int(paperDict[i]["citedBy"]):
          paperDict[i]["citedBy"] = paperDict[i + 1]["citedBy"]

        paperDict.remove(paperDict[i+1])
        duplicatedPapersCount += 1
        continue
        
    print("\r{0:.0f}%".format(float(i)/float(len(paperDict)) * 100)),
        
  print("\nDuplicated papers found: %s" % duplicatedPapersCount)
  print("Original papers count: %s" % originalPapersCount)
  print("Actual papers count: %s" % len(paperDict))
  print("Removed papers WoS: %s" % removedPapersWoS)
  print("Removed papers Scopus: %s" % removedPapersScopus)
  if(duplicatedPapersCount != 0):
    print("Duplicated documents with different cited by: %s, %s %%\n" % (duplicatedWithDifferentCitedBy,
          100*duplicatedWithDifferentCitedBy/duplicatedPapersCount))

  logWriter.writerow({'Info': ''})
  logWriter.writerow({'Info': '***** Duplication removal statics *****'})
  logWriter.writerow({'Info': 'Duplicated papers found', 'Number': str(duplicatedPapersCount)})
  logWriter.writerow({'Info': 'Original papers count', 'Number': str(originalPapersCount)})
  logWriter.writerow({'Info': 'Actual papers count', 'Number': str(len(paperDict))})
  logWriter.writerow({'Info': 'Removed papers WoS', 'Number': str(removedPapersWoS)})
  logWriter.writerow({'Info': 'Removed papers Scopus', 'Number': str(removedPapersScopus)})

  if(duplicatedPapersCount != 0):
    logWriter.writerow({'Info': 'Duplicated documents with different cited by', 'Number': str(duplicatedWithDifferentCitedBy)})

  return paperDict


def sourcesStatics(paperDict, logWriter):
  statics = {}

  statics["Scopus"]={}
  statics["Scopus"]["Article"] = 0
  statics["Scopus"]["Conference Paper"] = 0
  statics["Scopus"]["Proceedings Paper"] = 0
  statics["Scopus"]["Review"] = 0
  statics["Scopus"]["Total"] = 0
  statics["Scopus"]["Source"] = "Scopus"

  statics["WoS"] = {}
  statics["WoS"]["Article"] = 0
  statics["WoS"]["Conference Paper"] = 0
  statics["WoS"]["Proceedings Paper"] = 0
  statics["WoS"]["Review"] = 0
  statics["WoS"]["Total"] = 0
  statics["WoS"]["Source"] = "WoS"

  noDocumentTypeCount = 0

  for paper in paperDict:
    try:
      statics[paper["dataBase"]][paper["documentType"].split("; ")[0]] += 1

    except:
      noDocumentTypeCount += 1

    statics[paper["dataBase"]]["Total"] += 1

  logWriter.writerow(statics["Scopus"])
  logWriter.writerow(statics["WoS"])






  


