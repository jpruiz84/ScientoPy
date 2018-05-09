import paperUtils
import paperSave
import globalVar
import os
import matplotlib.pyplot as plt
import numpy as np
import graphUtils
import sys
import re


import argparse
parser = argparse.ArgumentParser(description="Analyze the topics inside a criterion")

validCriterion = ["author", "sourceTitle",  "subject", "authorKeywords", "indexKeywords",
                  "bothKeywords", "documentType", "dataBase", "country", "institution", "institutionWithCountry"]

parser.add_argument("criterion", choices = validCriterion,
help="Select the criterion to analyze the topics")

parser.add_argument("-l", "--length", type=int, default=10, help="Length of the top topics to present, default 10")

parser.add_argument("-s", "--start", type=int, default=0,  help="To filter the \
first elements, ex to filter the first 2 elements on the list use -s 2")

parser.add_argument("-t", "--topics", help='Topics to analyze according to critera, '
                                           'ex: authorKeywords -t "internet of things,iot;bluetooth" ')

parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,  help="Start year to limit the search")
parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,  help="End year year to limit the search")

parser.add_argument("--savePlot", default="",  help='Save plot to a file, ex: --savePlot "topKeywords.eps"')

parser.add_argument("--pYear", 
help="To present the results in percentage per year", action="store_true")

parser.add_argument("--yLog", 
help="Plot with Y axes on log scale", action="store_true")

parser.add_argument("--noPlot",
help="Do not plot the results, use for large amount of topics", action="store_false")

parser.add_argument("--parametric",
help="Graph on Y the number of publications, and on X accomulative number of citations", action="store_true")

parser.add_argument("--wordCloud",
help="Graph the topics word cloud", action="store_true")

parser.add_argument("--bar",
help="Graph the topics in horizontal bar", action="store_true")


parser.add_argument("--useCitedBy",
help="Short the top results based on times cited", action="store_true")

parser.add_argument("--agrWidth",
help="Average growth rate window width in years",type=int, default=1)

parser.add_argument("-r", "--previousResults",
help="Analyze based on the previous results", action="store_true")

parser.add_argument("--onlyFirst",
help="Only look on the first topic, for example to analize only the first aurhor name, "
     "country or institution", action="store_true")

parser.add_argument("--title",
help="To put a title in your graph", type=str)

parser.add_argument("--trend",
help="Get the top trending topics, with the highest last AGR", action="store_true")

parser.add_argument("-f", "--filter", help='Filter to be aplied on a sub topic.'
  'Example to extract instituions from United States: scientoPy.py institutionWithCountry -f "United States"')



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

# Create output folders if not exist
if not os.path.exists(globalVar.GRAPHS_OUT_FOLDER):
    os.makedirs(globalVar.GRAPHS_OUT_FOLDER)
if not os.path.exists(globalVar.RESULTS_FOLDER):
    os.makedirs(globalVar.RESULTS_FOLDER)

# Select the input file
if args.previousResults:
  INPUT_FILE = os.path.join(globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_NAME)
else:
  INPUT_FILE = os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_NAME)

# Start paper list empty
papersDict = []
papersDictOut = []
topicList = []

# Open the storage database and add to papersDict
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

if(len(papersDict) == 0):
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

  # For each paper
  for paper in papersDict:
    # For each item in paper critera
    for item in paper[args.criterion].split(";"):
      # Strip paper item and upper
      item = item.strip()
      item = item.upper()

      # If paper item empty continue
      if item == "":
        continue

      # If filter sub topic, omit items outside that do not match with the subtopic
      if filterSubTopic != "" and len(item.split(",")) >= 2:
        if(item.split(",")[1].strip().upper() != filterSubTopic.upper()):
          continue

      try:
        # If topic already in topicDic
        if item in topicDic:
          if not args.useCitedBy:
            topicDic[item] += 1
          else:
            topicDic[item] += int(paper["citedBy"])
        # If topic is not in topicDic
        else:
          if not args.useCitedBy:
            topicDic[item] = 1
          else:
            topicDic[item] = int(paper["citedBy"])
      # If citedBy has problem converting to int
      except:
        noWithCitedBy = 1
      # If onlyFirst, only keep the firt processesing
      if args.onlyFirst:
        break

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

#print("Topic list:")
#print(topicList)

# Create results data dictionary list and init fields
topicResults = []

# Create a dictonary in topicResults per element in topicList
for topics in topicList:
  topicItem = {}
  topicItem["upperName"] = topics[0].upper()
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
  topicItem["CitedByCount"] = [0] * len(yearArray)
  topicItem["CitedByCountAccum"] = [0] * len(yearArray)
  topicItem["CitedByTotal"] = 0
  topicItem["papers"] = []
  topicItem["topicsFound"] = []
  topicItem["hIndex"] = 0
  topicItem["agr"] = 0
  topicResults.append(topicItem)
#print(topicResults)

