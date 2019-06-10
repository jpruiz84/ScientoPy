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
from PIL import Image
import argparse

parser = argparse.ArgumentParser(description="Analyze the topics inside a criterion")

validCriterion = ["author", "sourceTitle",  "subject", "authorKeywords", "indexKeywords", "abstract", 
                  "bothKeywords", "documentType", "dataBase", "country", "institution", "institutionWithCountry"]

validGraphs = ["bar", "bar_trends", "time_line", "evolution", "word_cloud"]

parser.add_argument("-c","--criterion", choices = validCriterion, default= "authorKeywords",
help="Select the criterion to analyze the topics")

parser.add_argument("-g","--graphType", choices = validGraphs, default= "bar_trends",
help="Select the graph type to plot")

parser.add_argument("-l", "--length", type=int, default=10, help="Length of the top topics to analyze, default 10")

parser.add_argument("-s", "--start", type=int, default=0,  help="To filter the \
first top elements. Ex: to filter the first 2 elements on the list use -s 2")

parser.add_argument("-t", "--topics", help='Specific topics to analyze according to critera,\n\r'
                                           'group topics with "," and divide the topics with ";" \n\r'
                                           'Ex: authorKeywords -t "internet of things, iot; bluetooth" \n\r'
                                           'asterisk wildcard ex: authorKeywords -t "device*"')

parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,
                    help="Start year to limit the search, default: " + str(globalVar.DEFAULT_START_YEAR))
parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,
                    help="End year year to limit the search, default: " + str(globalVar.DEFAULT_END_YEAR))

parser.add_argument("--savePlot", default="",  help='Save plot to a file. Ex: --savePlot "topKeywords.eps"')

parser.add_argument("--pYear", 
help="To present the results in percentage per year instead of documents per year", action="store_true")

parser.add_argument("--yLog", 
help="Plot Y axes in log scale", action="store_true")

parser.add_argument("--noPlot",
help="Do not plot the results, use for large amount of topics", action="store_true")

parser.add_argument("--agrForGraph",
help="To use average growth rate (AGR) instead average documents per year (ADY) in parametric and parametric 2 graphs",
                    action="store_true")

parser.add_argument("--wordCloud",
help="Graph the topics word cloud", action="store_true")

parser.add_argument("--wordCloudMask", default="",  help='PNG mask image to use for wordCloud')

parser.add_argument("--windowWidth",
help="Window width in years for average growth rate and average documents per year, minimum 1",
                    type=int, default=2)

parser.add_argument("-r", "--previousResults",
help="Analyze based on the previous results", action="store_true")

parser.add_argument("--onlyFirst",
help="Only look in the first elemet of the topic, for example to analyze only the first author name, "
     "country or institution", action="store_true")

parser.add_argument("--graphTitle",
help="To put a title in the output graph", type=str)

parser.add_argument("--plotWidth", type=int, default=globalVar.DEFAULT_PLOT_WIDTH,
                    help="Set the plot width size in inches, default: " + str(globalVar.DEFAULT_PLOT_WIDTH))

parser.add_argument("--plotHeight", type=int, default=globalVar.DEFAULT_PLOT_HEIGHT,
                    help="Set the plot heigth size in inches, default: " + str(globalVar.DEFAULT_PLOT_HEIGHT))

parser.add_argument("--trend",
help="Get and graph the top trending topics, with the highest average growth rate", action="store_true")

parser.add_argument("-f", "--filter", help='Filter to be applied on a sub topic.'
  'Example to extract instituions from United States: scientoPy.py institutionWithCountry -f "United States"')


parser.add_argument("--intermediateFolder", default="",  help='Custom folder for input and output subfolders')

# ************************* Program start ********************************************************
# ************************************************************************************************

print("\n\nScientoPy: %s" % (globalVar.SCIENTOPY_VERSION))
print("================\n")

# Check python version
if sys.version_info[0] < 3:
  print("ERROR, you are using Python 2, Python 3.X.X required")
  print("")
  exit()

# Parse arguments
args = parser.parse_args()

# Validate window Width
if args.windowWidth < 1:
  print("ERROR: minimum windowWidth 1")
  exit()

# Validate start and end years
if args.startYear > args.endYear:
  print("ERROR: startYear > endYear")
  exit()

# Create output folders if not exist
if not os.path.exists(os.path.join(args.intermediateFolder, globalVar.GRAPHS_OUT_FOLDER)):
    os.makedirs(os.path.join(args.intermediateFolder, globalVar.GRAPHS_OUT_FOLDER))
if not os.path.exists(os.path.join(args.intermediateFolder, globalVar.RESULTS_FOLDER)):
    os.makedirs(os.path.join(args.intermediateFolder, globalVar.RESULTS_FOLDER))

