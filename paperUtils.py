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
import globalVar
import re
import unicodedata
import sys
import unidecode

def openFileToDict(ifile, papersDict):
  firstLineTell = ifile.tell()
  firstLine = ifile.readline()
  ifile.seek(firstLineTell)

  if "\t" in firstLine:
    reader = csv.reader(ifile, delimiter='\t')
  else:
    reader = csv.reader(ifile, delimiter=',')

  csv.field_size_limit(int(2e9))

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
      paperIn["author"] = ""
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
      paperIn["countries"] = ""
      paperIn["subject"] = ""
      paperIn["sourceTitle"] = ""

      paperIn["orcid"] = ""
      paperIn["citedReferences"] = ""

      paperIn["citedBy"] = ""
      paperIn["duplicatedIn"] = []

      paperIn["emailHost"] = ""
      paperIn["country"] = ""
      paperIn["institution"] = ""
      paperIn["institutionWithCountry"] = ""
      paperIn["bothKeywords"] = ""
      paperIn["authorFull"] = ""

      for col in row:
        if colnum >= len(header):
          break

        # remove special accents
        headerCol = unidecode.unidecode(header[colnum])

        # Scopus fields
        if headerCol == "Authors": paperIn["author"] = col
        if headerCol == "Authors": paperIn["authorFull"] = col
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
        if headerCol == "AU": paperIn["author"] = col    # Authors
        #if headerCol == "BA": paperIn[""] = col    # Book authors
        if headerCol == "BE": paperIn["editors"] = col    # Editors
        #if headerCol == "GP": paperIn[""] = col    # Book Group Author(s)
        if headerCol == "AF": paperIn["authorFull"] = col    # Authors full name
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
        if headerCol == "Subject": paperIn["subject"] = col
        if headerCol == "duplicatedIn": paperIn["duplicatedIn"] = col.split(";")
        if headerCol == "country": paperIn["country"] = col
        if headerCol == "institution": paperIn["institution"] = col
        if headerCol == "institutionWithCountry": paperIn["institutionWithCountry"] = col
        if headerCol == "bothKeywords": paperIn["bothKeywords"] = col
        if headerCol == "emailHost": paperIn["emailHost"] = col
        if headerCol == "authorFull": paperIn["authorFull"] = col

        colnum += 1

      # Omit papers without title
      if paperIn["title"] == "":
        print("No title, continue")
        continue

      # Put the database ussing eid
      if paperIn["dataBase"] == "":
        if paperIn["eid"].startswith("WOS"):
          paperIn["dataBase"] = "WoS"
          paperIn["source"] = "WoS"

        if paperIn["eid"].startswith("2-"):
          paperIn["dataBase"] = "Scopus"

      # If cited by is emtpy add 0
      if paperIn["citedBy"] == "":
        paperIn["citedBy"] = "0"

      # Change to false to not preprocess author
      if True:
        # For Scopus author, replace , with ;
        if paperIn["dataBase"] == "Scopus":
          paperIn["author"] = paperIn["author"].replace(".,", ";")

        # Remove dots from author
        paperIn["author"] = paperIn["author"].replace(".", "")

        # Remove coma from author
        paperIn["author"] = paperIn["author"].replace(",", "")

        # Remove accents in author
        paperIn["author"] = unidecode.unidecode(paperIn["author"])
        paperIn["authorFull"] = unidecode.unidecode(paperIn["authorFull"])


      # Extract country, institution and institutionWithCountry from affilation
      if paperIn["country"] == "" or paperIn["institution"] == "" or paperIn["institutionWithCountry"] == "":

        # Get each author affiliations
        affiliations = re.split("; (?=[^\]]*(?:\[|$))", paperIn["affiliations"])

        countries = []
        institutions = []
        institutionsWithCoutnry = []

        # For each affiliation
        for affiliation in affiliations:
          # Divide affiliation in sections by ",", but not consider "," inside "[]"
          afSections = re.split(", (?=[^\]]*(?:\[|$))|]", affiliation)

          # The last item in affiliation list is the country
          country = afSections[-1].strip()

          # Remove dots in country
          country = country.replace(".", "")

          if "BOSNIA & HERCEG".upper() == country.upper():
            country = "Bosnia and Herzegovina"

          if "CHINA".upper() in country.upper():
            country = "China"

          if "ENGLAND".upper() in country.upper():
            country = "United Kingdom"
          if "SCOTLAND".upper() in country.upper():
            country = "United Kingdom"
          if "WALES".upper() in country.upper():
            country = "United Kingdom"
          if "UK".upper() == country.upper():
            country = "United Kingdom"

          if "KINGDOM OF SAUDI ARABIA".upper() == country.upper():
            country = "Saudi Arabia"

          if "RUSSIA".upper() in country.upper():
            country = "Russian Federation"

          if "TRINID & TOBAGO".upper() == country.upper():
            country = "Trinidad and Tobago"

          if "U ARAB EMIRATES".upper() == country.upper():
            country = "United Arab Emirates"

          if "USA".upper() in country.upper():
            country = "United States"

          if "VIET NAM".upper() == country.upper():
            country = "Vietnam"

          # To do not duplicate countries in country field
          if country.upper() not in [x.upper() for x in countries]:
            countries.append(country)

          # Get institution
          institution = ""
          if paperIn["dataBase"] == "WoS" and affiliations != "":
            # Extract institution as the second element in affiliation sections
            if len(afSections) >= 2:
              institution = afSections[1].strip()
              if institution.upper() not in [x.upper() for x in institutions]:
                institutions.append(institution)

          institutionWithCoutnry = ""
          if institution != "":
            institutionWithCoutnry = ("%s, %s" % (institution.replace(",", ""), country.replace(",", "")))
            if institutionWithCoutnry.upper() not in [x.upper() for x in institutionsWithCoutnry]:
              institutionsWithCoutnry.append(institutionWithCoutnry)

          #print("\nOriginal: %s" % affiliation)
          #print("afSections: %s" % str(afSections))
          #print("country: %s" % country)
          #print("institution: %s" % institution)
          #print("institutionWithCoutnry: %s" % institutionWithCoutnry)

        paperIn["country"] = ";".join(countries)
        paperIn["institution"] = ";".join(institutions)
        paperIn["institutionWithCountry"] = ";".join(institutionsWithCoutnry)

      # Get email host
      if paperIn["emailHost"] == "":
        splited1 = paperIn["correspondenceAddress"].split("@")
        if len(splited1) > 1:
          splited2 = splited1[1].split(";")
          paperIn["emailHost"] = splited2[0]
        else:
          paperIn["emailHost"] = "No email"

      # Both keywords
      if paperIn["bothKeywords"] == "":
        bothKeywords = []
        for keyword in paperIn["authorKeywords"].split(";"):
          keywordStriped = keyword.strip()
          if keywordStriped == "":
            continue
          if keywordStriped.upper() not in [x.upper() for x in bothKeywords]:
            bothKeywords.append(keywordStriped)

        for keyword in paperIn["indexKeywords"].split(";"):
          keywordStriped = keyword.strip()
          if keywordStriped == "":
            continue
          if keywordStriped.upper() not in [x.upper() for x in bothKeywords]:
            bothKeywords.append(keywordStriped)
        paperIn["bothKeywords"] = ";".join(bothKeywords)

      # printPaper(paperIn)

      globalVar.loadedPapers += 1

      # Filter papers that are not in document tipe list
      if any(pType.upper() in paperIn["documentType"].upper().split("; ") \
             for pType in globalVar.INCLUDED_TYPES):
        papersDict.append(paperIn)
        if paperIn["dataBase"] == "WoS":
          globalVar.papersWoS += 1
        if paperIn["dataBase"] == "Scopus":
          globalVar.papersScopus += 1


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
  print('Authors: %s' % (paper["author"]))
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
  noAuthors = 0

  # Remove part of the title inside parentisis or square brakets
  # Some journals put this the original language tile in the brakets
  # Remove whitespace at the end and start of the tile
  for paper in paperDict:
    paper["titleB"] = unidecode.unidecode(paper["title"])
    paper["titleB"] = re.sub("[\(\[].*?[\)\]]", "", paper["titleB"].upper()).strip()
    paper["titleB"] = re.sub("[^a-zA-Z0-9]+", "",  paper["titleB"])

    paper["firstAuthorLastName"] = unidecode.unidecode(paper["author"])
    paper["firstAuthorLastName"] = re.sub(";|\.|,", " ", paper["firstAuthorLastName"]).split(" ")[0]
    paper["firstAuthorLastName"] = re.sub("[^a-zA-Z]+", "", paper["firstAuthorLastName"])


  # Short by database, to put WoS first over Scopus, reverse True
  paperDict = sorted(paperDict, key=lambda x: x["dataBase"], reverse=True)
  paperDict = sorted(paperDict, key=lambda x: x["titleB"])
 
  print("Removing duplicates...")

  countMatch2 = 0
  # Run on paper list
  for i in range(0, len(paperDict)):
    match = True
    while(match):

      # If we are on the last paper in the list
      if i >= (len(paperDict) - 1):
        match = False
        continue

      # Compare first author last name and titleB in uppercase
      match = (paperDict[i]["firstAuthorLastName"] == paperDict[i+1]["firstAuthorLastName"])
      match &=  (paperDict[i]["titleB"] == paperDict[i+1]["titleB"])
      if(paperDict[i]["doi"] != ""):
        match |= (paperDict[i]["doi"] == paperDict[i + 1]["doi"])

      match2 = (paperDict[i]["year"] != paperDict[i + 1]["year"]) & match
      if (match2 == True):
        countMatch2 += 1
        #print(countMatch2)

      # If the criterion match
      if(match == True):
        #print("\nPaper %s duplicated with %s" %  (i, i+1))
        
        #print("Dup A: %s, %s" % (paperDict[i]["title"], paperDict[i]["year"]))
        #print("Authors: %s, Database: %s, Cited by: %s" %
        #(paperDict[i]["author"], paperDict[i]["dataBase"], paperDict[i]["citedBy"]))
        
        #print("Dup B: %s, %s" % (paperDict[i+1]["title"], paperDict[i+1]["year"]))
        #print("Authors: %s, Database: %s, Cited by: %s" %
        #(paperDict[i+1]["author"], paperDict[i+1]["dataBase"], paperDict[i+1]["citedBy"]))

        # Update the removed count
        if paperDict[i+1]["dataBase"] == "WoS":
          removedPapersWoS += 1

        if paperDict[i+1]["dataBase"] == "Scopus":
          removedPapersScopus += 1
          
        #print("Removing: %s" % paperDict[i+1]["dataBase"])

        # Add all duplicated in duplicatedIn
        #paperDict[i]["duplicatedIn"] = ";".join(paperDict[i]["duplicatedIn"].split(";") + [paperDict[i+1]["eid"]])
        #paperDict[i]["duplicatedIn"] += (paperDict[i + 1]["eid"] + ";")
        paperDict[i]["duplicatedIn"].append(paperDict[i + 1]["eid"])

        # Find how many duplicated documents has different cited by
        if int(paperDict[i]["citedBy"]) != int(paperDict[i + 1]["citedBy"]):
          duplicatedWithDifferentCitedBy += 1

        # If the cited by count from the paper to remove is bigger than the cited by count for
        # the paper to keep, set the cited by count with the bigger one
        if int(paperDict[i + 1]["citedBy"]) > int(paperDict[i]["citedBy"]):
          paperDict[i]["citedBy"] = paperDict[i + 1]["citedBy"]

        # Remove paper i + 1
        paperDict.remove(paperDict[i+1])

        # Update progress percentage
        duplicatedPapersCount += 1
        progressPer = float(i) / float(len(paperDict)) * 100
        if progressPer < 100:
          #print("\r%0.1f%%" % progressPer)
          sys.stdout.write("\r%d%%  " % (int(progressPer)))
          sys.stdout.flush()
        continue

  # To avoid by zero division
  if globalVar.papersScopus > 0:
    percentajeRemovedPapersScopus = 100.0*removedPapersScopus/globalVar.papersScopus
  else:
    percentajeRemovedPapersScopus = 0
  if globalVar.papersWoS > 0:
    percentajeRemovedPapersWoS = 100.0 * removedPapersWoS / globalVar.papersWoS
  else:
    percentajeRemovedPapersWoS = 0
  if duplicatedPapersCount > 0:
    percenDuplicatedWithDifferentCitedBy = 100.0*duplicatedWithDifferentCitedBy/duplicatedPapersCount
  else:
    percenDuplicatedWithDifferentCitedBy = 0


  print("\r{0:.0f}%".format(100))
  print("\nDuplicated papers found: %s" % duplicatedPapersCount)
  print("Original papers count: %s" % globalVar.OriginalTotalPapers)
  print("Actual papers count: %s" % len(paperDict))
  print("Removed papers WoS: %s, %.1f %%" %
        (removedPapersWoS, percentajeRemovedPapersWoS))
  print("Removed papers Scopus: %s, %.1f %%" %
        (removedPapersScopus, percentajeRemovedPapersScopus))
  if(duplicatedPapersCount != 0):
    print("Duplicated documents with different cited by: %s, %.1f %%\n" % (duplicatedWithDifferentCitedBy,
                                                                           percenDuplicatedWithDifferentCitedBy))

  logWriter.writerow({'Info': ''})
  logWriter.writerow({'Info': 'Duplication removal statics'})

  logWriter.writerow({'Info': 'Total duplicated papers found',
                      'Number':("%d" % (duplicatedPapersCount)),
                      'Percentage': ("%.1f%%" % (100.0 * duplicatedPapersCount / globalVar.OriginalTotalPapers))})

  logWriter.writerow({'Info': 'Removed duplicated papers from WoS',
                      'Number':("%d" % (removedPapersWoS)),
                      'Percentage': ("%.1f%%" % (percentajeRemovedPapersWoS))})

  logWriter.writerow({'Info': 'Removed duplicated papers from Scopus',
                      'Number':("%d" % (removedPapersScopus)),
                      'Percentage': ("%.1f%%" % (percentajeRemovedPapersScopus))})

  logWriter.writerow({'Info': 'Duplicated documents with different cited by',
                      'Number':("%d" % (duplicatedWithDifferentCitedBy)),
                      'Percentage': ("%.1f%%" % (percenDuplicatedWithDifferentCitedBy))})

  globalVar.totalAfterRemDupl = len(paperDict)
  logWriter.writerow({'Info': 'Total papers after rem. dupl.', 'Number': str(globalVar.totalAfterRemDupl)})

  return paperDict


