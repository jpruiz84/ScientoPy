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

import sys

# Check python version
if sys.version_info[0] < 3:
  print("ERROR, you are using Python 2, Python 3.X.X required")
  print("")
  exit()

# Default start and end year
DEFAULT_START_YEAR = 1990
DEFAULT_END_YEAR = 2019

# Default plot width and height in inches
DEFAULT_PLOT_WIDTH = 6.4
DEFAULT_PLOT_HEIGHT = 4.8


# Default output files and folders
PREPROCESS_LOG_FILE = "PreprocessedBrief.csv"
OUTPUT_FILE_NAME = "papersPreprocessed.csv"
OUTPUT_FILE_BIB = "bibliography.bib"
DATA_OUT_FOLDER = "dataPre"
GRAPHS_OUT_FOLDER = "graphs"
DEFUALT_DATA_IN_FOLDER = "dataIn"
RESULTS_FOLDER = "results"

# Documents types to include on the script processing
INCLUDED_TYPES = ["Conference Paper", "Article", 
"Review", "Proceedings Paper", "Article in Press"]

# Default trend sizes
TOP_TREND_SIZE = 200
TREND_PERIODS = 3

# True to use a predefined color map instead the following list
USE_COLOR_MAP = True

# Default colors and markers for the graphs
COLORS_TAB10 = [
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf",
"#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

COLORS_TAB20 = [
"#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
"#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5",
"#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
"#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5",
"#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
"#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5",
"#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
"#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5",
"#1f77b4", "#aec7e8", "#ff7f0e", "#ffbb78", "#2ca02c", "#98df8a", "#d62728", "#ff9896", "#9467bd", "#c5b0d5",
"#8c564b", "#c49c94", "#e377c2", "#f7b6d2", "#7f7f7f", "#c7c7c7", "#bcbd22", "#dbdb8d", "#17becf", "#9edae5"]


MARKERS = ('o', '^', 's', 'p', '*', 'd', 'D', '8', 'v', '>', 'v', '<', '8', '^', 's', 'p', 'h', '*', 'H', 'D', 'd',
'o', '^', 's', 'p', '*', 'd', 'D', '8', 'v', '>', 'v', '^', '<', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 
'o', '^', 's', 'p', '*', 'd', 'D', '8', 'v', '>', 'v', '^', '<', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 
'o', '^', 's', 'p', '*', 'd', 'D', '8', 'v', '>', 'v', '^', '<', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 
'o', '^', 's', 'p', '*', 'd', 'D', '8', 'v', '>', 'v', '^', '<', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 
'o', '^', 's', 'p', '*', 'd', 'D', '8', 'v', '>', 'v', '^', '<', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 
'o', '^', 's', 'p', '*', 'd', 'D', '8', 'v', '>', 'v', '^', '<', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 
'o', '^', 's', 'p', '*', 'd', 'D', '8', 'v', '>', 'v', '^', '<', '8', 's', 'p', '*', 'h', 'H', 'D', 'd')


# Save the papersPreprocessed format
SAVE_RESULTS_ON = "SCOPUS_FIELDS"
#SAVE_RESULTS_ON = "WOS_FIELDS"

# Global variables
logFile = 0
loadedPapers = 0
omitedPapers = 0
OriginalTotalPapers = 0
papersScopus = 0
papersWoS = 0
totalAfterRemDupl = 0


SCIENTOPY_VERSION = "1.4.0"
