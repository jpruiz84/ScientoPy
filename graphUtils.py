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

import numpy as np
import globalVar
from matplotlib.lines import Line2D
from matplotlib import gridspec
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
from scipy import interpolate
from matplotlib.ticker import MaxNLocator
import matplotlib.ticker


def plot_time_line(plt, topicResults, fSecundary):
    count = 0
    ax = plt.gca()
    for topicItem in topicResults:
      x = topicItem["year"]
      y = topicItem["PapersCount"]
      yAcum = topicItem["PapersCountAccum"]
      zero_to_nan2(y, yAcum)

      if not fSecundary:
        plt.plot(x, y,
        linewidth=1.2, marker=globalVar.MARKERS[count], markersize=10, label = topicItem["name"],
        zorder=(len(topicResults) - count), color=globalVar.COLORS_TAB10[count], markeredgewidth=0.0)
      else:
        plt.plot(x, y,
                 linewidth=1.2, marker=globalVar.MARKERS[count], markersize=10, label=topicItem["name"],
                 zorder=(len(topicResults) - count), color=globalVar.COLORS_TAB10[count], markeredgewidth=0.0,
                 linestyle = "--")

      ax.xaxis.set_major_locator(MaxNLocator(integer=True))

      count += 1

    [xmin, xmax] = ax.get_xlim()
    ax.set_xlim([min(x), xmax + (xmax - xmin) * 0.1])

    ax.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

    legend1 = plt.legend(loc = "best", fancybox= "false")
    legend1.get_frame().set_alpha(1)
    legend1.set_zorder(count)  # put the legend on top
    plt.xlabel("Publication year")
    plt.ylabel("Number of documents")

def plot_bar_horizontal(plt, topicResults, args):
  ax = plt.gca()
  itemsName = []
  x = []
  for topicItem in topicResults:
    x.append(topicItem["PapersTotal"])
    itemsName.append(topicItem["name"])

  y_pos = np.arange(len(itemsName))[::-1]

  plt.barh(y_pos, x, 0.6, align='center', color=globalVar.COLORS_TAB20[0], edgecolor="black", linewidth=0.5)
  plt.yticks(y_pos, itemsName)
  plt.xlabel('Total number of documents')

  ax.set_axisbelow(True)
  ax.xaxis.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

  fig = plt.gcf()
  fig.set_size_inches(args.plotWidth, args.plotHeight)


def plot_bar_horizontal_trends(plt, topicResults, agrStartYear, agrEndYear, args):
  ax = plt.gca()
  itemsName = []
  x = []
  x2 = []
  xPer = []
  for topicItem in topicResults:
    x.append(topicItem["PapersTotal"])
    x2.append(topicItem["PapersInLastYears"])
    xPer.append(round(topicItem["PerInLastYears"]))
    itemsName.append(topicItem["name"])

  y_pos = np.arange(len(itemsName))[::-1]

  plt.barh(y_pos, x, 0.6, align='center', color=globalVar.COLORS_TAB20[0], edgecolor="black", linewidth=0.5)
  plt.barh(y_pos, x2, 0.6, align='center', color=globalVar.COLORS_TAB20[2], edgecolor="black", linewidth=0.5, left=np.subtract(x,x2))

  [xmin, xmax] = ax.get_xlim()
  [ymin, ymax] = ax.get_ylim()
  ax.set_xlim([xmin, xmax + (xmax-xmin)*0.1])


  for xt, xPerT, yt in zip(x, xPer, y_pos):
    plt.text(xt + (xmax-xmin)*0.03, yt - (ymax-ymin)*0.003, '%d%%' % xPerT, ha='left', va='center')


  plt.yticks(y_pos, itemsName)
  plt.xlabel('Total number of documents, with percentage of documents \npublished in the last years %d - %d' % (agrStartYear, agrEndYear))
  #plt.ylabel("Average documents per year, %d - %d (doc./year)" % (agrStartYear, agrEndYear))

  plt.legend(["Before %d" % agrStartYear, "Between %d - %d" %(agrStartYear, agrEndYear)], loc=4)

  ax.set_axisbelow(True)
  ax.xaxis.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

  fig = plt.gcf()
  fig.set_size_inches(args.plotWidth, args.plotHeight)

  if(len(itemsName) > 20):
    fig.set_size_inches(args.plotWidth, args.plotHeight*(len(itemsName)/17))


