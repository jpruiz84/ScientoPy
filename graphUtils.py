# The MIT License (MIT)
# Copyright (c) 2026 - Universidad del Cauca, Juan Ruiz-Rosero
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
import matplotlib.ticker as mtick


def plot_time_line(plt, topicResults, fSecundary, args):
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

    fig = plt.gcf()
    fig.set_size_inches(globalVar.DEFAULT_PLOT_WIDTH, globalVar.DEFAULT_PLOT_WIDTH/2)
    plt.gcf().canvas.manager.set_window_title(args.criterion + ' time line graph')

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
  plt.gcf().canvas.manager.set_window_title(args.criterion + ' bar graph')
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
    xPer.append(topicItem["PerInLastYears"])
    itemsName.append(topicItem["name"])

  y_pos = np.arange(len(itemsName))[::-1]

  plt.barh(y_pos, x, 0.6, align='center', color=globalVar.COLORS_TAB20[0], edgecolor="black", linewidth=0.5)
  plt.barh(y_pos, x2, 0.6, align='center', color=globalVar.COLORS_TAB20[2], edgecolor="black", linewidth=0.5, left=np.subtract(x,x2))

  [xmin, xmax] = ax.get_xlim()
  [ymin, ymax] = ax.get_ylim()
  ax.set_xlim([xmin, xmax + (xmax-xmin)*0.1])


  for xt, xPerT, yt in zip(x, xPer, y_pos):
    plt.text(xt + (xmax-xmin)*0.03, yt - (ymax-ymin)*0.003, f'%0.{globalVar.decPlaces}f%%' % xPerT, ha='left', va='center')


  plt.yticks(y_pos, itemsName)
  plt.xlabel('Total number of documents, with percentage of documents \npublished in the last years %d - %d' % (agrStartYear, agrEndYear))
  #plt.ylabel("Average documents per year, %d - %d (doc./year)" % (agrStartYear, agrEndYear))

  plt.legend(["Before %d" % agrStartYear, "Between %d - %d" %(agrStartYear, agrEndYear)], loc=4)

  ax.set_axisbelow(True)
  ax.xaxis.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

  fig = plt.gcf()
  fig.set_size_inches(args.plotWidth, args.plotHeight)
  plt.gcf().canvas.manager.set_window_title(args.criterion + ' bar trends graph')


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

  ax.xaxis.set_major_formatter(mtick.PercentFormatter())

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
  ax.add_line(dashed_line)

  # Plot the Y dash line
  ymin, ymax = ax.get_ylim()
  dashed_line = Line2D([0.0, 0.0], [ymin, ymax], linestyle='--', linewidth=1, color=[0, 0, 0], zorder=2,
                       transform=ax.transData)
  ax.add_line(dashed_line)

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
  plt.ylabel("Accumulative number of documents")

  if args.yLog:
    ax0.set_yscale("symlog", nonpositive='clip')
    ax0.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax0.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())

  fig = plt.gcf()
  plt.gcf().canvas.manager.set_window_title(args.criterion + ' evolution graph')


def graphPreprocess(plt, preProcessBrief):
  ax = plt.gca()
  itemsName = ["WoS", "Scopus"]

  x = []
  x2 = []
  xPer = []

  x.append(preProcessBrief["loadedPapersWoS"])
  x.append(preProcessBrief["loadedPapersScopus"])

  x2.append(preProcessBrief["removedPapersWoS"])
  x2.append(preProcessBrief["removedPapersScopus"])

  xPer.append(preProcessBrief["percenRemPapersWos"])
  xPer.append(preProcessBrief["percenRemPapersScopus"])

  y_pos = np.arange(len(itemsName))[::-1]

  plt.barh(y_pos, x, 0.4, align='center', color=globalVar.COLORS_TAB20[0], edgecolor="black", linewidth=0.5)
  plt.barh(y_pos, x2, 0.4, align='center', color=globalVar.COLORS_TAB20[2], edgecolor="black", linewidth=0.5, left=np.subtract(x,x2))

  [xmin, xmax] = ax.get_xlim()
  [ymin, ymax] = ax.get_ylim()
  ax.set_xlim([xmin, xmax + (xmax-xmin)*0.2])
  ax.set_ylim([ymin - (ymax - ymin) * 0.2, ymax + (ymax - ymin) * 0.2])


  for xt, xPerT, yt in zip(x, xPer, y_pos):
    plt.text(xt + (xmax-xmin)*0.03, yt - (ymax-ymin)*0.003, f'%0.{globalVar.decPlaces}f%%' % xPerT, ha='left', va='center')


  plt.yticks(y_pos, itemsName)
  plt.xlabel("Total loaded documents, with percentage of removed documents")

  plt.legend(["Documents kept", "Removed dupl."], loc=1, prop={'size': 10})

  ax.set_axisbelow(True)
  ax.xaxis.grid(linestyle='--', linewidth=0.5, dashes=(5, 10))

  fig = plt.gcf()
  fig.set_size_inches(globalVar.DEFAULT_PLOT_WIDTH, globalVar.DEFAULT_PLOT_WIDTH/2)
  plt.gcf().canvas.manager.set_window_title('Preprocess brief graph')