# Select the input file
if args.previousResults:
  INPUT_FILE = os.path.join(args.intermediateFolder, globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_NAME)
else:
  INPUT_FILE = os.path.join(args.intermediateFolder, globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME)

# Start the list empty
papersDict = []
papersDictOut = []
topicList = []

# Open the storage database and add to papersDict
if not os.path.isfile(INPUT_FILE):
  print("ERROR: %s file not found" % INPUT_FILE)
  print("Make sure that you have run the preprocess step before run scientoPy")
  exit()

ifile = open(INPUT_FILE, "r", encoding='utf-8')
print("Reading file: %s" % (INPUT_FILE))
paperUtils.openFileToDict(ifile, papersDict)
ifile.close()

print("Scopus papers: %s" % globalVar.papersScopus)
print("WoS papers: %s" % globalVar.papersWoS)
print("Omited papers: %s" % globalVar.omitedPapers)
print("Total papers: %s" % len(papersDict))

# Create a yearArray
yearArray = range(args.startYear, args.endYear + 1)
yearPapers = {}
for i in range(args.startYear, args.endYear + 1):
  yearPapers[i] = 0

# Filter papers with invalid year
papersDict = list(filter(lambda x: x["year"].isdigit(), papersDict))
# Filter the papers outside the year range
papersDict = list(filter(lambda x: int(x["year"]) >= args.startYear, papersDict))
papersDict = list(filter(lambda x: int(x["year"]) <= args.endYear, papersDict))

print("Total papers in range (%s - %s): %s" %
      (args.startYear, args.endYear , len(papersDict)))

# If no papers in the range exit
if(len(papersDict) == 0):
  print("ERROR: no papers found in the range.")
  exit()

# Find the number of total papers per year
for paper in papersDict:
  if int(paper["year"]) in yearPapers.keys():
    yearPapers[int(paper["year"])] += 1


# Get the filter options
filterSubTopic = ""
if args.filter:
  filterSubTopic = args.filter.strip()
  print("Filter Sub Topic: %s" % filterSubTopic)

# Parse custom topics
if args.topics:
  print("Custom topics entered:")

  # Divide the topics by ;
  topicsFirst = args.topics.split(";")

  for x in topicsFirst:
    topicList.append(x.split(","))

  # Remove begining and ending space from topics
  for topic in topicList:
    for idx,item in enumerate(topic):
      topic[idx] = item.strip()

  # Remove for each sub topic, start and end spaces
  for item1 in topicList:
    for item2 in item1:
      item2 = item2.strip()

  for topic in topicList:
    print(topic)

# Find the top topics
else:
  print("Finding the top topics...")

  topicDic = {}

  # For each paper, get the full topicDic
  for paper in papersDict:

    # For each item in paper criteria
    for item in paper[args.criterion].split(";"):
      # Strip paper item and upper case
      item = item.strip()
      item = item.upper()

      # If paper item empty continue
      if item == "":
        continue

      # If filter sub topic, omit items outside that do not match with the subtopic
      if filterSubTopic != "" and len(item.split(",")) >= 2:
        if(item.split(",")[1].strip().upper() != filterSubTopic.upper()):
          continue

      # If topic already in topicDic
      if item in topicDic:
        topicDic[item] += 1
      # If topic is not in topicDic, create this in topicDic
      else:
        topicDic[item] = 1

      # If onlyFirst, only keep the firt processesing
      if args.onlyFirst:
        break

  # If trending analysis, the top topic list to analyse is bigger
  if args.trend:
    topicListLength = globalVar.TOP_TREND_SIZE
    startList = 0
  else:
    topicListLength = args.length
    startList = args.start

  # Get the top topics by the topDic count
  topTopcis = sorted(topicDic.items(),
                     key=lambda x: -x[1])[startList:(startList + topicListLength)]

  # Put the topTopics in topic List
  for topic in topTopcis:
    topicList.append([topic[0]])

  if len(topicList) == 0:
    print("\nFINISHED : There is not results with your inputs criteria or filter")
    exit()

# print("Topic list:")
# print(topicList)

# Create a dictonary in topicResults list per element in topicList
topicResults = []
for topics in topicList:
  topicItem = {}
  topicItem["upperName"] = topics[0].upper()
  # If the topic name was given as an argument, use the first one given, else keep empty to use the first one found
  if args.topics:
    topicItem["name"] = topics[0]
  else:
    topicItem["name"] = ""
  topicItem["allTopics"] = topics
  topicItem["year"] = yearArray
  topicItem["PapersCount"] = [0] * len(yearArray)
  topicItem["PapersCountAccum"] = [0] * len(yearArray)
  topicItem["PapersCountRate"] = [0] * len(yearArray)
  topicItem["PapersTotal"] = 0
  topicItem["AverageDocPerYear"] = 0      # ADY
  topicItem["PapersInLastYears"] = 0
  topicItem["PerInLastYears"] = 0         #PDLY
  topicItem["CitedByCount"] = [0] * len(yearArray)
  topicItem["CitedByCountAccum"] = [0] * len(yearArray)
  topicItem["CitedByTotal"] = 0
  topicItem["papers"] = []
  topicItem["topicsFound"] = []
  topicItem["hIndex"] = 0
  topicItem["agr"] = 0                  # Average growth rate
  topicResults.append(topicItem)