# Keep only the first zero right to left
def zero_to_nan(values):
  firstZero = False
  for i in reversed(range(0, len(values))):
    if values[i] < 0.1:
      if firstZero:
        values[i] = float('nan')
      firstZero = True

# Keep only the first zero right to left
def zero_to_nan2(values, valuesAcum):
  for i in reversed(range(0, len(values))):
    if valuesAcum[i] == 0:
      if values[i] == 0:
        values[i] = float('nan')


def plot_evolution(plt, topicResults, agrStartYear, agrEndYear, args):
  my_dpi = 100
  plt.figure(figsize=(800 / my_dpi, 500 / my_dpi), dpi=my_dpi)

  gs = gridspec.GridSpec(1, 2, width_ratios=[5, 3])

  # Plot AGR and H-index
  ax = plt.subplot(gs[1])
  xArray = []
  yArray = []
  count = 0
  for topicItem in topicResults:
    x = topicItem["PerInLastYears"]
    if not args.agrForGraph:
      y = topicItem["AverageDocPerYear"]
    else:
      y = topicItem["agr"]

    xArray.append(x)
    yArray.append(y)

    ax.scatter(x, y, marker=globalVar.MARKERS[count], label=topicItem["name"], zorder=(3 + len(topicResults) - count),
               s=200, c=globalVar.COLORS_TAB10[count], edgecolors=globalVar.COLORS_TAB10[count])

    count += 1

  plt.xlabel("Percentage of documents \npublished in the last years %d - %d " % (agrStartYear, agrEndYear))
  if not args.agrForGraph:
    plt.ylabel("Average documents per year, %d - %d (doc./year)" % (agrStartYear, agrEndYear))
  else:
    plt.ylabel("Average growth rate (AGR), %d - %d (doc./year)" % (agrStartYear, agrEndYear))

  plt.gca().set_xticklabels(['{:.0f}%'.format(x) for x in plt.gca().get_xticks()])

  # Calculate plot max and min
  xMax = max(xArray)
  yMax = max(yArray)

  xMin = min(xArray)
  yMin = min(yArray)

  yMaxMax = max([abs(yMax), abs(yMin)])

  # Set the graphs limits
  if (xMin > 0):
    plt.xlim(left=0)
  else:
    plt.xlim(left=-0.5)

  plt.xlim(right=xMax * 1.2)

  if (yMin > 0):
    plt.ylim(bottom=0)
  else:
    plt.ylim(bottom=yMin - (yMaxMax * 0.1))

  if (yMax > 0):
    plt.ylim(top=yMax + (yMaxMax * 0.1))
  else:
    plt.ylim(top=yMax * (-1.2))


  ax.grid(linestyle='--', linewidth=0.5, dashes=(5, 10), zorder = 1)

  # Plot the X dash line
  xmin, xmax = ax.get_xlim()
  dashed_line = Line2D([xmin, xmax], [0.0, 0.0], linestyle='--', linewidth=1, color=[0, 0, 0], zorder=2,
                       transform=ax.transData)
  ax.lines.append(dashed_line)

  # Plot the Y dash line
  ymin, ymax = ax.get_ylim()
  dashed_line = Line2D([0.0, 0.0], [ymin, ymax], linestyle='--', linewidth=1, color=[0, 0, 0], zorder=2,
                       transform=ax.transData)
  ax.lines.append(dashed_line)

  #plt.ylabel("Average growth rate, %d - %d (doc./year)" % (
  #  yearArray[startYearIndex], yearArray[endYearIndex]))
  #plt.xlabel("Total documents ")


  # Plot accumulative papers count
  ax0 = plt.subplot(gs[0])

  count = 0
  legendArray = []
  for topicItem in topicResults:
    legendArray.append(topicItem["name"])
    #zero_to_nan(topicResults[topics[0].upper()]["PapersCountAccum"])

    x = topicItem["year"]
    y = topicItem["PapersCountAccum"]

    xnew = np.linspace(min(x), max(x), 300)

    f = interpolate.interp1d(x, y, kind='linear')
    ylineal = f(xnew)

    s = Rbf(x, y, smooth=0.4, epsilon = 0.2)
    ynew = s(xnew)

    for i in range(0,len(ylineal)):
      if ylineal[i] < 0.1:
        ynew[i] = 0

    zero_to_nan(ynew)
    zero_to_nan(y)

    ax0.plot(xnew, ynew,
             linewidth=1.5, marker=globalVar.MARKERS[count], markersize=12, markevery = [-1],
             zorder=(len(topicResults) - count), color=globalVar.COLORS_TAB10[count], markeredgewidth=0.0)


    #ax0.plot(x, y,
    #         linewidth=1.5, marker=globalVar.MARKERS[count], markersize=12, markevery = [-1],
    #         zorder=(len(topicResults) - count), color=globalVar.COLORS_TAB10[count], alpha = 0.25, markeredgewidth=0.0)

    ax0.xaxis.set_major_locator(MaxNLocator(integer=True))


    count += 1

  [xmin, xmax] = ax0.get_xlim()
  ax0.set_xlim([min(x), xmax + (xmax-xmin)*0.1])

  [ymin, ymax] = ax0.get_ylim()
  ax0.set_ylim(0, ymax)
  ax0.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

  # Only integers in accomulatlive number of documents
  ax0.yaxis.set_major_locator(MaxNLocator(integer=True))

  ax0.ticklabel_format(useOffset=False)
  legend1 = ax0.legend(legendArray, loc=2, fontsize=10, scatterpoints=1)
  legend1.get_frame().set_alpha(1)
  legend1.set_zorder(count)  # put the legend on top

  plt.xlabel("Publication year")
  plt.ylabel("Accumulative Number of Documents")

  if args.yLog:
    ax0.set_yscale("symlog", nonposy='clip')
    ax0.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax0.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())


