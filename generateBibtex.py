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
citesList = []
for char in range(0,len(bodytext) - 10):
  if bodytext[char:char+6] == '\\cite{':
    author = ''
    char += len('\\cite{')
    while (bodytext[char] != '}'):
      if (bodytext[char] == ' '):
        char+=1
      elif(bodytext[char] == ','):
        char +=1 
        if author in citesList:
          author = ''
        else:
          citesList.append(author)
          author=''
      else:
        author += (bodytext[char])
        char +=1  
    if author in citesList:
      pass
    else:
      citesList.append(author) 

print(citesList)

# Start paper list empty
papersDict = []
papersToBib = []

# Open the storage database and add to papersDict
#INPUT_FILE = os.path.join(globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_NAME)
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
  if paper["eid"] in citesList:
    print("******* Added paper: %s" % paper["title"])
    papersToBib.append(paper)


OUT_FILE = os.path.join(globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_BIB)
ofile = open(OUT_FILE, 'w', encoding='utf-8')

'''
@Article{Abril07,
  author 	= "Patricia S. Abril and Robert Plant",
  title 	= "The patent holder's dilemma: Buy, sell, or troll?",
  journal = "Communications of the ACM",
  volume 	= "50",
  number 	= "1",
  month 	= jan,
  year 		= "2007",
  pages 	= "36--44",
  doi 		= "10.1145/1188913.1188915",
  note		= "",
}

'''

for paper in papersToBib:
  ofile.write('@Article{%s,\n'% paper["eid"])
  ofile.write('  author \t=\t"%s",\n' % paper["authorFull"].replace("; "," and "))
  ofile.write('  title\t\t=\t"%s",\n' % paper["title"].replace("&","\&"))
  ofile.write('  journal \t=\t"%s",\n' % paper["sourceTitle"])
  ofile.write('  numpages\t=\t"%s",\n' % paper["pageCount"])
  ofile.write('  volume \t=\t"%s",\n' % paper["volume"])
  ofile.write('  number \t=\t"%s",\n' % paper["artNo"])
  ofile.write('  year \t\t=\t"%s",\n' % paper["year"])
  ofile.write('  doi \t\t=\t"%s",\n' % paper["doi"])
  ofile.write('}\n\n\n')

print("Total references generated: %d" % len(papersToBib))
ofile.close()
