# ScientoPy

ScientoPy is a open-source Python based scientometric analysis tool.
It has the following main characteristics: 

 
- Import Clarivate Web of Science (WoS) and Scopus data sets (recursive folder scan)
- Parallel, multi-core preprocessing pipeline (Polars CSV reader + process-pool row normalization)
- Apache Parquet as the canonical on-disk format — ~10× smaller and ~20× faster to load than CSV
- Filter publications by document type
- Merge WoS and Scopus data set based on a field tags correlation table
- Find and remove duplicated documents
- H-index extraction for the analyzed topics.
- Country and institution extraction from author affiliations
- Top authors, countries, or institutions based on first document's authors or all document's authors
- Preprocessing brief graph and report table
- Top topics and specific topics analysis
- Wildcard topics search
- Trending topics using the top average growth rate (AGR)
- Five different visualization graphs: bar, bar trends, timeline, evolution, and word cloud
- Interactive co-occurrence network maps (VOSviewer style) for keywords, co-authorship, and country or institution collaboration: 3D/2D views, clustering, overlay and density visualizations, an animated crawler tour, and PNG/SVG/video/VOSviewer/Gephi exports
- Automatic BibTeX bibliography generation from LaTeX documents using paper EIDs as cite keys
- On-demand CSV export (Scopus or WoS field style) via `exportPapers.py` or the GUI Export tab
- Graphical user interface with six tabs (Pre-processing, Analysis, Results, Extended Results, Export, Network Map)


Download Pre-built Releases
===========================

Download the latest release for your platform from:
<https://github.com/jpruiz84/ScientoPy/releases>

| Platform | File | Instructions |
|---|---|---|
| **Windows** (x64) | `ScientoPy-windows-x64.zip` | Extract and run `ScientoPyGui.exe` |
| **Linux** (x64) | `ScientoPy-linux-x64.tar.gz` | Extract, then `chmod +x ScientoPyGui/ScientoPyGui && ./ScientoPyGui/ScientoPyGui` |
| **macOS** (Apple Silicon) | `ScientoPy-macos-arm64.zip` | Extract, then right-click > Open (or `xattr -cr ScientoPyGui/`) to bypass Gatekeeper |

For detailed instructions about the ScientoPy Graphic User Interface, see the user manual:
[Manual/ScientoPyGui_user_manual.pdf](./Manual/ScientoPyGui_user_manual.pdf)

Run ScientoPy from source (Linux, macOS, Windows)
==================================================

To clone directly the last version from the repository run the following
git command:

    git clone https://github.com/jpruiz84/ScientoPy


Install prerequisites
----------------------

**Requirements:** Python 3.9 or higher.

1.  On Ubuntu/Debian, install Python3 and tkinter:

        sudo apt-get install python3 python3-tk python3-pip python3-pil python3-pil.imagetk

2.  Create a virtual environment and install dependencies:

        python3 -m venv venv
        source venv/bin/activate        # Linux/macOS
        # venv\Scripts\activate          # Windows

        pip install --upgrade pip
        pip install -r requirements.txt
        

The bibliometric dataset
=======================

To download a custom dataset refer to the user manual: 
    [Manual/ScientoPy_user_manual.pdf](./Manual/ScientoPy_user_manual.pdf)
    
In this repo we include an example dataset that was donwloaded using: 
"Bluetooth low energy" as search criteria 


Running the ScientoPy Graphical User Interface GUI
==================================================

To run ScientoPy operations from the GUI, execute the following command:

    python3 ScientoPyGui.py


Running the ScientoPy from console scripts
=========================================

This section describes the ScientoPy scripts to preprocess and analyze
the bibliometric dataset.

Preprocessing
-------------

First we need to preprocess the downloaded dataset. This preprocess
merges all the downloaded files from the input folder into a single
file. Also, this process removes the duplicated documents. To preprocess
the example dataset (“Bluetooth low energy” located in dataInExample)
run this command inside ScientoPy folder:

    python3 preProcess.py dataInExample