# Sequential blue ramp, light to dark, for magnitudes (world map)
SEQUENTIAL_BLUES = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]

# Cluster colors of the thematic map, used in this order
THEME_COLORS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]


def _is_dark(color):
  """True when a matplotlib color is a dark surface."""
  import matplotlib.colors as mcolors
  r, g, b = mcolors.to_rgb(color)
  return 0.2126 * r + 0.7152 * g + 0.0722 * b < 0.5


def plot_world_map(plt, counts, args):
  """Choropleth world map of {country name: documents}.

  Countries are shaded with one blue ramp (linear, or logarithmic with
  args.yLog) and the ones with no documents stay gray. Countries too small to
  see at this scale (Singapore, Hong Kong, ...) get a dot in the same color.
  Returns the names that could not be placed on the map, the ones with more
  documents first.
  """
  import worldMap
  from matplotlib.cm import ScalarMappable
  from matplotlib.collections import PolyCollection
  from matplotlib.colors import LinearSegmentedColormap, LogNorm, Normalize

  countries = worldMap.load_countries()
  matched, notFound = worldMap.match_countries(counts)
  matched = {index: value for index, value in matched.items() if value > 0}

  fig = plt.gcf()
  ax = plt.gca()
  surface = fig.get_facecolor()
  dark = _is_dark(surface)
  ink = plt.rcParams["text.color"]
  noData = "#3b3b39" if dark else "#e6e5e0"
  # On a dark surface the ramp runs the other way: few documents stay close
  # to the surface and many documents stand out
  ramp = SEQUENTIAL_BLUES[::-1][1:] if dark else SEQUENTIAL_BLUES
  cmap = LinearSegmentedColormap.from_list("scientopy_blues", ramp)

  maxValue = max(matched.values()) if matched else 1
  if args.yLog:
    norm = LogNorm(vmin=1, vmax=max(maxValue, 2))
  else:
    norm = Normalize(vmin=0, vmax=maxValue)

  # Larger outlines first, so enclaves (Lesotho, San Marino) stay on top
  shapes = []
  dots = []
  for index, country in enumerate(countries):
    value = matched.get(index)
    color = cmap(norm(value)) if value else noData
    extent = 0.0
    largest = None
    for ring in country["polygons"]:
      lon, lat = zip(*ring)
      x, y = worldMap.robinson(lon, lat)
      size = (x.max() - x.min()) * (y.max() - y.min())
      shapes.append((size, np.column_stack([x, y]), color))
      if largest is None or size > largest[0]:
        largest = (size, x.mean(), y.mean())
      extent = max(extent, x.max() - x.min(), y.max() - y.min())
    if value and largest is not None and extent < 0.03:
      dots.append((largest[1], largest[2], color))

  shapes.sort(key=lambda shape: -shape[0])
  ax.add_collection(PolyCollection([shape[1] for shape in shapes],
                                   facecolors=[shape[2] for shape in shapes],
                                   edgecolors=surface, linewidths=0.3))
  if dots:
    ax.scatter([d[0] for d in dots], [d[1] for d in dots], s=16, c=[d[2] for d in dots],
               edgecolors=surface, linewidths=0.6, zorder=3)

  ax.set_xlim(-2.72, 2.72)
  ax.set_ylim(-1.0, 1.33)
  ax.set_aspect("equal")
  ax.set_anchor("N")
  ax.axis("off")

  # Color scale over the South Pacific, where the map is empty
  cax = ax.inset_axes([0.04, 0.13, 0.22, 0.03])
  colorbar = fig.colorbar(ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation="horizontal")
  if not args.yLog:
    colorbar.ax.xaxis.set_major_locator(MaxNLocator(nbins=4, integer=True))
  colorbar.outline.set_visible(False)
  colorbar.ax.tick_params(labelsize=7, length=2, colors=ink)
  colorbar.set_label("Number of documents" + (" (log scale)" if args.yLog else ""),
                     fontsize=7, color=ink, loc="left")

  if args.plotHeight != globalVar.DEFAULT_PLOT_HEIGHT:
    fig.set_size_inches(args.plotWidth, args.plotHeight)
  else:
    fig.set_size_inches(args.plotWidth, args.plotWidth * 0.46)
  plt.gcf().canvas.manager.set_window_title(args.criterion + ' world map graph')

  # The names with more documents first
  return sorted(notFound, key=lambda name: (-counts[name], name))