# Find papers within the arguments, and fill the topicResults fields per year.
print("Calculating papers sum...")
# For each paper
for paper in papersDict:
  # For each item in paper criteria
  for item in paper[args.criterion].split(";"):
    # Strip paper item and upper
    item = item.strip()
    itemUp = item.upper()

    # For each topic in topic results
    for topicItem in topicResults:
      # for each sub topic
      for subTopic in topicItem["allTopics"]:

        # Check if the sub topic match with the paper item
        if args.topics and "*" in subTopic.upper():
          subTopicRegex = subTopic.upper().replace("*", ".*")
          p = re.compile(subTopicRegex)
          match = p.match(itemUp)
        else:
          match = subTopic.upper() == itemUp

        # If match, sum it to the topicItem
        if match:
          yearIndex = topicItem["year"].index(int(paper["year"]))
          topicItem["PapersCount"][yearIndex] += 1
          topicItem["PapersTotal"] += 1
          topicItem["CitedByCount"][yearIndex] += int(paper["citedBy"])
          topicItem["CitedByTotal"] += int(paper["citedBy"])
          # If no name in the topicItem, put the first one that was found
          if topicItem["name"] == "":
            topicItem["name"] = item
          topicItem["papers"].append(paper)
          # Add the matched paper to the papersDictOut
          papersDictOut.append(paper)

          # If it is a new topic, add it to topicItem["topicsFound"]
          if itemUp not in [x.upper() for x in topicItem["topicsFound"]]:
            topicItem["topicsFound"].append(item)
    # Only process one (the first one) if args.onlyFirst
    if args.onlyFirst:
      break

# Print the topics found if the asterisk willcard was used
for topicItem in topicResults:
  for subTopic in topicItem["allTopics"]:
    if args.topics and "*" in subTopic.upper():
      print("\nTopics found for %s:" % subTopic)
      print('"' + ';'.join(topicItem["topicsFound"]) + '"')
      print("")


print("Calculating accumulative ...")
# Extract accumulative
for topicItem in topicResults:
  citedAccumValue = 0
  papersAccumValue = 0
  for i in range(0,len(topicItem["CitedByCountAccum"])):
    citedAccumValue += topicItem["CitedByCount"][i]
    topicItem["CitedByCountAccum"][i] = citedAccumValue

    papersAccumValue += topicItem["PapersCount"][i]
    topicItem["PapersCountAccum"][i] = papersAccumValue


print("Calculating Average Growth Rate (AGR)...")
# Extract the Average Growth Rate (AGR)
for topicItem in topicResults:
  # Calculate rates
  pastCount = 0
  # Per year with papers count data
  for i in range(0, len(topicItem["PapersCount"])):
    topicItem["PapersCountRate"][i] = topicItem["PapersCount"][i] - pastCount
    pastCount = topicItem["PapersCount"][i]

  # Calculate AGR from rates
  endYearIndex = len(topicItem["year"]) - 1
  startYearIndex = endYearIndex - (args.windowWidth - 1)

  topicItem["agr"] = \
    round(np.mean(topicItem["PapersCountRate"][startYearIndex : endYearIndex + 1]), 1)

print("Calculating Average Documents per Year (ADY)...")
# Extract the Average Documents per Year (ADY)
for topicItem in topicResults:

  # Calculate ADY from rates
  endYearIndex = len(topicItem["year"]) - 1
  startYearIndex = endYearIndex - (args.windowWidth - 1)

  topicItem["AverageDocPerYear"] = \
    round(np.mean(topicItem["PapersCount"][startYearIndex : endYearIndex + 1]), 1)

  topicItem["PapersInLastYears"] = \
    np.sum(topicItem["PapersCount"][startYearIndex : endYearIndex + 1])

  if topicItem["PapersTotal"] > 0:
    topicItem["PerInLastYears"] = \
      round(100 * topicItem["PapersInLastYears"] / topicItem["PapersTotal"], 1)

# Scale in percentage per year
if args.pYear:
  for topicItem in topicResults:
    for year, value in yearPapers.items():
      index = topicItem["year"].index(year)
      if value != 0:
        topicItem["PapersCount"][index] /= (float(value)/100.0)

