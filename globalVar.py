# Default start and end year
DEFAULT_START_YEAR = 2000
DEFAULT_END_YEAR = 2017

# Default output files and folders
PREPROCESS_LOG_FILE = "PreprocessedBrief.csv"
OUTPUT_FILE_NAME = "papersPreprocessed.csv"
DATA_OUT_FOLDER = "dataPre"
GRAPHS_OUT_FOLDER = "graphs"
DEFUALT_DATA_IN_FOLDER = "dataIn"
RESULTS_FOLDER = "results"

# Documents types to include on the script processing
INCLUDED_TYPES = ["Conference Paper", "Article", 
"Review", "Proceedings Paper"]

# Default trend sizes
TOP_TREND_SIZE = 200
TREND_PERIODS = 3

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

SCIENTOPY_VERSION = "1.0.3c"