The input folder is scanned **recursively**, so Scopus and WoS exports
can be organized in sub-folders. The pipeline is multi-core (parallel
Polars CSV reader + per-file row normalization) and prints its progress
as four numbered steps:

    [1/4] Loading papers
    [2/4] Disambiguating Scopus author names
    [3/4] Removing duplicates
    [4/4] Saving preprocessed corpus

Then, inside the folder `ScientoPy/dataPre` you will find the following
files:

-   **papersPreprocessed.parquet:** canonical preprocessed corpus stored
    as Apache Parquet (Zstd-compressed). Replaces the previous
    `papersPreprocessed.csv`. Used as input by every other ScientoPy
    script. Typically 5-15× smaller than the equivalent CSV and loads in
    well under a second even for 300 k-paper datasets. To obtain a CSV
    copy, use `exportPapers.py` (see below).

-   **PreprocessedBrief.csv:** this file briefs the pre-process statics
    results, such as duplicated papers removed, types of documents, and
    others.

To find more options of the preprocessing script you can run:

    python3 preProcess.py -h

Extract the top topics
----------------------

With this script you can extract the top topics of a selected criterion.
The ScientoPy criterion are described bellow:


- **author:** Authors last name and first name initial
- **sourceTitle:** Publication or journal name
- **subject:** Research areas, only from WoS documents
- **authorKeywords:** Author keywords
- **indexKeywords:** Keywords generated by the index, from WoS Keyword
Plus, and from Scopus Indexed keywords
- **bothKeywords:** AuthorKeywords and indexKeywords are used for this
search
- **abstract:** Document abstract, for use with pre-defined topics and
asterisk wildcard
- **documentType:** Type of document
- **dataBase:** Database where the document was extracted (WoS or
Scopus)
- **country:** Country extracted from authors affiliations
- **institution:** Institution extracted from authors affiliations
- **institutionWithCountry:** Institution with country extracted from
authors affiliations

For example, to find the top author keywords you can run this script:

    python3 scientoPy.py -c authorKeywords

This will generate a list with the top 10 topics on the selected
criterion (in this case authorKeywords), with the number of documents
per topic, and the h-index associated to each one. Also, this script
graphs the evolution of each topic per year, and saves the quantitative
results on the folder `ScientoPy/results`.

This script have more options like, save the plot on a file, or increase
the number of topic results. For more information you can run:

    python3 scientoPy.py -h

Analyze custom topics inside a criterion
----------------------------------------

If you want to make an analysis of custom topics, such as the two
selected countries papers evolution, you can use the `scientoPy.py`
script, with the option `-t`, to specify the topics:

    python3 scientoPy.py -c country -t "United States; Brazil"

You can analyze any topic in any criterion. Put the topics on the `-t`
argument. Divide the topics with the `;`. Also, you can integrate two or
more topics in one, by dividing it with `,`. This is very useful for
abbreviations and plural singulars, for example:

    python3 scientoPy.py -c authorKeywords -t \
    "WSN, Wireless sensor network, Wireless sensor networks; RFID, RADIO FREQUENCY IDENTIFICATION"

