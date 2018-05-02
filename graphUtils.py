import numpy as np
from scipy.spatial import cKDTree
import globalVar
from matplotlib.lines import Line2D
from matplotlib import gridspec
from scipy.interpolate import Rbf, InterpolatedUnivariateSpline
from scipy import interpolate
from matplotlib.ticker import MaxNLocator

LABEL_COLOR = "#dddddd"
BUBBLE_COLOR = "#63d065"
EDGE_COLOR = "#444444"

xMax = 1
yMax = 1


def get_label_xy(xyData, i):
  tree = cKDTree(xyData)
  thresh = 0.15
  neighbors = tree.query_ball_point([xyData[i, 0], xyData[i, 1]], thresh)

  # print neighbors

  # if no conflicts
  if len(neighbors) == 1:
    xy = (-30, 30)
  else:
    mean = np.mean(xyData[:, :2][neighbors], axis=0)

    if mean[0] == xyData[i, 0] and mean[1] == xyData[i, 1]:
      if i < np.max(neighbors):
        xy = (-30, 30)
      else:
        xy = (30, -30)
    else:
      angle = np.arctan2(xyData[i, 1] - mean[1], xyData[i, 0] - mean[0])

      if angle > np.pi / 2:
        xy = (-30, 30)
      elif angle > 0:
        xy = (30, 30)
      elif angle > -np.pi / 2:
        xy = (30, -30)
      else:
        xy = (-30, -30)

  return xy


