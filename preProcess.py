# !/usr/bin/python3

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

import argparse
from PreProcessClass import PreProcessClass

# Parse arguments
parser = argparse.ArgumentParser(description="Pre process and remove duplicates documents from Scopus and WoS")

parser.add_argument("dataInFolder", help="Folder where the Scopus or WoS data is located")

parser.add_argument("--noRemDupl",
                    help="To do not remove the duplicated documents", action="store_true")

parser.add_argument("--savePlot", default="",
                    help='Save the pre processed graph to a file, ex: --savePlot "preProcessed.eps"')

parser.add_argument("--graphTitle",
                    help="To put a title in the output graph", type=str)

args = parser.parse_args()

preProcess = PreProcessClass()
preProcess.preprocess(args)
