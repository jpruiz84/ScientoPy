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
import pathlib
import sys
import webbrowser

import globalVar
import networkAnalysis as na

def add_map_arguments(parser):
    """Arguments that select the items, links and clusters. Shared with
    scientoPyThematicMap.py, so both scripts give the same clusters."""
    parser.add_argument("-c", "--criterion", choices=globalVar.validNetworkCriterion,
                        default="authorKeywords",
                        help="Criterion to map: keyword co-occurrence, co-authorship, "
                             "country or institution collaboration, default authorKeywords")

    parser.add_argument("-l", "--length", type=int, default=na.DEFAULT_LENGTH,
                        help="Maximum number of items in the map (top by occurrences), "
                             "default %d, maximum %d" % (na.DEFAULT_LENGTH, na.MAX_LENGTH))

    parser.add_argument("--minOccurrences", type=int, default=na.DEFAULT_MIN_OCCURRENCES,
                        help="Minimum number of documents an item must appear in, default %d"
                             % na.DEFAULT_MIN_OCCURRENCES)

    parser.add_argument("-s", "--skipFirst", type=int, default=0,
                        help="Leave out the first N top items, for example the search terms "
                             "that co-occur with everything. Ex: -s 2")

    parser.add_argument("--exclude", default="",
                        help='Items to leave out, separated by ";". Ex: --exclude "ble; bluetooth"')

    parser.add_argument("--synonyms", default="",
                        help='Merge synonyms before counting. Groups separated by ";", synonyms by ",", '
                             'the first one names the group. Ex: --synonyms "internet of things, iot; '
                             'bluetooth low energy, ble". Also accepts a VOSviewer thesaurus file '
                             '(tab separated: label, replace by)')

    parser.add_argument("--startYear", type=int, default=globalVar.DEFAULT_START_YEAR,
                        help="Start year to limit the search, default: %d" % globalVar.DEFAULT_START_YEAR)

    parser.add_argument("--endYear", type=int, default=globalVar.DEFAULT_END_YEAR,
                        help="End year to limit the search, default: %d" % globalVar.DEFAULT_END_YEAR)

    parser.add_argument("--counting", choices=na.COUNTING_METHODS, default=na.DEFAULT_COUNTING,
                        help="full: every co-occurrence counts 1. fractional: a document with n "
                             "items gives each link 1/(n-1), so documents with many authors or "
                             "keywords weigh less. Default %s" % na.DEFAULT_COUNTING)

    parser.add_argument("--minLinkStrength", type=float, default=na.DEFAULT_MIN_LINK_STRENGTH,
                        help="Minimum link strength to keep a link, default: keep all links")

    parser.add_argument("--resolution", type=float, default=na.DEFAULT_RESOLUTION,
                        help="Clustering resolution, higher values give more and smaller "
                             "clusters, default %s" % na.DEFAULT_RESOLUTION)

    parser.add_argument("--minClusterSize", type=int, default=na.DEFAULT_MIN_CLUSTER_SIZE,
                        help="Clusters with fewer items are merged into their most connected "
                             "cluster, default %d" % na.DEFAULT_MIN_CLUSTER_SIZE)

    parser.add_argument("-r", "--previousResults", action="store_true",
                        help="Map the documents found by the previous scientoPy.py analysis")

    parser.add_argument("--graphTitle", type=str, default="",
                        help="Title shown in the map")


parser = argparse.ArgumentParser(
    description="Create an interactive co-occurrence network map (VOSviewer style) "
                "of the topics inside a criterion",
    epilog="The map is saved as graphs/<Criterion>_network.html (works offline, open it "
           "in any modern browser). JSON, CSV, GEXF (Gephi) and VOSviewer map/network "
           "files are saved under results/. For the thematic map of the same clusters "
           "run scientoPyThematicMap.py.",
)

add_map_arguments(parser)

parser.add_argument("--cohesion", type=float, default=na.DEFAULT_COHESION,
                    help="Extra attraction between items of the same cluster in the layout, "
                         "0 for the plain VOS mapping, default %s" % na.DEFAULT_COHESION)

parser.add_argument("--windowWidth", type=int, default=na.DEFAULT_WINDOW_WIDTH,
                    help="Window width in years for the AGR and PDLY of each item, default %d"
                         % na.DEFAULT_WINDOW_WIDTH)

parser.add_argument("--noOpen", action="store_true",
                    help="Do not open the map in the web browser")


def main():
    args = parser.parse_args()

    print("\n\nScientoPy network map: %s" % globalVar.SCIENTOPY_VERSION)
    print("============================\n")

    try:
        data, files = na.generate_network_map(
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
            cohesion=args.cohesion,
            window_width=args.windowWidth,
            previous_results=args.previousResults,
            title=args.graphTitle,
        )
    except na.NetworkError as e:
        print("ERROR: %s" % e)
        sys.exit(1)

    meta = data["meta"]
    print("Papers in range (%d - %d): %d" % (meta["startYear"], meta["endYear"], meta["papersInRange"]))
    print("Items: %d   Links: %d   Clusters: %d\n" % (len(data["nodes"]), len(data["links"]),
                                                     len(data["clusters"])))
    print('-' * 87)
    print("{:<8s}{:>6s}{:>8s}   {:<65s}".format("Cluster", "Items", "Avg yr", "Top items"))
    print('-' * 87)
    for cluster in data["clusters"]:
        avg_year = "%.1f" % cluster["avgYear"] if cluster["avgYear"] else "-"
        print("{:<8d}{:>6d}{:>8s}   {:<65s}".format(
            cluster["id"], cluster["size"], avg_year, "; ".join(cluster["top"][:4])[:65]))
    print('-' * 87)

    print("\nNetwork map saved on: %s" % files["html"])
    print("Data saved on: %s" % ", ".join(
        files[k] for k in ("json", "nodes", "links", "clusters", "gexf", "vosMap", "vosNetwork")))

    if not args.noOpen:
        webbrowser.open(pathlib.Path(os.path.abspath(files["html"])).as_uri())


if __name__ == '__main__':
    main()
