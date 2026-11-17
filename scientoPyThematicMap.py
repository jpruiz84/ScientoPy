#!/usr/bin/env python3

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

import argparse
import os
import sys

import globalVar
import networkAnalysis as na
from scientoPyNetwork import add_map_arguments

parser = argparse.ArgumentParser(
    description="Create the thematic map (strategic diagram) of the topics inside a "
                "criterion: the clusters of topics that appear together, placed by their "
                "centrality (relevance) and density (development)",
    epilog="The themes are the clusters of scientoPyNetwork.py run with the same options. "
           "The table with the themes is saved as results/<Criterion>_thematic_map.csv.",
)

add_map_arguments(parser)

parser.add_argument("--labels", type=int, default=na.DEFAULT_THEME_LABELS,
                    help="Number of items written on each theme, the top ones by "
                         "occurrences, default %d" % na.DEFAULT_THEME_LABELS)

parser.add_argument("--axes", choices=na.THEMATIC_AXES, default="rank",
                    help="rank: place the themes by their centrality and density ranks, "
                         "which spreads them evenly. value: place them by the centrality "
                         "and density values. Default rank")

parser.add_argument("--savePlot", default="",
                    help='Save plot to a file. Ex: --savePlot "thematicMap.eps"')

parser.add_argument("--noPlot", action="store_true",
                    help="Do not plot the map, only save the table with the themes")

parser.add_argument("--plotWidth", type=float, default=globalVar.DEFAULT_PLOT_WIDTH,
                    help="Set the plot width size in inches, default: " + str(globalVar.DEFAULT_PLOT_WIDTH))

parser.add_argument("--plotHeight", type=float, default=globalVar.DEFAULT_PLOT_HEIGHT,
                    help="Set the plot heigth size in inches, default: " + str(globalVar.DEFAULT_PLOT_HEIGHT))


def main():
    args = parser.parse_args()

    print("\n\nScientoPy thematic map: %s" % globalVar.SCIENTOPY_VERSION)
    print("=============================\n")

    try:
        data, themes, files = na.generate_thematic_map(
            criterion=args.criterion,
            start_year=args.startYear,
            end_year=args.endYear,
            length=args.length,
            min_occurrences=args.minOccurrences,
            skip_first=args.skipFirst,
            exclude=args.exclude.split(";"),
            synonyms=args.synonyms,
            counting=args.counting,
            min_link_strength=args.minLinkStrength,
            resolution=args.resolution,
            min_cluster_size=args.minClusterSize,
            previous_results=args.previousResults,
            title=args.graphTitle,
        )
    except na.NetworkError as e:
        print("ERROR: %s" % e)
        sys.exit(1)

    meta = data["meta"]
    print("Papers in range (%d - %d): %d" % (meta["startYear"], meta["endYear"], meta["papersInRange"]))
    print("Items: %d   Themes: %d\n" % (len(data["nodes"]), len(themes)))
    print('-' * 100)
    print("{:<8s}{:>6s}{:>12s}{:>10s}   {:<28s} {:<33s}".format(
        "Cluster", "Items", "Centrality", "Density", "Theme", "Top items"))
    print('-' * 100)
    for theme in themes:
        print("{:<8d}{:>6d}{:>12.3f}{:>10.3f}   {:<28s} {:<33s}".format(
            theme["cluster"], theme["size"], theme["centrality"], theme["density"],
            theme["theme"], "; ".join(theme["items"][:3])[:33]))
    print('-' * 100)
    print("\nThemes saved on: %s" % files["themes"])

    if args.noPlot:
        return

    import matplotlib.pyplot as plt
    import graphUtils

    if not os.path.exists(globalVar.GRAPHS_OUT_FOLDER):
        os.makedirs(globalVar.GRAPHS_OUT_FOLDER)
    graphUtils.show_thematic_map(plt, themes, args)


if __name__ == '__main__':
    main()