**Note:** The command is very long, for that reason the command was
divided by `\`. If you have problems in Windows, remove the "" and put
the command in one single line.

### Asterisk (\*) wildcard

You can use the asterisk wildcard to find phrases or words which starts
or ends with the letters that you have inserted. For example, if you
want to find “device”, “devices”, and “device integration”, enter the
following command:

    python3 scientoPy.py -c authorKeywords -t "device*"

ScientoPy will print the topics found for the previous search:

    Topics found for device*:
    "devices;device management;Device Interactions;Device objectification;Device;Device integration"

You can use this information, to analyze each specific topic found, like
this:

    python3 scientoPy.py -c authorKeywords -t \
    "devices;device management;Device Interactions;Device objectification;Device;Device integration"

### Merging synonyms

The same topic is often written in several ways: abbreviations
("IoT", "Internet of Things"), singular and plural, an author with and
without the middle initial, or an institution with two names. The
`--synonyms` option counts those names as one topic when ScientoPy finds
the top topics, in any criterion:

    python3 scientoPy.py -c authorKeywords \
    --synonyms "Internet of Things, IoT, Internet of Things (IoT); Bluetooth Low Energy, BLE"

Divide the groups with `;` and the names inside a group with `,`. The
first name of each group is the one shown in the results. A document
with several names of the same group counts once.

For long lists, `--synonyms` also takes a VOSviewer thesaurus file: a
tab separated text file with the header `label` and `replace by`. A name
with an empty `replace by` is left out of the results:

    python3 scientoPy.py -c institution --synonyms thesaurus_institutions.txt

The same option and file work in `scientoPyNetwork.py` and
`scientoPyThematicMap.py`, so the tables, the network map and the
thematic map use the same names.

### Evolution plot

Also, you can see the results with a evolution graphic (add
`-g evolution`). This option plot the accumulative documents, average
documents per year (ADY), and PDLY, for example:

    python3 scientoPy.py -c authorKeywords -t \
    "WSN, Wireless sensor network, Wireless sensor networks; RFID, RADIO FREQUENCY IDENTIFICATION" \
    -g evolution

This script have more options like, save the plot on a file, or others.
For more information you can run:

    python3 scientoPy.py -h

World map
---------

The `world_map` graph shades every country by its number of documents.
It needs the `country` criterion:

    python3 scientoPy.py -c country -g world_map

The map shows every country found in the dataset, while the results
table (`results/Country.csv`) keeps the top ones set by `-l`. Some
useful options:

    # Logarithmic color scale, to see the countries with few documents
    python3 scientoPy.py -c country -g world_map --yLog

    # Leave out the first two countries, to compare the others
    python3 scientoPy.py -c country -g world_map -s 2

    # Only the countries that publish with Canada, saved for a paper
    python3 scientoPy.py -c country -t "Canada" --noPlot
    python3 scientoPy.py -c country -r -g world_map --savePlot "canada_collaboration.eps"

Countries with no documents are gray. Countries too small to see at
this scale, like Singapore, get a dot. Names in the country field that
are not a country (errors in the affiliations of the dataset) are
listed in the console. The map works offline: the country outlines
(from Natural Earth, public domain) come with ScientoPy.

Finding trending topics
-----------------------

This script finds the top trending topics based on the higher average
growth rate (AGR) over the others. The AGR is calculated on two years
periods. 

To find the top trending topics on author keywords criterion, you can
run the following script:

    python3 scientoPy.py -c authorKeywords --trend --startYear 2008 --endYear 2018 \
    --windowWidth 2  --agrForGraph -g evolution

This script will find the top 200 topics, then it calculates the AGR for
the last 2 years (`--windowWidth 2`). Finally, the 200 top topics are
sorted from the highest AGR in the last 2 year period to the lower. The
first 3 AGR topics are filtered (they correspond to the keyword Internet
of things), and the next 10 topics are garph in a evolution plot.

For more information about the AGR calculation refer to the 
PDF manual:


    Manual/ScientoPy_user_manual.pdf


Analysis based on the previous results
--------------------------------------

ScientoPy writes a lightweight internal file with all the output
documents from the last run so subsequent analyses can chain off it.
For example:

    python3 scientoPy.py -c country -t "Canada" --noPlot

ScientoPy writes `results/lastAnalysis.parquet` with every document
whose authors are affiliated in Canada. Pass `-r` (or
`--previousResults`) on the next call to analyze that subset:

    python3 scientoPy.py -c authorKeywords -r -g bar

returns the top author keywords from papers affiliated in Canada.

    python3 scientoPy.py -c country -r -g bar

returns the countries that most commonly co-publish with Canada.

**Notes:**

-   `lastAnalysis.parquet` is only produced when `-r` /
    `--previousResults` is **not** used, so chained analyses do not
    overwrite it.
-   In previous versions this file was a CSV named
    `results/papersPreprocessed.csv`, re-written on every analysis. It
    is now replaced by the Parquet file; analyses no longer write any
    CSV automatically. Use `exportPapers.py` (or the **5. Export** GUI
    tab) to re-materialize a CSV on demand.

Exporting to CSV
----------------

The preprocessed corpus and the analysis results can be exported to
Scopus- or WoS-style CSVs on demand with `exportPapers.py`:

    # Full preprocessed corpus -> export/papersPreprocessed.csv (Scopus fields)
    python3 exportPapers.py

    # Same, but WoS-style field names
    python3 exportPapers.py --format wos

    # Copy the latest results/*.csv into export/results/
    python3 exportPapers.py --source results

    # Custom destination
    python3 exportPapers.py --source preprocessed --format scopus -o my_corpus.csv

Running `exportPapers.py` with no flags defaults to
`--source preprocessed --format scopus` and writes to
`export/papersPreprocessed.csv`. For the full option list run:

    python3 exportPapers.py -h

### Extended results (per-document)

The detailed extended-results CSV (`results/<Criterion>_extended.csv`,
one row per paper) is **not produced automatically** because it can
reach hundreds of thousands of rows on large corpora. To produce it,
either pass `--saveExtended` on the CLI:

    python3 scientoPy.py -c authorKeywords --saveExtended

or pick **Extended results (last analysis, per-document)** in the GUI
**5. Export** tab after running an analysis.

All export options are also available from the GUI in the **5. Export**
tab.

Network maps (VOSviewer style)
------------------------------

`scientoPyNetwork.py` builds a co-occurrence network of the top items of
a criterion and saves it as an interactive map that opens in the web
browser. Two items are linked when they appear in the same document, so
the same command maps keyword co-occurrence (`authorKeywords`,
`indexKeywords`, `bothKeywords`), co-authorship (`author`), country or
institution collaboration (`country`, `institution`,
`institutionWithCountry`) and WoS subject areas (`subject`).

    # Top 300 author keywords, opens graphs/AuthorKeywords_network.html
    python3 scientoPyNetwork.py -c authorKeywords

    # Merge synonyms and leave out the search terms
    python3 scientoPyNetwork.py -c authorKeywords \
        --synonyms "internet of things, iot; bluetooth low energy, ble" \
        --exclude "bluetooth low energy"

    # Country collaboration with fractional counting
    python3 scientoPyNetwork.py -c country --counting fractional

    # Co-authorship inside the documents found by the previous analysis
    python3 scientoPy.py -c country -t "Colombia" --noPlot
    python3 scientoPyNetwork.py -c author -r

The analysis follows VOSviewer: links are normalized with the association
strength, items are clustered by optimizing the VOSviewer quality function
(with a resolution parameter), and the map layout uses the VOS mapping
technique, in both 3D and 2D.

| Option | Description |
|---|---|
| `-c`, `--criterion` | Criterion to map, default `authorKeywords` |
| `-l`, `--length` | Maximum number of items, the top ones by occurrences, default 300 |
| `--minOccurrences` | Minimum number of documents per item, default 2 |
| `-s`, `--skipFirst` | Leave out the first N top items |
| `--exclude` | Items to leave out, separated by `;` |
| `--synonyms` | Synonym groups, `"a, a2; b, b2"` (the first one names the group), or a VOSviewer thesaurus file |
| `--startYear`, `--endYear` | Year range |
| `--counting` | `full` or `fractional` counting of co-occurrences |
| `--minLinkStrength` | Minimum link weight to keep a link |
| `--resolution` | Clustering resolution, higher gives more and smaller clusters, default 1 |
| `--minClusterSize` | Smaller clusters are merged into their most connected cluster, default 3 |
| `--cohesion` | Extra attraction inside clusters in the layout, `0` for the plain VOS mapping, default 0.5 |
| `-r`, `--previousResults` | Map the documents found by the last `scientoPy.py` run |
| `--graphTitle` | Title shown in the map |
| `--noOpen` | Do not open the web browser |

Besides the map, the script writes the items of every cluster to
`results/<Criterion>_network_clusters.csv`, one row per cluster, ready
for a table of keywords by cluster.

The map is a single HTML file that works offline in any recent browser
with WebGL2 (Chrome, Edge, Firefox, Safari). It includes:

- **Views:** network (clusters), overlay by average publication year or
  average citations, and density; 3D orbit or flat 2D, with animated
  transitions.
- **Crawler tour:** a spider walks the map one cluster at a time. It reads
  the items, probes the strongest links, and flags emerging items (recent
  and growing) and highly cited ones. A dashboard follows it with a
  crawl log, cluster progress, coverage radar, year heat map, and a
  momentum gauge (50 = same share of recent documents as the whole
  corpus).
- **Exploration:** search, click an item for its statistics, documents
  per year, strongest links and most cited documents, timeline playback
  of the map growth, and the `scientoPy.py` command to analyze it.
- **Exports:** neon PNG (2x, 4x), publication PNG and SVG (light
  background), 16:9, 9:16, and 1:1 videos of the full crawl tour (MP4 or
  WebM, depending on the browser), VOSviewer map and network files,
  GEXF for Gephi, CSV, and JSON.

The map makes no network requests. DOI links in the item details open
only when clicked.

In the GUI, the same options are in the **6. Network Map** tab.

Thematic map
------------

`scientoPyThematicMap.py` draws the thematic map (strategic diagram) of
a criterion. It groups the items that appear together in clusters, the
same clusters as `scientoPyNetwork.py` with the same options, and places
every cluster (a theme) by two values from Callon's co-word analysis:

- **Centrality (relevance degree):** strength of the links between the
  items of the theme and the items of the other themes. A central theme
  is tied to the rest of the field.
- **Density (development degree):** strength of the links between the
  items of the theme. A dense theme is well developed.

The link strength between two items is the equivalence index,
`e = c_ij² / (c_i · c_j)`, with `c_ij` the documents with both items and
`c_i`, `c_j` the documents with each one. Centrality is 10 times the sum
of `e` over the links to other themes, and density is 100 times the sum
of `e` over the links inside the theme, divided by its number of items.

    # Thematic map of the author keywords
    python3 scientoPyThematicMap.py -c authorKeywords

    # Merge synonyms, leave out the search terms and save the plot
    python3 scientoPyThematicMap.py -c authorKeywords \
        --synonyms "internet of things, iot; bluetooth low energy, ble" \
        -s 2 --savePlot "thematic_map.eps"

The dashed lines cross at the medians and split the map in four:

| Quadrant | Centrality | Density | Meaning |
|---|---|---|---|
| Motor themes (top right) | high | high | Developed and important for the field |
| Niche themes (top left) | low | high | Developed, but isolated from the rest |
| Emerging or declining themes (bottom left) | low | low | Weakly developed and marginal |
| Basic themes (bottom right) | high | low | Important for the field, but not developed |

The bubble area is the number of occurrences of the items of the theme,
and each bubble shows its top items. Items that never appear with
another item are not part of any theme.

`scientoPyThematicMap.py` takes the options of `scientoPyNetwork.py`
that select the items and the clusters (`-c`, `-l`, `--minOccurrences`,
`-s`, `--exclude`, `--synonyms`, `--startYear`, `--endYear`,
`--counting`, `--minLinkStrength`, `--resolution`, `--minClusterSize`,
`-r`), and these ones:

| Option | Description |
|---|---|
| `--labels` | Number of items written on each theme, default 3 |
| `--axes` | `rank` places the themes by their centrality and density ranks, which spreads them evenly (default). `value` places them by the values |
| `--savePlot` | Save the plot to a file in `graphs/` (png, eps, pdf, svg) |
| `--noPlot` | Only save the table |
| `--plotWidth`, `--plotHeight` | Plot size in inches |
| `--graphTitle` | Title of the plot |

The themes, with their centrality, density, quadrant and every item, are
saved to `results/<Criterion>_thematic_map.csv`.

In the GUI, use the **Thematic map** button of the **6. Network Map**
tab.

Most cited documents
--------------------

`topCitedPapers.py` lists the most cited documents of the dataset:

    # Top 10 most cited documents
    python3 topCitedPapers.py

    # Top 20, published from 2015 to 2024
    python3 topCitedPapers.py -l 20 --startYear 2015 --endYear 2024

    # Most cited documents about a topic
    python3 scientoPy.py -c authorKeywords -t "indoor positioning" --noPlot
    python3 topCitedPapers.py -r

The table is saved to `results/TopCitedPapers.csv` with the citations,
the citations per year (citations divided by the years since the
document was published), year, title, authors, source, document type,
DOI, and EID. The citations are the ones reported by Scopus or WoS when
the dataset was downloaded.

In the GUI, use the **Most cited documents** button of the
**2. Analysis** tab. It uses the year range and the topics length of
that tab, and shows the table in the **4. Extended Results** tab.

Output files and directories
----------------------------

After run some ScientoPy commands or after run all the example commands
by executing the script `exampleGenerateGraphs.sh` you will find the
following folder and files structure described bellow:

-   **dataInExample:** contains Scopus and WoS example data set for the
    search criteria “Bluetooth low energy” downloaded in April 2, 2026.
    This is the input example for preprocess script.

-   **dataPre:** output folder for the preprocess results, and input
    folder for scientoPy script.

    -   **papersPreprocessed.parquet:** canonical preprocessed corpus
        (Apache Parquet, Zstd-compressed). Replaces the old
        `papersPreprocessed.csv` as the input for every other ScientoPy
        script. Use `exportPapers.py` to obtain a CSV copy.

    -   **PreprocessedBrief.csv:** preproceses brief table that shows the
        preprocess results related to total papers found per data base, the
        omitted papers, the duplicated papers count per data base, and the
        total number of papers per paper type (Conference paper, article,
        review...)

-   **graphs:** graphs output folder for preprocess and scientoPy
    scripts

    -   **AuthorKeywords\_network.html:** interactive network map written
        by `scientoPyNetwork.py` (self-contained, open it in a browser).

-   **Manual:** folder with the pdf manual and example paper with
    scientoPy commands highlighted used for graph and tables generation.

-   **results:** output folder for scientoPy result output files

    -   **AuthorKeywords.csv:** scientoPy output file for the selected
        criterion (in this case authorKeywords) that shows the top topics or
        the custom topics with the total number of documents, the Average
        Growth Rate (AGR), the Average Documents per Year (ADY), the
        h-index, and the documents per each year.
    
    -   **AuthorKeywords\_extended.csv:** scientoPy output file for the
        selected criterion (in this case authorKeywords) that show the top
        or custom topics with the documents related to each one.

    -   **AuthorKeywords\_network.json**, **\_network\_nodes.csv**,
        **\_network\_links.csv**, **\_network\_clusters.csv**,
        **\_network.gexf**, **\_vosviewer\_map.txt**,
        **\_vosviewer\_network.txt:** network map data written by
        `scientoPyNetwork.py`: items with their cluster, occurrences,
        links, average year and citations, the links with their weights,
        and the items of every cluster. The VOSviewer files open in
        VOSviewer and the GEXF file in Gephi.

    -   **AuthorKeywords\_thematic\_map.csv:** themes of the thematic
        map written by `scientoPyThematicMap.py`, with their centrality,
        density, quadrant, and items.

    -   **TopCitedPapers.csv:** most cited documents written by
        `topCitedPapers.py`.

    -   **lastAnalysis.parquet:** internal file with the output papers
        from the last scientoPy script run. Used as input when the
        option `-r` or `--previousResults` is passed on the next run.

-   **export:** populated on demand by `exportPapers.py`. Default
    destinations are `export/papersPreprocessed.csv` (preprocessed
    corpus) and `export/results/` (copy of analysis CSVs).

BibTeX generation
-----------------

ScientoPy can automatically generate a BibTeX bibliography file from a
LaTeX document. Use the paper EID (found in the `EID` column of the
extended results file `results/*_extended.csv`) as the cite key in your
LaTeX document:

    \cite{WOS:000363238300013}

Then run the `generateBibtex.py` script:

    python3 generateBibtex.py latexExample/article_example.tex

This will create `latexExample/article_example_bibliography.bib` next to
the input file. The script:

- Extracts all `\cite{}` keys from the LaTeX document body
- Matches them against the preprocessed dataset (`dataPre/papersPreprocessed.parquet`)
- Generates `@Article{}` entries for journals/reviews and `@Inproceedings{}` for conference papers
- Handles author name formatting and LaTeX special character escaping

Reference the generated file in your LaTeX document:

    \bibliographystyle{unsrt}
    \bibliography{article_example_bibliography}

A Makefile is provided in `latexExample/` that automates the full
build (bibliography generation + pdflatex/bibtex compilation). Run
`make` inside that folder.

This feature is also available from the GUI via the **Generate BibTeX**
button on the Analysis tab.


ScientoPy graph types
=====================

ScientoPy has 6 different ways to graph the results described bellow:


| Graph type      | Argument        | Description                                                                                                                                       |
|-----------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Time line       | `-g time_line`     | Graphs the number of documents of each topic vs the publication year                                                                              |
| Horizontal bars | `-g bar`         | Graphs the total number of documents of each topic in horizontal bars                                                                             |
| Horizontal bars trends | `-g bar_trends`         | Graphs the total number of documents of each topic in horizontal bars, with the percentage of document published in the last years     |
| Word cloud      | `-g word_cloud`   | Generate a word cloud based on the topic total number of publications                                                                             |
| Evolution      | `-g evolution`  | Graphs two plots, one with the accumulative number of documents vs the publication year, and other with the average papers per year vs the percentage of documents in the last years |
| World map      | `-g world_map`  | Shades every country by its number of documents, only for the `country` criterion                                                                 |

The network map and the thematic map have their own scripts,
`scientoPyNetwork.py` and `scientoPyThematicMap.py`, described above.



To see graph examples refer to the PDF manual:

[Manual/ScientoPy_user_manual.pdf](./Manual/ScientoPy_user_manual.pdf)


## How to cite ScientoPy

If you use ScientoPy in a book, paper, website, technical report, etc., please include a reference to ScientoPy.

To cite ScientoPy, use the following [reference](https://link.springer.com/article/10.1007/s11192-019-03213-w):

> Ruiz-Rosero, J., Ramirez-Gonzalez, G., & Viveros-Delgado, J. (2019). Software survey: ScientoPy, a scientometric tool for topics trend analysis in scientific publications. Scientometrics, 1-24.

The bibtex entry for this is:

    @Article{Ruiz-Rosero2019,
        author="Ruiz-Rosero, Juan
        and Ramirez-Gonzalez, Gustavo
        and Viveros-Delgado, Jesus",
        title="Software survey: ScientoPy, a scientometric tool for topics trend analysis in scientific publications",
        journal="Scientometrics",
        year="2019",
        month="Nov",
        day="01",
        volume="121",
        number="2",
        pages="1165--1188",
        abstract="Bibliometric analysis is growing research filed supported in different tools. Some of these tools are based on network representation or thematic analysis. Despite years of tools development, still, there is the need to support merging information from different sources and enhancing longitudinal temporal analysis as part of trending topic evolution. We carried out a new scientometric open-source tool called ScientoPy and demonstrated it in a use case for the Internet of things topic. This tool contributes to merging problems from Scopus and Clarivate Web of Science sources, extracts and represents h-index for the analysis topic, and offers a set of possibilities for temporal analysis for authors, institutions, wildcards, and trending topics using four different visualizations options. This tool enables future bibliometric analysis in different emerging fields.",
        issn="1588-2861",
        doi="10.1007/s11192-019-03213-w",
        url="https://doi.org/10.1007/s11192-019-03213-w"
    }



## Authors

* **Juan Ruiz-Rosero** - *Initial work and documentation* 

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

<br>

# Additional Information
- ScientoPy will not transfer any information to other networked systems unless explicitly requested by any party involved with installing or operating it

<br>

# Sponsors
<table>
 <tbody>
  <tr>
   <td align="center"><img alt="[SignPath]" src="https://avatars.githubusercontent.com/u/34448643" height="30"/></td>
   <td>Free code signing on Windows provided by <a href="https://signpath.io/">SignPath.io</a>, certificate by <a href="https://signpath.org/">SignPath Foundation</a></td>
  </tr>
 </tbody>
</table>