def labeled_scatter_plot(data, labels, plt_in):
  # Get the max of each axis
  xMax = data[:, :2][:, 0].max()
  yMax = data[:, :2][:, 1].max()
  zMax = data[:, 2].max()

  xMin = data[:, :2][:, 0].min()
  yMin = data[:, :2][:, 1].min()
  zMin = data[:, 2].min()

  # print("yMax = %s" % yMax)

  # Plot bubbles in scatter
  plt_in.scatter(
    data[:, 0], data[:, 1], marker='o', c=BUBBLE_COLOR, s=1000 * (data[:, 2] / float(zMax)),
    cmap=plt_in.get_cmap('Spectral'))

  # Get xyData points ploted scaled to 1
  xData = data[:, :2][:, 0] / float(xMax)
  yData = data[:, :2][:, 1] / float(yMax)
  xyData = np.append([xData], [yData], axis=0)
  xyData = np.transpose(xyData)

  # Plot each label
  for i in range(data.shape[0]):
    print(labels[i])
    xy = get_label_xy(xyData, i)
    plt_in.annotate(
      labels[i],
      xy=data[i, :2], xytext=xy,
      textcoords='offset points', ha='center', va='center',
      bbox=dict(boxstyle='round,pad=0.5', fc=LABEL_COLOR, alpha=0.75),
      arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    xy = np.array(xy) * [0.08 * xMax / 30.0, 0.12 * yMax / 30.0]
    xyLabel = data[i, :2] + xy
    xyLabelScaled1 = xyLabel * [1 / xMax, 1 / yMax]

    xyData = np.append(xyData, [xyLabelScaled1], axis=0)

  # for i in range(0,len(labels)):
  #    print("(%d): %s, label: %d" % (i, labels[i], (i + len(labels))))

  # Set the graphs limits
  if (xMin > 0):
    plt_in.xlim(xmin=0)
  else:
    plt_in.xlim(xmin=xMin * 1.2)
  plt_in.xlim(xmax=xMax * 1.2)

  if (yMin > 0):
    plt_in.ylim(ymin=0)
  else:
    plt_in.ylim(ymin=yMin - (yMax * 0.1))

  if (yMax > 0):
    plt_in.ylim(ymax=yMax * 1.2)
  else:
    plt_in.ylim(ymax=yMax * (-1.2))


def labeled_scatter_plot_colors(data, labels, plt_in):
  cmap = plt_in.cm.Paired(np.linspace(0, 1, len(labels)))

  # Get the max of each axis
  xMax = data[:, :2][:, 0].max()
  yMax = data[:, :2][:, 1].max()
  zMax = data[:, 2].max()

  xMin = data[:, :2][:, 0].min()
  yMin = data[:, :2][:, 1].min()
  zMin = data[:, 2].min()

  # print("yMax = %s" % yMax)

  fig = plt_in.figure()
  ax = plt_in.subplot(111)

  i = 0
  for dataIn in data:
    # plt_in.plot(dataIn[0], dataIn[1], 'o', color=globalVar.COLORS[i], markersize=100*dataIn[2]/float(zMax), label=labels[i])
    ax.scatter(dataIn[0], dataIn[1], marker="o", s=2000 * (dataIn[2] + 1) / float(zMax), c="w", edgecolors=EDGE_COLOR)
    ax.scatter(dataIn[0], dataIn[1], marker=globalVar.MARKERS[i], label=labels[i],
               s=800 * (dataIn[2] + 1) / float(zMax), c=cmap[i].tolist(), edgecolors=cmap[i].tolist())
    i += 1

  # for i in range(0,len(labels)):
  #    print("(%d): %s, label: %d" % (i, labels[i], (i + len(labels))))


  # Shrink current axis by 20%
  # box = ax.get_position()
  # ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])


  lgnd = ax.legend(loc=2, scatterpoints=1, fontsize=12, fancybox=True, ncol=3)

  lgnd.get_frame().set_alpha(0.5)

  # lgnd = plt_in.legend(loc='center left', bbox_to_anchor=(1, 0.815), numpoints=1)
  for handle in lgnd.legendHandles:
    handle.set_sizes([100.0])

  # Set the graphs limits
  if (xMin > 0):
    plt_in.xlim(xmin=0)
  else:
    plt_in.xlim(xmin=xMin * 1.2)
  plt_in.xlim(xmax=xMax * 1.2)

  if (yMin > 0):
    plt_in.ylim(ymin=0)
  else:
    plt_in.ylim(ymin=yMin - (yMax * 0.1))

  if (yMax > 0):
    plt_in.ylim(ymax=yMax * 1.4)
  else:
    plt_in.ylim(ymax=yMax * (-1.2))


# This is the used for parametric right now ********************************************
def plot_parametric(plt, topicResults, agrStartYear, agrEndYear):
  my_dpi = 80
  plt.figure(figsize=(800 / my_dpi, 500 / my_dpi), dpi=my_dpi)

  gs = gridspec.GridSpec(1, 2, width_ratios=[5, 3])

  # Plot AGR and H-index
  ax = plt.subplot(gs[1])
  xArray = []
  yArray = []
  count = 0
  for topicItem in topicResults:
    x = topicItem["hIndex"]
    y = topicItem["agr"]

    xArray.append(x)
    yArray.append(y)

    ax.scatter(x, y, marker=globalVar.MARKERS[count], label=topicItem["name"], zorder=(3 + len(topicResults) - count),
               s=200, c=globalVar.COLORS[count], edgecolors=globalVar.COLORS[count])

    count += 1

  plt.xlabel("h-Index")
  plt.ylabel("Average Growth Rate, %d - %d (doc./year)" % (agrStartYear, agrEndYear))


  # Calculate plot max and min
  xMax = max(xArray)
  yMax = max(yArray)

  xMin = min(xArray)
  yMin = min(yArray)

  yMaxMax = max([abs(yMax), abs(yMin)])

  # Set the graphs limits
  if (xMin > 0):
    plt.xlim(xmin=0)
  else:
    plt.xlim(xmin=-0.5)

  plt.xlim(xmax=xMax * 1.2)

  if (yMin > 0):
    plt.ylim(ymin=0)
  else:
    plt.ylim(ymin=yMin - (yMaxMax * 0.1))

  if (yMax > 0):
    plt.ylim(ymax=yMax + (yMaxMax * 0.1))
  else:
    plt.ylim(ymax=yMax * (-1.2))


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
             zorder=(len(topicResults) - count), color=globalVar.COLORS[count], markeredgewidth=0.0)


    #ax0.plot(x, y,
    #         linewidth=1.5, marker=globalVar.MARKERS[count], markersize=12, markevery = [-1],
    #         zorder=(len(topicResults) - count), color=globalVar.COLORS[count], alpha = 0.25, markeredgewidth=0.0)

    ax0.xaxis.set_major_locator(MaxNLocator(integer=True))


    count += 1

  [xmin, xmax] = ax0.get_xlim()
  ax0.set_xlim([min(x), xmax + (xmax-xmin)*0.1])

  [ymin, ymax] = ax0.get_ylim()
  ax0.set_ylim(0, ymax)
  ax0.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))


  ax0.ticklabel_format(useOffset=False)
  legend1 = ax0.legend(legendArray, loc=2, fontsize=12, scatterpoints=1)
  legend1.get_frame().set_alpha(1)
  legend1.set_zorder(count)  # put the legend on top


  plt.xlabel("Publication year")
  plt.ylabel("Accumulative Number of Documents")

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
        zorder=(len(topicResults) - count), color=globalVar.COLORS[count], markeredgewidth=0.0)
      else:
        plt.plot(x, y,
                 linewidth=1.2, marker=globalVar.MARKERS[count], markersize=10, label=topicItem["name"],
                 zorder=(len(topicResults) - count), color=globalVar.COLORS[count], markeredgewidth=0.0,
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


