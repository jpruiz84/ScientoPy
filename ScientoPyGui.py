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

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkinter import font

import tkinter.scrolledtext as scrolledtext
from PIL import ImageTk, Image
import globalVar
from PreProcessClass import PreProcessClass
from ScientoPyClass import ScientoPyClass
from generateBibtex import generateBibtex
import webbrowser
import os.path


class ScientoPyGui:
    def __init__(self):
        self.scientoPy = ScientoPyClass(from_gui=True)

        self.root = Tk()
        self.root.geometry("853x480")
        self.root.resizable(width=False, height=False)

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)

        self.root.option_add("*font", default_font)
        if os.path.exists('scientopy_icon.png'):
            self.root.iconphoto(True, PhotoImage(file="scientopy_icon.png"))

        self.root.title("ScientoPy")

        # Starting the tabs
        self.nb = ttk.Notebook(self.root)
        preprocess_page = Frame(self.nb)
        process_page = Frame(self.nb)

        self.nb.add(preprocess_page, text='1. Pre-processing')
        self.nb.add(process_page, text='2. Analysis')
        self.nb.pack(expand=1, fill="both")
        self.nb.select(preprocess_page)

        # Pre processing tab *******************************
        if os.path.exists('scientopy_logo.png'):
            load = Image.open("scientopy_logo.png")
            render = ImageTk.PhotoImage(load)
            img = Label(preprocess_page, image=render)
            img.image = render
            img.place(relx=0.5, rely=0.35, anchor=CENTER)

        version_label = Label(preprocess_page, text=("Universidad del Cauca, Popayán, Colombia"
                                                     "\nMIT License \nVersion %s" % globalVar.SCIENTOPY_VERSION))
        version_label.place(relx=0.5, rely=0.7, anchor=CENTER)

        Label(preprocess_page, text="Dataset folder:").grid(column=0, row=0, padx=17)

        preprocess_page.grid_rowconfigure(0, pad=700)

        self.datasetLoc = StringVar()
        preprocess_page.grid_columnconfigure(2, weight=1)
        self.datasetLocEntry = Entry(preprocess_page, textvariable=self.datasetLoc)
        # self.datasetLocEntry.place(relx=0.47, rely=0.8, anchor=CENTER)
        self.datasetLocEntry.grid(column=1, row=0, columnspan=2, sticky='we')

        dataset_button = Button(preprocess_page, text="Select dataset", command=self.select_dataset)
        # dataset_button.place(relx=0.9, rely=0.8, anchor=CENTER)
        dataset_button.grid(column=3, row=0, sticky='w', padx=17)

        self.chkValueRemoveDupl = BooleanVar()
        self.chkValueRemoveDupl.set(True)
        Checkbutton(preprocess_page, var=self.chkValueRemoveDupl,
                    text="Remove duplicated documents").place(relx=0.015, rely=0.9, anchor=W)

        # Buttons ****************************

        run_preprocess_button = Button(preprocess_page, text="Run preprocess", command=self.run_preprocess)
        run_preprocess_button.place(relx=0.9, rely=0.9, anchor=CENTER)

        open_preprocess_brief = Button(preprocess_page, text="Open preprocess brief",
                                       command=self.open_preprocess_brief)
        open_preprocess_brief.place(relx=0.57, rely=0.9, anchor=W)

        # Analysis tab ************************************************************

        Label(process_page, text="").grid(sticky=W, column=0, row=0)
        Label(process_page, text="Criterion:", borderwidth=10).grid(sticky=W, column=0, row=1)
        self.comboCriterion = ttk.Combobox(process_page, values=globalVar.validCriterion, width=15)
        self.comboCriterion.current(3)
        self.comboCriterion.grid(column=1, row=1)

        Label(process_page, text="Graph type:", borderwidth=10).grid(sticky=W, column=0, row=2)
        self.comboGraphType = ttk.Combobox(process_page, values=globalVar.validGrapTypes, width=15)
        self.comboGraphType.current(0)
        self.comboGraphType.grid(column=1, row=2)

        Label(process_page, text="Start Year:", borderwidth=10).grid(sticky=W, column=0, row=3)
        self.spinStartYear = Spinbox(process_page, from_=1900, to=2100,
                                     textvariable=DoubleVar(value=globalVar.DEFAULT_START_YEAR), width=15)
        self.spinStartYear.grid(column=1, row=3)

        Label(process_page, text="End Year:", borderwidth=10).grid(sticky=W, column=0, row=4)
        self.spinEndYear = Spinbox(process_page, from_=1900, to=2100,
                                   textvariable=DoubleVar(value=globalVar.DEFAULT_END_YEAR), width=15)
        self.spinEndYear.grid(column=1, row=4)

        Label(process_page, text="Topics length:", borderwidth=10).grid(sticky=W, column=0, row=5)
        self.spinTopicsLength = Spinbox(process_page, from_=0, to=1000, textvariable=DoubleVar(value=10),
                                        width=15)
        self.spinTopicsLength.grid(column=1, row=5)

        Label(process_page, text="Skip first:", borderwidth=10).grid(sticky=W, column=0, row=6)
        self.spinSkipFirst = Spinbox(process_page, from_=0, to=1000, textvariable=DoubleVar(value=0),
                                     width=15)
        self.spinSkipFirst.grid(column=1, row=6)

        Label(process_page, text="Window (years):", borderwidth=10).grid(sticky=W, column=0, row=7)
        self.spinWindowWidth = Spinbox(process_page, from_=1, to=100, textvariable=DoubleVar(value=2),
                                       width=15)
        self.spinWindowWidth.grid(column=1, row=7)

        self.chkValuePreviusResults = BooleanVar()
        self.chkValuePreviusResults.set(False)
        Checkbutton(process_page, var=self.chkValuePreviusResults,
                    text="Use previous results").grid(sticky=W, column=0, row=8, padx=7)

        self.chkValueTrendAnalysis = BooleanVar()
        self.chkValueTrendAnalysis.set(False)
        Checkbutton(process_page, var=self.chkValueTrendAnalysis,
                    text="Trend analysis").grid(sticky=W, column=0, row=9, padx=7)

        process_page.grid_columnconfigure(2, weight=1)

        Label(process_page, text="Custom topics:", borderwidth=10).grid(sticky=W, column=2, row=1, padx=15)
        self.entryCustomTopics = scrolledtext.ScrolledText(process_page, undo=True, height=18)
        self.entryCustomTopics.grid(column=2, row=2, rowspan=9, sticky=E, padx=25)

        # Buttons ****************************

        results_button = Button(process_page, text="Open results table", command=self.open_results)
        results_button.place(relx=0.008, rely=0.92, anchor=W)

        ext_results_button = Button(process_page, text="Open extended results", command=self.open_ext_results)
        ext_results_button.place(relx=0.20, rely=0.92, anchor=W)

        genbibtex_button = Button(process_page, text="Generate BibTeX", command=self.generate_bibtex)
        genbibtex_button.place(relx=0.45, rely=0.92, anchor=W)

        run_button = Button(process_page, text="Run", command=self.scientoPyRun)
        run_button.place(relx=0.96, rely=0.92, anchor=E)

    def open_results(self):
        if os.path.exists(self.scientoPy.resultsFileName):
            webbrowser.open(self.scientoPy.resultsFileName)
        else:
            messagebox.showinfo("Error", "No results found, please run the analysis first")

    def open_ext_results(self):
        if os.path.exists(self.scientoPy.extResultsFileName):
            webbrowser.open(self.scientoPy.extResultsFileName)
        else:
            messagebox.showinfo("Error", "No extended results found, please run the analysis first")

    def open_preprocess_brief(self):
        if os.path.exists(self.scientoPy.preprocessBriefFileName):
            webbrowser.open(self.scientoPy.preprocessBriefFileName)
        else:
            messagebox.showinfo("Error", "No preprocess breif found, please run the preprocess first")

    def scientoPyRun(self):
        if not os.path.exists(self.scientoPy.preprocessDatasetFile):
            messagebox.showinfo("Error", "No preprocess input dataset, please run the preprocess first")
            return

        print(self.chkValuePreviusResults.get())

        self.scientoPy.closePlot()

        self.scientoPy.criterion = self.comboCriterion.get()
        self.scientoPy.graphType = self.comboGraphType.get()
        self.scientoPy.startYear = int(self.spinStartYear.get())
        self.scientoPy.endYear = int(self.spinEndYear.get())
        self.scientoPy.length = int(self.spinTopicsLength.get())
        self.scientoPy.skipFirst = int(self.spinSkipFirst.get())
        self.scientoPy.windowWidth = int(self.spinWindowWidth.get())
        self.scientoPy.previousResults = self.chkValuePreviusResults.get()
        self.scientoPy.trend = self.chkValueTrendAnalysis.get()

        if bool(self.entryCustomTopics.get("1.0", END).strip()):
            self.scientoPy.topics = self.entryCustomTopics.get("1.0", END).replace("\n", ";")
        else:
            self.scientoPy.topics = ''

        self.scientoPy.scientoPy()

    def select_dataset(self):
        self.root.dir_name = filedialog.askdirectory()
        if not self.root.dir_name:
            return

        self.datasetLoc.set(self.root.dir_name)

    def run_preprocess(self):
        if self.datasetLoc.get():
            try:
                preprocess = PreProcessClass(from_gui=True)
                preprocess.dataInFolder = self.root.dir_name
                preprocess.noRemDupl = not self.chkValueRemoveDupl.get()
                totalPapers = preprocess.preprocess()
                if totalPapers == 0:
                    messagebox.showinfo("Error", "No valid dataset files found in: %s" % self.root.dir_name)
            except:
                messagebox.showinfo("Error", "No valid dataset folder")
        else:
            messagebox.showinfo("Error", "No dataset folder defined")

    def generate_bibtex(self):
        if not os.path.exists(self.scientoPy.preprocessDatasetFile):
            messagebox.showinfo("Error", "No preprocess input dataset, please run the preprocess first")
            return


        latexFileName = filedialog.askopenfilename(initialdir="./", title="Select the LaTeX file",
                                                   filetypes=(("Latex", "*.tex"), ("all files", "*.*")))
        if not latexFileName:
            return

        print(latexFileName)
        outFileName = generateBibtex(latexFileName)
        webbrowser.open(outFileName)

    def runGui(self):
        self.root.mainloop()


if __name__ == '__main__':
    scientoPyGui = ScientoPyGui()
    scientoPyGui.runGui()