def grapPreprocess(plt, preProcessBrief):
  ax = plt.gca()
  itemsName = ["WoS", "Scopus"]

  x = []
  x2 = []
  xPer = []

  x.append(preProcessBrief["loadedPapersWoS"])
  x.append(preProcessBrief["loadedPapersScopus"])

  x2.append(preProcessBrief["removedPapersWoS"])
  x2.append(preProcessBrief["removedPapersScopus"])

  xPer.append(round(preProcessBrief["percenRemPapersWos"]))
  xPer.append(round(preProcessBrief["percenRemPapersScopus"]))

  y_pos = np.arange(len(itemsName))[::-1]

  plt.barh(y_pos, x, 0.4, align='center', color=globalVar.COLORS_TAB20[0], edgecolor="black", linewidth=0.5)
  plt.barh(y_pos, x2, 0.4, align='center', color=globalVar.COLORS_TAB20[2], edgecolor="black", linewidth=0.5, left=np.subtract(x,x2))

  [xmin, xmax] = ax.get_xlim()
  [ymin, ymax] = ax.get_ylim()
  ax.set_xlim([xmin, xmax + (xmax-xmin)*0.2])
  ax.set_ylim([ymin - (ymax - ymin) * 0.2, ymax + (ymax - ymin) * 0.2])


  for xt, xPerT, yt in zip(x, xPer, y_pos):
    plt.text(xt + (xmax-xmin)*0.03, yt - (ymax-ymin)*0.003, '%d%%' % xPerT, ha='left', va='center')


  plt.yticks(y_pos, itemsName)
  plt.xlabel("Total loaded documents, with percentage of removed documents")

  plt.legend(["Documents kept", "Removed dupl."], loc=1, prop={'size': 10})

  ax.set_axisbelow(True)
  ax.xaxis.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

  fig = plt.gcf()
  fig.set_size_inches(globalVar.DEFAULT_PLOT_WIDTH, globalVar.DEFAULT_PLOT_WIDTH/2)

