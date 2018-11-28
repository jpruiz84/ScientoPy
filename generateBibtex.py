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

import paperUtils
import paperSave
import globalVar
import os
import matplotlib.pyplot as plt
import numpy as np
import graphUtils
import sys
import re

import sys
import os

filename = sys.argv[1]
fileobject = (open(filename, 'r'))
rawtext = fileobject.read()
fileobject.close()

start = '\\begin{document}'
end = '\\begin{thebibliography}'
bodytext = rawtext[rawtext.find(start)+len(start):rawtext.rfind(end)]


# Extact the cites keys
citesDict = {}
for char in range(0,len(bodytext) - 10):
  if bodytext[char:char+6] == '\\cite{':
    cite = ''
    char += len('\\cite{')
    while (bodytext[char] != '}'):
      if (bodytext[char] == ' '):
        char +=1
      elif(bodytext[char] == ','):
        char +=1 
        if cite in citesDict.keys():
          cite = ''
        else:
          citesDict[cite] = False
          cite=''
      else:
        cite += (bodytext[char])
        char +=1  
    if cite in citesDict.keys():
      pass
    else:
      citesDict[cite] = False

print("%d cites found." % len(citesDict))
print(citesDict)

# Start paper list empty
papersDict = []
papersToBib = []

# Open the storage database and add to papersDict
INPUT_FILE = os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME)
ifile = open(INPUT_FILE, "r", encoding='utf-8')
print("Reading file: %s" % (INPUT_FILE))
paperUtils.openFileToDict(ifile, papersDict)
ifile.close()
print("Loaded %d docuemnts" % (len(papersDict)))


# Find the number of total papers per year
count = 1
for paper in papersDict:
  #print("%d, %s" % (count, paper["title"]))
  #count += 1
  if paper["eid"] in citesDict.keys():
    if citesDict[paper["eid"]] == False:
      print("Added paper(%s): %s" % (paper["eid"], paper["title"]))
      papersToBib.append(paper)
      citesDict[paper["eid"]] = True


OUT_FILE = os.path.join(globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_BIB)
ofile = open(OUT_FILE, 'w', encoding='utf-8')

for paper in papersToBib:
  authorsNames = paper["authorFull"]
  if paper["dataBase"] == "Scopus":
    authorsNames = authorsNames.replace(",", ";")
    authorsNames = authorsNames.split(";")
    authorsNames = [x.strip() for x in authorsNames]
    authorsNames = [x.replace(" ", ", ") for x in authorsNames]
    authorsNames = " and ".join(authorsNames)

  if paper["dataBase"] == "WoS":
    authorsNames = authorsNames.replace("; ", " and ")

  if(paper["documentType"].split(";")[0] in ["Article", "Review", "Article in Press"]):
    ofile.write('@Article{%s,\n' % paper["eid"])
    ofile.write('  author \t=\t"%s",\n' % authorsNames)
    ofile.write('  title\t\t=\t"%s",\n' % paper["title"].replace("&", "\&"))
    ofile.write('  journal \t=\t"%s",\n' % paper["sourceTitle"].replace("&","\&"))
    ofile.write('  numpages\t=\t"%s",\n' % paper["pageCount"].replace("&","\&"))
    ofile.write('  volume \t=\t"%s",\n' % paper["volume"])
    ofile.write('  number \t=\t"%s",\n' % paper["artNo"])
    ofile.write('  year \t\t=\t"%s",\n' % paper["year"])
    ofile.write('  doi \t\t=\t"%s",\n' % paper["doi"])
    ofile.write('}\n\n\n')

  if (paper["documentType"].split(";")[0] in ["Conference Paper", "Proceedings Paper",]):
    ofile.write('@Inproceedings{%s,\n'% paper["eid"])
    ofile.write('  author \t=\t"%s",\n' % authorsNames)
    ofile.write('  title\t\t=\t"%s",\n' % paper["title"].replace("&","\&"))
    ofile.write('  booktitle \t=\t"%s",\n' % paper["sourceTitle"].replace("&","\&"))
    ofile.write('  publisher \t=\t"%s",\n' % paper["publisher"].replace("&","\&"))
    ofile.write('  numpages\t=\t"%s",\n' % paper["pageCount"])
    ofile.write('  volume \t=\t"%s",\n' % paper["volume"])
    ofile.write('  number \t=\t"%s",\n' % paper["artNo"])
    ofile.write('  year \t\t=\t"%s",\n' % paper["year"])
    ofile.write('  doi \t\t=\t"%s",\n' % paper["doi"])
    ofile.write('}\n\n\n')

print("Total references generated: %d" % len(papersToBib))
ofile.close()


