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
- Automatic BibTeX bibliography generation from LaTeX documents using paper EIDs as cite keys
- On-demand CSV export (Scopus or WoS field style) via `exportPapers.py` or the GUI Export tab
- Graphical user interface with five tabs (Pre-processing, Analysis, Results, Extended Results, Export)


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

ScientoPy has 5 different ways to graph the results described bellow:


| Graph type      | Argument        | Description                                                                                                                                       |
|-----------------|-----------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Time line       | `-g time_line`     | Graphs the number of documents of each topic vs the publication year                                                                              |
| Horizontal bars | `-g bar`         | Graphs the total number of documents of each topic in horizontal bars                                                                             |
| Horizontal bars trends | `-g bar_trends`         | Graphs the total number of documents of each topic in horizontal bars, with the percentage of document published in the last years     |
| Word cloud      | `-g word_cloud`   | Generate a word cloud based on the topic total number of publications                                                                             |
| Evolution      | `-g evolution`  | Graphs two plots, one with the accumulative number of documents vs the publication year, and other with the average papers per year vs the percentage of documents in the last years |



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


