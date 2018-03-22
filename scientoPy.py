import paperUtils
import paperSave
import globalVar
import os
import matplotlib.pyplot as plt
import numpy as np
import graphUtils
import sys
from wordcloud import WordCloud



import argparse
parser = argparse.ArgumentParser(description="Analyze the topics inside a criterion")

parser.add_argument("criterion", choices=["authors", "source",  "subject",
"authorKeywords", "indexKeywords", "documentType", "dataBase", "country", "emailHost", "institution"],
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


parser.add_argument("--useCitedBy",
help="Short the top results based on times cited", action="store_true")

parser.add_argument("--agrWidth",
help="Average growth rate window width in years",type=int, default=2)

parser.add_argument("-r", "--previousResults",
help="Analyze based on the previous results", action="store_true")

parser.add_argument("--onlyFirst",
help="Only look on the first topic, for example to analize only the first aurhor name, "
     "country or institution", action="store_true")

parser.add_argument("--title",
help="To put a title in your graph", type=str)




# Program start ********************************************************
print("\n\nScientoPy: %s" % (globalVar.SCIENTOPY_VERSION))
print("================\n")

if sys.version_info[0] > 2:
  print("ERROR, you are using Python 3, Python 2.7.XX required")
  print("")
  exit()

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

# Open the storage database and add to papersDict
ifile = open(INPUT_FILE, "r")
print("Reading file: %s" % (INPUT_FILE))
paperUtils.analyzeFileDict(ifile, papersDict)
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

# Find the number of total papers per year
for paper in papersDict:
  if int(paper["year"]) in yearPapers.keys():
    yearPapers[int(paper["year"])] += 1

topicList = []
# Parse custom topics
if args.topics:
  print("Custom topics entered:")

  # Divide the topics by ;
  topicsFirst = args.topics.split(";")

  for x in topicsFirst:
    topicList.append(x.split(","))

  # Remove begining space from topics
  for topic in topicList:
    for idx,item in enumerate(topic):
      topic[idx] = item.strip()

  # Remove for each sub topic, start and end spaces
  for item1 in topicList:
    for item2 in item1:
      item2 = item2.strip()

# Find the top topics
else:
  print("Finding the top topics...")

  topicDic = {}
  # Find papers within the arguments
  # run on papersDict
  for paper in papersDict:
    for item in paper[args.criterion].split(";"):
      item = item.strip()
      item = item.upper()
      if item == "":
        continue
      try:
        if item in topicDic:
          if not args.useCitedBy:
            topicDic[item] += 1
          else:
            topicDic[item] += int(paper["citedBy"])
        else:
          if not args.useCitedBy:
            topicDic[item] = 1
          else:
            topicDic[item] = int(paper["citedBy"])
      except:
        noWithCitedBy = 1
      if args.onlyFirst:
        break

  topTopcis = sorted(topicDic.iteritems(),
                     key=lambda x: -x[1])[int(args.start):int(args.length)]

  for topic in topTopcis:
    topicList.append([topic[0]])

print(topicList)

# Create results data dictionary and init fields
topicResults = {}
for topics in topicList:
  topicName = topics[0].upper()
  topicResults[topicName] = {}
  topicResults[topicName]["year"] = yearArray
  topicResults[topicName]["PapersCount"] = [0] * len(yearArray)
  topicResults[topicName]["PapersCountAccum"] = [0] * len(yearArray)
  topicResults[topicName]["PapersCountRate"] = [0] * len(yearArray)
  topicResults[topicName]["PapersTotal"] = 0
  topicResults[topicName]["CitedByCount"] = [0] * len(yearArray)
  topicResults[topicName]["CitedByCountAccum"] = [0] * len(yearArray)
  topicResults[topicName]["CitedByTotal"] = 0
  topicResults[topicName]["name"] = topics[0]
  topicResults[topicName]["papers"] = []
  topicResults[topicName]["hIndex"] = 0
  topicResults[topicName]["agr"] = 0
#print(topicResults)

# Find papers within the arguments, and fill the topicResults fileds per year.
# run on papersDict
for paper in papersDict:
  # run on criterin sub fields
  for item in paper[args.criterion].split(";"):
    item = item.strip()
    itemUp = item.upper()

    # run in topicList to fill topicResults
    for topics in topicList:
      for topic in topics:
        if topic.upper() == itemUp:
          topicName = topics[0].upper()
          yearIndex = topicResults[topicName]["year"].index(int(paper["year"]))
          topicResults[topicName]["PapersCount"][yearIndex] += 1
          topicResults[topicName]["PapersTotal"] += 1
          topicResults[topicName]["CitedByCount"][yearIndex] += int(paper["citedBy"])
          topicResults[topicName]["CitedByTotal"] += int(paper["citedBy"])
          topicResults[topicName]["name"] = item
          topicResults[topicName]["papers"].append(paper)
          papersDictOut.append(paper)
    if args.onlyFirst:
      break

#print(topicResults)


# Extract the Average Growth Rate (AGR)
for topic in topicList:
  topicName = topic[0].upper()
  citedAccumValue = 0
  papersAccumValue = 0

  # Calculate rates
  pastCount = 0
  for i in range(0, len(topicResults[topicName]["PapersCount"])):
    topicResults[topicName]["PapersCountRate"][i] = topicResults[topicName]["PapersCount"][i] - pastCount
    pastCount = topicResults[topicName]["PapersCount"][i]

  # Calculate AGR from rates
  endYearIndex = len(topicResults[topicName]["year"]) - 1
  startYearIndex = endYearIndex - args.agrWidth

  topicResults[topicName]["agr"] = \
    np.mean(topicResults[topicName]["PapersCountRate"][startYearIndex : endYearIndex + 1])

# Extract accumulative
for topic in topicList:
  topicName = topic[0].upper()
  citedAccumValue = 0
  papersAccumValue = 0
  for i in range(0,len(topicResults[topicName]["CitedByCountAccum"])):
    citedAccumValue += topicResults[topicName]["CitedByCount"][i]
    topicResults[topicName]["CitedByCountAccum"][i] = citedAccumValue

    papersAccumValue += topicResults[topicName]["PapersCount"][i]
    topicResults[topicName]["PapersCountAccum"][i] = papersAccumValue

# Scale in percentage per year
if args.pYear:
  for topics in topicList:
    for year, value in yearPapers.iteritems():
      index = topicResults[topics[0].upper()]["year"].index(year)
      if value != 0:
        topicResults[topics[0].upper()]["PapersCount"][index] /= (float(value)/100.0)


# Calculate h index per topic
for topic in topicList:
  topicName = topic[0].upper()
  #print("\n" + topicName)

  # Sort papers by cited by count
  papersIn = topicResults[topicName]["papers"]
  papersIn = sorted(papersIn, key=lambda x: int(x["citedBy"]), reverse = True)

  count = 1
  hIndex = 0
  for paper in papersIn:
    #print(str(count) + ". " + paper["citedBy"])
    if int(paper["citedBy"]) >= count:
      hIndex = count
    count += 1
    #print("hIndex: " + str(hIndex))
    topicResults[topicName]["hIndex"] = hIndex

# Print top topics
print("\nTop topics:")
print("Pos. " + args.criterion + ", Total, AGR, h-index")
count = 0
for topic in topicList:
  print("%s. %s:, %d, %.1f, %d" % (count + 1,
  topicResults[topic[0].upper()]["name"], topicResults[topic[0].upper()]["PapersTotal"],
                                       topicResults[topic[0].upper()]["agr"],
                            topicResults[topic[0].upper()]["hIndex"]))
  count += 1

# Plot
if args.noPlot:

  if args.parametric:

    graphUtils.plot_parametric(plt, topicResults, topicList, yearArray[startYearIndex], yearArray[endYearIndex])
    if args.yLog:
      plt.yscale('log')

  elif args.wordCloud:
    my_dpi = 96
    plt.figure(figsize=(1960/my_dpi, 1080/my_dpi), dpi=my_dpi)
    
    wc = WordCloud(background_color="white", max_words=1000, width = 1960, height = 1080 , colormap = "Paired")
    freq = {}
    for topic in topicList:
      freq[topicResults[topic[0].upper()]["name"]] = topicResults[topic[0].upper()]["PapersTotal"]
    # generate word cloud
    wc.generate_from_frequencies(freq)

    # show
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
  else:
    count = 0
    legendArray=[]
    for topics in topicList:
      legendArray.append(topicResults[topics[0].upper()]["name"])

      plt.plot(topicResults[topics[0].upper()]["year"], topicResults[topics[0].upper()]["PapersCount"],
      linewidth=1.2, marker=globalVar.MARKERS[count], markersize=10,
      zorder=(len(topicList) - count), color=globalVar.COLORS[count],markeredgewidth=0.0)

      count += 1

    plt.legend(legendArray, loc = 2)
    plt.xlabel("Publication year")
    plt.ylabel("Number of documents")

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


paperSave.saveTopResults(topicResults, args.criterion)
paperSave.saveExtendedResults(topicResults, args.criterion)

# Only save results if that is result of a not previous result
if not args.previousResults:
  paperSave.saveResults(papersDictOut, os.path.join(globalVar.RESULTS_FOLDER, globalVar.OUTPUT_FILE_NAME))