THEME_LABEL_GID = "scientopy-theme-label"
THEME_CORNER_GID = "scientopy-theme-corner"


def separate_theme_labels(ax, iterations=400):
  """Move the theme labels of a thematic map apart until none overlap.

  Call it once the figure has its final size and layout. Works in pixels:
  two labels that overlap are pushed apart along the direction that needs
  the shortest move, and the quadrant captions stay where they are. A label
  that ends away from its bubble gets a thin line back to it.
  """
  fig = ax.figure
  fig.canvas.draw()
  renderer = fig.canvas.get_renderer()

  labels = [t for t in ax.texts if t.get_gid() == THEME_LABEL_GID]
  if not labels:
    return
  pad = 5.0
  boxes = []
  for text in labels + [t for t in ax.texts if t.get_gid() == THEME_CORNER_GID]:
    extent = text.get_window_extent(renderer)
    boxes.append([extent.x0 - pad, extent.y0 - pad, extent.x1 + pad, extent.y1 + pad])
  boxes = np.array(boxes)
  nLabels = len(labels)
  anchors = np.column_stack([(boxes[:nLabels, 0] + boxes[:nLabels, 2]) / 2,
                             (boxes[:nLabels, 1] + boxes[:nLabels, 3]) / 2])
  frame = ax.get_window_extent(renderer)

  for _ in range(iterations):
    moved = False
    for a in range(nLabels):
      for b in range(a + 1, len(boxes)):
        overlapX = min(boxes[a, 2], boxes[b, 2]) - max(boxes[a, 0], boxes[b, 0])
        overlapY = min(boxes[a, 3], boxes[b, 3]) - max(boxes[a, 1], boxes[b, 1])
        if overlapX <= 0 or overlapY <= 0:
          continue
        moved = True
        axis = 0 if overlapX < overlapY else 1
        step = (overlapX if axis == 0 else overlapY) + 0.5
        centerA = (boxes[a, axis] + boxes[a, axis + 2]) / 2
        centerB = (boxes[b, axis] + boxes[b, axis + 2]) / 2
        direction = -1.0 if centerA < centerB or (centerA == centerB and a < b) else 1.0
        if b < nLabels:
          boxes[a, [axis, axis + 2]] += direction * step / 2
          boxes[b, [axis, axis + 2]] -= direction * step / 2
        else:
          boxes[a, [axis, axis + 2]] += direction * step
    # Keep the labels inside the plot
    for a in range(nLabels):
      for axis, low, high in ((0, frame.x0, frame.x1), (1, frame.y0, frame.y1)):
        shift = max(low - boxes[a, axis], 0) + min(high - boxes[a, axis + 2], 0)
        boxes[a, [axis, axis + 2]] += shift
    if not moved:
      break

  toData = ax.transData.inverted()
  muted = "#9a9992" if _is_dark(fig.get_facecolor()) else "#7c7b75"
  for a, text in enumerate(labels):
    center = np.array([(boxes[a, 0] + boxes[a, 2]) / 2, (boxes[a, 1] + boxes[a, 3]) / 2])
    if np.abs(center - anchors[a]).max() < 1.0:
      continue
    start = toData.transform(anchors[a])
    end = toData.transform(center)
    text.set_position(end)
    height = boxes[a, 3] - boxes[a, 1]
    if np.hypot(*(center - anchors[a])) > 0.6 * height:
      ax.plot([start[0], end[0]], [start[1], end[1]], color=muted, linewidth=0.7, zorder=4)
      ax.scatter([start[0]], [start[1]], s=8, color=muted, zorder=4)