# Find papers within the arguments, and fill the topicResults fileds per year.
print("Calcualting papers sum...")
# For each paper
for paper in papersDict:
  # For each item in paper critera
  for item in paper[args.criterion].split(";"):
    # Strip paper item and upper
    item = item.strip()
    itemUp = item.upper()

    for topicItem in topicResults:
      for subTopic in topicItem["allTopics"]:
        if args.topics and "*" in subTopic.upper():
          subTopicRegex = subTopic.upper().replace("*", ".*")
          p = re.compile(subTopicRegex)
          match = p.match(itemUp)
        else:
          match = subTopic.upper() == itemUp

        if match:
          yearIndex = topicItem["year"].index(int(paper["year"]))
          topicItem["PapersCount"][yearIndex] += 1
          topicItem["PapersTotal"] += 1
          topicItem["CitedByCount"][yearIndex] += int(paper["citedBy"])
          topicItem["CitedByTotal"] += int(paper["citedBy"])
          if topicItem["name"] == "":
            topicItem["name"] = item
          topicItem["papers"].append(paper)
          papersDictOut.append(paper)

          if itemUp not in [x.upper() for x in topicItem["topicsFound"]]:
            topicItem["topicsFound"].append(item)
    if args.onlyFirst:
      break

# Print the topics found if the asterisk willcard was used
for topicItem in topicResults:
  for subTopic in topicItem["allTopics"]:
    if args.topics and "*" in subTopic.upper():
      print("\nTopics found for %s:" % subTopic)
      print('"' + ';'.join(topicItem["topicsFound"]) + '"')
      print("")


print("Calculating AGR...")
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
  startYearIndex = endYearIndex - args.agrWidth

  topicItem["agr"] = \
    np.mean(topicItem["PapersCountRate"][startYearIndex : endYearIndex + 1])

print("Calculating accumulatives...")
# Extract accumulative
for topicItem in topicResults:
  citedAccumValue = 0
  papersAccumValue = 0
  for i in range(0,len(topicItem["CitedByCountAccum"])):
    citedAccumValue += topicItem["CitedByCount"][i]
    topicItem["CitedByCountAccum"][i] = citedAccumValue

    papersAccumValue += topicItem["PapersCount"][i]
    topicItem["PapersCountAccum"][i] = papersAccumValue

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


# Sort by PapersTotal, then by hIndex, and then by name.
topicResults = sorted(topicResults, key=lambda x: x["name"], reverse=False)
topicResults = sorted(topicResults, key=lambda x: int(x["hIndex"]), reverse=True)
topicResults = sorted(topicResults, key=lambda x: int(x["PapersTotal"]), reverse=True)

if args.trend:
  topicResults = sorted(topicResults, key=lambda x: int(x["agr"]), reverse=True)
  topicResults =  topicResults[args.start:(args.start+args.length)]

# Print top topics
print("\nTop topics:")
print("Average Growth Rate period: %d - %d" % (yearArray[startYearIndex], yearArray[endYearIndex]))
print("Pos. " + args.criterion + ", Total, AGR, h-index")
count = 0
for topicItem in topicResults:
  print("%s. %s:, %d, %.1f, %d" %
        (count + 1, topicItem["name"], topicItem["PapersTotal"], topicItem["agr"], topicItem["hIndex"]))
  count += 1
print("")

if filterSubTopic != "":
  for topicItem in topicResults:
    topicItem["name"] = topicItem["name"].split(",")[0].strip()

# Plot
if args.noPlot:

  if args.parametric:

    graphUtils.plot_parametric(plt, topicResults, yearArray[startYearIndex], yearArray[endYearIndex])
    if args.yLog:
      plt.yscale('log')

  elif args.wordCloud:
    from wordcloud import WordCloud
    my_dpi = 96
    plt.figure(figsize=(1960/my_dpi, 1080/my_dpi), dpi=my_dpi)
    
    wc = WordCloud(background_color="white", max_words=1000, width = 1960, height = 1080 , colormap = "tab10")
    freq = {}
    for topicItem in topicResults:
      freq[topicItem["name"]] = topicItem["PapersTotal"]
    # generate word cloud
    wc.generate_from_frequencies(freq)

    # show
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
  elif args.bar:
    graphUtils.plot_bar_horizontal(plt, topicResults)

  else:
    graphUtils.plot_time_line(plt, topicResults, False)

    if args.yLog:
      plt.yscale('log')

    if args.pYear:
      plt.ylabel("% of documents per year")

  if args.title:
    plt.title(args.title)

  plt.tight_layout()

  if args.savePlot == "":
    plt.show()
  else:
    plt.savefig(os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot),
    bbox_inches = 'tight', pad_inches = 0.01)
    print("Plot saved on: " + os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot))


paperSave.saveTopResults(topicResults, args.criterion)
paperSave.saveExtendedResults(topicResults, args.criterion)

# Only save results if that is result of a not previous result
if not args.previousResults:
  paperSave.saveResults(papersDictOut, os.path.join(globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_NAME))
