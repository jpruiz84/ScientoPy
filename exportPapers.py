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

"""Explicit export of ScientoPy data to Scopus- or WoS-style CSVs.

Replaces the implicit `papersPreprocessed.csv` writes that used to happen
during preprocess and analysis. CLI entry point:

    exportPapers.py --source {preprocessed,results}
                    --format {scopus,wos}
                    [--output PATH]

See doc/performance_improvement_spec.md §5.9 for the design rationale.
"""

import argparse
import os
import shutil
import sys
import time

import globalVar
import paperIO
import paperSave


FORMAT_TO_GLOBAL = {
    "scopus": "SCOPUS_FIELDS",
    "wos": "WOS_FIELDS",
}


def _banner(source, fmt, output_path):
    """Print a friendly header to the CLI and update globalVar so the GUI
    progress dialog shows the same text before the first percentage tick.
    """
    title = "ScientoPy Export"
    bar = "=" * max(50, len(title))
    print("\n%s\n%s" % (title, bar))
    print("  Source:      %s" % source)
    print("  Format:      %s" % fmt)
    print("  Destination: %s" % output_path)
    print(bar)
    globalVar.progressText = "Exporting (%s -> %s)" % (source, fmt)
    globalVar.progressPer = 0


def export_preprocessed(fmt, output_path):
    """Export the full deduplicated corpus from dataPre/papersPreprocessed.parquet
    into a single CSV at `output_path`, using Scopus- or WoS-style fields.
    """
    parquet = os.path.join(globalVar.DATA_OUT_FOLDER, globalVar.OUTPUT_FILE_PARQUET)
    if not os.path.isfile(parquet):
        raise FileNotFoundError(
            "Preprocessed corpus not found at %s. Run preProcess.py first." % parquet
        )

    t0 = time.time()
    globalVar.progressText = "Reading preprocessed corpus..."
    globalVar.progressPer = 0
    print("  Reading %s ..." % parquet)
    papers = paperIO.read_preprocessed(parquet)
    print("  Loaded %d papers in %.1fs" % (len(papers), time.time() - t0))

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)

    globalVar.progressText = "Writing CSV (%s fields)" % fmt
    globalVar.progressPer = 0

    # paperSave.saveResults still keys off the module-level SAVE_RESULTS_ON.
    # The CLI --format flag wins: overwrite it for the duration of this call,
    # then restore the previous value so repeated invocations in a REPL stay
    # well-behaved.
    prev = globalVar.SAVE_RESULTS_ON
    try:
        globalVar.SAVE_RESULTS_ON = FORMAT_TO_GLOBAL[fmt]
        paperSave.saveResults(papers, output_path)
    finally:
        globalVar.SAVE_RESULTS_ON = prev

    print("Exported %d papers to %s (%s format)" % (len(papers), output_path, fmt))
    return output_path


def export_results(fmt, output_dir):
    """Copy the analysis-result CSVs currently in results/*.csv into
    `output_dir`. The top-results and extended-results CSVs are
    ScientoPy-native tables (Position, Total, AGR, ADY, …), not Scopus/WoS
    records, so `--format` only changes the filename style:
      - scopus: unchanged filenames
      - wos:    unchanged filenames (reserved for future WoS-specific
                reshaping of per-paper rows in the extended results)
    """
    src = globalVar.RESULTS_FOLDER
    if not os.path.isdir(src):
        raise FileNotFoundError("No results folder at %s" % src)

    # Collect CSVs except the transient lastAnalysis file used by -r.
    entries = [
        f
        for f in os.listdir(src)
        if f.lower().endswith(".csv") and f != globalVar.LAST_ANALYSIS_FILE
    ]
    if not entries:
        raise FileNotFoundError(
            "results/ is empty. Run scientoPy.py at least once before --source results."
        )

    os.makedirs(output_dir, exist_ok=True)
    globalVar.progressText = "Copying results CSVs"
    total = len(entries)
    for i, name in enumerate(entries):
        src_path = os.path.join(src, name)
        dst_path = os.path.join(output_dir, name)
        shutil.copy2(src_path, dst_path)
        print("Copied %s -> %s" % (src_path, dst_path))
        globalVar.progressPer = int((i + 1) * 100 / max(1, total))

    print("Exported %d result file(s) to %s (%s format)" % (len(entries), output_dir, fmt))
    return output_dir


def export(source, fmt, output=None):
    """Library entry point used by the GUI Export tab."""
    if source == "preprocessed":
        if output is None:
            output = os.path.join("export", globalVar.OUTPUT_FILE_NAME)
    elif source == "results":
        if output is None:
            output = os.path.join("export", "results")
    else:
        raise ValueError("Unknown source: %s" % source)

    _banner(source, fmt, output)
    try:
        if source == "preprocessed":
            result = export_preprocessed(fmt, output)
        else:
            result = export_results(fmt, output)
    finally:
        # Let the GUI's ProgressDialog close cleanly. Matches the 101 sentinel
        # used by preprocess / analysis so existing code paths work unchanged.
        globalVar.progressPer = 101
    return result


def build_parser():
    parser = argparse.ArgumentParser(
        description="Export ScientoPy preprocessed corpus or analysis results "
        "to Scopus- or WoS-style CSV files.",
        epilog="Run with no flags to export the preprocessed corpus in Scopus "
        "format to export/papersPreprocessed.csv.",
    )
    parser.add_argument(
        "--source",
        default="preprocessed",
        choices=["preprocessed", "results"],
        help="preprocessed (default): export "
        "dataPre/papersPreprocessed.parquet as a single CSV. "
        "results: copy the CSVs currently in results/ into the "
        "destination folder.",
    )
    parser.add_argument(
        "--format",
        default="scopus",
        choices=["scopus", "wos"],
        help="Column-naming convention for the export (default: scopus).",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Destination file (preprocessed) or directory (results). "
        "Defaults: export/papersPreprocessed.csv  /  export/results/",
    )
    return parser


def main():
    args = build_parser().parse_args()
    try:
        export(args.source, args.format, args.output)
    except (FileNotFoundError, ValueError) as e:
        print("ERROR: %s" % e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