print("Calculating h-index...")
# Calculate h index per topic
for topicItem in topicResults:

  #print("\n" + topicName)

  # Sort papers by cited by count
  papersIn = topicItem["papers"]
  papersIn = sorted(papersIn, key=lambda x: int(x["citedBy"]), reverse = True)

  count = 1
  hIndex = 0
  for paper in papersIn:
    #print(str(count) + ". " + paper["citedBy"])
    if int(paper["citedBy"]) >= count:
      hIndex = count
    count += 1
    #print("hIndex: " + str(hIndex))
    topicItem["hIndex"] = hIndex


# Sort by PapersTotal, and then by name.
topicResults = sorted(topicResults, key=lambda x: x["name"], reverse=False)
topicResults = sorted(topicResults, key=lambda x: int(x["PapersTotal"]), reverse=True)

# If trend analysis, sort by agr, and get the first ones
if args.trend:
  topicResults = sorted(topicResults, key=lambda x: int(x["agr"]), reverse=True)
  topicResults = topicResults[args.start:(args.start + args.length)]

# Print top topics
print("\nTop topics:")
print("Average Growth Rate (AGR) and Average Documents per Year (ADY) period: %d - %d\n\r"
      % (yearArray[startYearIndex], yearArray[endYearIndex]))
print('-' * 87)
print("{:<4s}{:<30s}{:>10s}{:>10s}{:>10s}{:>10s}{:>12s}".format("Pos", args.criterion, "Total", "AGR", "ADY", "PDLY", "h-index"))
print('-' * 87)
count = 0
for topicItem in topicResults:
  print("{:<4d}{:<30s}{:>10d}{:>10.1f}{:>10.1f}{:>10.1f}{:>10d}".format(
    count + 1, topicItem["name"], topicItem["PapersTotal"], topicItem["agr"],
         topicItem["AverageDocPerYear"], topicItem["PerInLastYears"], topicItem["hIndex"]))
  count += 1
print('-' * 87)
print("")

if filterSubTopic != "":
  for topicItem in topicResults:
    topicItem["name"] = topicItem["name"].split(",")[0].strip()

# If more than 100 results and not wordCloud, no plot.
if len(topicResults) > 100 and not args.graphType == "word_cloud" and not args.noPlot:
  args.noPlot = True
  print("\nERROR: Not allowed to graph more than 100 results")

# Plot
if not args.noPlot:
  if args.graphType == "evolution":
    graphUtils.plot_evolution(plt, topicResults, yearArray[startYearIndex], yearArray[endYearIndex], args)

  if args.graphType == "word_cloud":
    from wordcloud import WordCloud
    my_dpi = 96
    plt.figure(figsize=(1960/my_dpi, 1080/my_dpi), dpi=my_dpi)

    if args.wordCloudMask:
      imageMask = np.array(Image.open(args.wordCloudMask))
      wc = WordCloud(background_color="white", max_words=5000, width=1960, height=1080, colormap="tab10",
                     mask=imageMask)
    else:
      wc = WordCloud(background_color="white", max_words=5000, width=1960, height=1080, colormap="tab10")

    freq = {}
    for topicItem in topicResults:
      freq[topicItem["name"]] = topicItem["PapersTotal"]
    # generate word cloud
    wc.generate_from_frequencies(freq)

    # show
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")

  if args.graphType == "bar":
    graphUtils.plot_bar_horizontal(plt, topicResults, args)

  if args.graphType == "bar_trends":
    graphUtils.plot_bar_horizontal_trends(plt, topicResults,
                                          yearArray[startYearIndex], yearArray[endYearIndex], args)
  if args.graphType == "time_line":
    graphUtils.plot_time_line(plt, topicResults, False)
    fig = plt.gcf()
    fig.set_size_inches(args.plotWidth, args.plotHeight)

    if args.yLog:
      plt.yscale('log')
      #TODO: Fix mticker
      #plt.gca().yaxis.set_minor_formatter(mticker.ScalarFormatter())

    if args.pYear:
      plt.ylabel("% of documents per year")

  if args.graphTitle:
    #plt.title(args.graphTitle)
    fig = plt.gcf()
    fig.suptitle(args.graphTitle, y=1.0)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
  else:
    plt.tight_layout()

  if args.savePlot == "":
    plt.show()
  else:
    plt.savefig(os.path.join(args.intermediateFolder, globalVar.GRAPHS_OUT_FOLDER, args.savePlot),
    bbox_inches = 'tight', pad_inches = 0.01)
    print("Plot saved on: " + os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot))


paperSave.saveTopResults(topicResults, args.criterion, args.intermediateFolder)
paperSave.saveExtendedResults(topicResults, args.criterion, args.intermediateFolder)

# Only save results if that is result of a not previous result
if not args.previousResults:
  paperSave.saveResults(papersDictOut, os.path.join(args.intermediateFolder, globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_NAME))