def plot_thematic_map(plt, themes, args):
  """Thematic map (strategic diagram): one bubble per cluster of items.

  x is the Callon centrality (relevance of the theme for the whole field),
  y the Callon density (development of the theme) and the bubble area the
  occurrences of its items. With args.axes == "rank" (default) the bubbles
  are placed by rank, which spreads them evenly; with "value" by the
  centrality and density values. The dashed lines cross at the medians and
  split the map in motor, niche, emerging or declining, and basic themes.
  """
  import matplotlib.patheffects as patheffects

  fig = plt.gcf()
  ax = plt.gca()
  surface = fig.get_facecolor()
  ink = plt.rcParams["text.color"]
  muted = "#9a9992" if _is_dark(surface) else "#7c7b75"

  byRank = getattr(args, "axes", "rank") != "value"
  if byRank:
    x = np.array([theme["rankCentrality"] for theme in themes], dtype=float)
    y = np.array([theme["rankDensity"] for theme in themes], dtype=float)
  else:
    x = np.array([theme["centrality"] for theme in themes], dtype=float)
    y = np.array([theme["density"] for theme in themes], dtype=float)

  def limits(values):
    middle = float(np.median(values))
    if byRank:
      # The median in the center, so the four quadrants have the same size
      half = max(middle - values.min(), values.max() - middle) * 1.25 + 0.6
      return middle, middle - half, middle + half
    margin = 0.15 * (values.max() - values.min()) or 1.0
    return middle, values.min() - margin, values.max() + margin

  xMid, xMin, xMax = limits(x)
  yMid, yMin, yMax = limits(y)

  occ = np.array([theme["occ"] for theme in themes], dtype=float)
  sizes = 250 + 4500 * occ / occ.max()
  # Soft fills mixed with the surface instead of transparency, which EPS
  # files do not support
  import matplotlib.colors as mcolors
  surfaceRgb = np.array(mcolors.to_rgb(surface))
  colors = [tuple(0.6 * np.array(mcolors.to_rgb(THEME_COLORS[k % len(THEME_COLORS)])) + 0.4 * surfaceRgb)
            for k in range(len(themes))]

  ax.axvline(xMid, linestyle="--", linewidth=0.8, color=muted, zorder=1)
  ax.axhline(yMid, linestyle="--", linewidth=0.8, color=muted, zorder=1)
  # Larger bubbles behind, so the small ones stay visible
  order = np.argsort(-sizes)
  ax.scatter(x[order], y[order], s=sizes[order], c=[colors[k] for k in order],
             edgecolors=surface, linewidths=1.5, zorder=2)

  nLabels = max(1, getattr(args, "labels", 3))
  halo = [patheffects.withStroke(linewidth=2.5, foreground=surface)]
  for k, theme in enumerate(themes):
    text = ax.text(x[k], y[k], "\n".join(theme["items"][:nLabels]), ha="center", va="center",
                   fontsize=8.5, color=ink, zorder=5, linespacing=1.15, gid=THEME_LABEL_GID)
    text.set_path_effects(halo)

  corner = dict(transform=ax.transAxes, fontsize=9, color=muted, zorder=3, gid=THEME_CORNER_GID)
  ax.text(0.98, 0.98, "Motor themes", ha="right", va="top", **corner)
  ax.text(0.02, 0.98, "Niche themes", ha="left", va="top", **corner)
  ax.text(0.02, 0.02, "Emerging or\ndeclining themes", ha="left", va="bottom", **corner)
  ax.text(0.98, 0.02, "Basic themes", ha="right", va="bottom", **corner)

  ax.set_xlim(xMin, xMax)
  ax.set_ylim(yMin, yMax)
  ax.set_xlabel("Relevance degree\n(Centrality)")
  ax.set_ylabel("Development degree\n(Density)")
  if byRank:
    # Rank positions carry no unit; the values are in the results table
    ax.set_xticks([])
    ax.set_yticks([])

  fig.set_size_inches(args.plotWidth, args.plotHeight)
  plt.gcf().canvas.manager.set_window_title(args.criterion + ' thematic map graph')


def show_thematic_map(plt, themes, args, fromGui=False):
  """Draw the thematic map and show it, or save it to args.savePlot."""
  import os

  plt.figure()
  plot_thematic_map(plt, themes, args)

  if args.graphTitle:
    fig = plt.gcf()
    fig.suptitle(args.graphTitle, y=1.0)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
  else:
    plt.tight_layout()
  separate_theme_labels(plt.gca())

  if args.savePlot == "":
    plt.show(block=not fromGui)
  else:
    plt.savefig(os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot),
                bbox_inches='tight', pad_inches=0.01)
    print("Plot saved on: " + os.path.join(globalVar.GRAPHS_OUT_FOLDER, args.savePlot))