def sourcesStatics(paperDict, logWriter):
  statics = {}

  totalPapers = len(paperDict)

  statics["WoS"] = {}
  for typeIn in globalVar.INCLUDED_TYPES:
    statics["WoS"][typeIn] = 0
  statics["WoS"]["Total"] = 0
  statics["WoS"]["Source"] = "WoS"

  statics["Scopus"]={}
  for typeIn in globalVar.INCLUDED_TYPES:
    statics["Scopus"][typeIn] = 0
  statics["Scopus"]["Total"] = 0
  statics["Scopus"]["Source"] = "Scopus"


  noDocumentTypeCount = 0

  # On each paper to count statics
  for paper in paperDict:
    try:
      statics[paper["dataBase"]][paper["documentType"].split("; ")[0]] += 1
      statics[paper["dataBase"]]["Total"] += 1

    except:
      noDocumentTypeCount += 1

  # Put the percentajes
  for key1, value1 in statics.items():
    for key2, value2 in statics[key1].items():
      if type(statics[key1][key2]) == int:
        statics[key1][key2] = ("%d, %.1f%%" % (statics[key1][key2], (100.0 * statics[key1][key2]/totalPapers)))

  logWriter.writerow(statics["WoS"])
  logWriter.writerow(statics["Scopus"])






  


