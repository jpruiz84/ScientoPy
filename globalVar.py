from matplotlib import cm

# Default start and end year
DEFAULT_START_YEAR = 2000
DEFAULT_END_YEAR = 2018

# Default output files and folders
PREPROCESS_LOG_FILE = "PreprocessedBrief.tsv"
OUTPUT_FILE_NAME = "papersPreprocessed.tsv"
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
COLORS = ["#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969",
"#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969",
"#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969",
"#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969",
"#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969",
"#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969",
"#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969",
"#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969",
"#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969",
"#ff0000", "#009900", "#0000ff", "#ee7700", "#8b4513", "#8a2be2", "#000000", "#00bfff", "#b8860b", "#fa8072", "#696969"]

if USE_COLOR_MAP:
  cmap = cm.get_cmap('tab10')
  for i in range(0,len(COLORS)):
    COLORS[i] = cmap(i%10)


MARKERS = ('o', '^', 's', 'p', '*', 'd', 'D', '8', 'v', '>', 'v', '^', '<', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 
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
papersScopus = 0
papersWoS = 0
omitedPapers = 0

SCIENTOPY_VERSION = "1.2.1"
