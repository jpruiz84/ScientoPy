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

      paperIn["emailHost"] = ""
      paperIn["institution"] = ""

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
        #if headerCol == "PT": paperIn[""] = col    # Publication Type (J=Journal; B=Book; S=Series; P=Patent)
        if headerCol == "AU": paperIn["authors"] = col    # Authors
        #if headerCol == "BA": paperIn[""] = col    # Book authors
        if headerCol == "BE": paperIn["editors"] = col    # Editors
        #if headerCol == "GP": paperIn[""] = col    # Book Group Author(s)
        #if headerCol == "AF": paperIn[""] = col    # Authors full name
        #if headerCol == "BF": paperIn[""] = col    # Book Authors Full Name
        #if headerCol == "CA": paperIn[""] = col    # Group authors
        if headerCol == "TI": paperIn["title"] = col    # Document Title
        if headerCol == "SO": paperIn["sourceTitle"] = col    # Publication Name
        #if headerCol == "SE": paperIn[""] = col   # Book Series Title
        #if headerCol == "BS": paperIn[""] = col   # Book Series subtitle
        if headerCol == "LA": paperIn["languageOfOriginalDocument"] = col   # Language
        if headerCol == "DT": paperIn["documentType"] = col   # Language
        #if headerCol == "CT": paperIn[""] = col    # Conference Title
        #if headerCol == "CY": paperIn[""] = col    # Conference Date
        #if headerCol == "CL": paperIn[""] = col    # Conference Location
        #if headerCol == "SP": paperIn[""] = col    # Conference Sponsor
        #if headerCol == "HO": paperIn[""] = col    # Conference Host
        if headerCol == "DE": paperIn["authorKeywords"] = col   # Author Keywords
        if headerCol == "ID": paperIn["indexKeywords"] = col    # Keywords Plus
        if headerCol == "AB": paperIn["abstract"] = col   # Abstract
        if headerCol == "C1": paperIn["affiliations"] = col   # Author Address
        #if headerCol == "RP": paperIn[""] = col    # Reprint Address
        if headerCol == "EM": paperIn["correspondenceAddress"] = col    # E-mail Address
        #if headerCol == "RI": paperIn[""] = col    # ResearcherID Number
        if headerCol == "OI": paperIn["orcid"] = col    # ORCID Identifier (Open Researcher and Contributor ID)
        #if headerCol == "FU": paperIn[""] = col    # Funding Agency and Grant Number
        #if headerCol == "FX": paperIn[""] = col    # Funding Text
        if headerCol == "CR": paperIn["citedReferences"] = col    # Cited References
        #if headerCol == "NR": paperIn[""] = col    # Cited Reference Count
        #if headerCol == "TC": paperIn["citedBy"] = col    # Web of Science Core Collection Times Cited Count

        # Total Times Cited Count (Web of Science Core Collection, BIOSIS Citation Index,
        # Chinese Science Citation Database, Data Citation Index, Russian Science Citation Index, SciELO Citation Index)
        if headerCol == "Z9": paperIn["citedBy"] = col

        #if headerCol == "U1": paperIn[""] = col    # Usage Count (Last 180 Days)
        #if headerCol == "U2": paperIn[""] = col    # Usage Count (Since 2013)
        if headerCol == "PU": paperIn["publisher"] = col    # Publisher
        #if headerCol == "PI": paperIn[""] = col    # Publisher City
        #if headerCol == "PA": paperIn[""] = col    # Publisher Address
        if headerCol == "SN": paperIn["issn"] = col   # International Standard Serial Number (ISSN)
        #if headerCol == "EI": paperIn[""] = col    # Electronic International Standard Serial Number (eISSN)
        if headerCol == "BN": paperIn["isbn"] = col   # International Standard Book Number (ISBN)
        if headerCol == "J9": paperIn["abbreviatedSourceTitle"] = col   # 29-Character Source Abbreviation
        #if headerCol == "JI": paperIn[""] = col    # ISO Source Abbreviation
        #if headerCol == "PD": paperIn[""] = col    # Publication Date
        if headerCol == "PY": paperIn["year"] = col   # Year Published
        if headerCol == "VL": paperIn["volume"] = col   # Volume
        if headerCol == "IS": paperIn["issue"] = col    # Issue
        #if headerCol == "PN": paperIn[""] = col    # Part Number
        #if headerCol == "SU": paperIn[""] = col    # Supplement
        #if headerCol == "SI": paperIn[""] = col    # Special Issue
        #if headerCol == "MA": paperIn[""] = col    # Meeting Abstract
        if headerCol == "BP": paperIn["pageSart"] = col   # Beginning Page
        if headerCol == "EP": paperIn["pageEnd"] = col    # Ending Page
        if headerCol == "AR": paperIn["artNo"] = col    # Article Number
        if headerCol == "DI": paperIn["doi"] = col    # Digital Object Identifier (DOI)
        #if headerCol == "D2": paperIn[""] = col    # Book Digital Object Identifier (DOI)
        if headerCol == "PG": paperIn["pageCount"] = col    # Page Count
        #if headerCol == "WC": paperIn["subject"] = col   # Web of Science Categories
        if headerCol == "SC": paperIn["subject"] = col    # Research Areas
        #if headerCol == "GA": paperIn[""] = col          #Document Delivery Number
        if headerCol == "UT": paperIn["eid"] = col        # Accession Number
        if headerCol == "PM": paperIn["pubMedId"] = col   # PubMed ID
        #if headerCol == "OA": paperIn[""] = col      # Open Access Indicator
        #if headerCol == "HC": paperIn[""] = col      # ESI Highly Cited Paper. Note that this field is valued only for ESI subscribers.
        #if headerCol == "HP": paperIn[""] = col      # ESI Hot Paper. Note that this field is valued only for ESI subscribers.
        #if headerCol == "DA": paperIn[""] = col      # Date this report was generated.

        # Own fields
        if headerCol == "duplicatedIn": paperIn["duplicatedIn"] = col
        if headerCol == "country": paperIn["country"] = col
        if headerCol == "emailHost": paperIn["emailHost"] = col

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

      # Get email host
      if paperIn["emailHost"] == "":
        splited1 = paperIn["correspondenceAddress"].split("@")
        if len(splited1) > 1:
          splited2 = splited1[1].split(";")
          paperIn["emailHost"] = splited2[0]
        else:
          paperIn["emailHost"] = "No email"

      # Institution from WoS
      if paperIn["institution"] == "":
        if paperIn["dataBase"] == "WoS" and paperIn["affiliations"] != "":
          # Get the first author affiliations, and extract the first item as institution
          firstAf = re.split("; (?=[^\]]*(?:\[|$))", paperIn["affiliations"])[0]
          paperIn["institution"] = re.split(", (?=[^\]]*(?:\[|$))|]", firstAf)[1].strip()

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






  


