# !/usr/bin/python3
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import tkinter.scrolledtext as scrolledtext
from PIL import ImageTk, Image
import globalVar
from PreProcessClass import PreProcessClass


def scientoPy():
    print("ScientoPy")



root = Tk()
root.geometry("853x480")
root.title("ScientoPy")

# Starting the tabs
nb = ttk.Notebook(root)
preprocess_page = Frame(nb)
process_page = Frame(nb)


nb.add(preprocess_page, text='Pre processing')
nb.add(process_page, text='Analysis')
nb.pack(expand=1, fill="both")
nb.select(process_page)

# Pre processing tab
img = ImageTk.PhotoImage(Image.open("scientopy_logo.png"))
logo_panel = Label(preprocess_page, image=img)
logo_panel.place(relx=0.5, rely=0.4, anchor=CENTER)

version_label = Label(preprocess_page, text=("Version %s" % globalVar.SCIENTOPY_VERSION))
version_label.place(relx=0.5, rely=0.7, anchor=CENTER)

def open_dataset():
    root.dir_name = filedialog.askdirectory()

    preprocess = PreProcessClass()
    preprocess.dataInFolder = root.dir_name
    #args2 = PreProcessArgs()
    #args2.dataInFolder = root.dir_name
    preprocess.preprocess()
    print(root.dir_name)

dataset_button = Button(preprocess_page, text="Select dataset", command=open_dataset)
dataset_button.place(relx=0.5, rely=0.9, anchor=CENTER)



# Analysis tab



Label(process_page, text="Criterion:", borderwidth=10).grid(sticky=W, column=0, row=0)
comboCriterion = ttk.Combobox(process_page, values=globalVar.validCriterion, width = 15)
comboCriterion.current(3)
comboCriterion.grid(column=1, row=0)

Label(process_page, text="Graph type:", borderwidth=10).grid(sticky=W, column=0, row=1)
comboGraphType = ttk.Combobox(process_page, values=globalVar.validGrapTypes, width = 15)
comboGraphType.current(0)
comboGraphType.grid(column=1, row=1)

Label(process_page, text="Start Year:", borderwidth=10).grid(sticky=W, column=0, row=3)
spinStartYear = Spinbox(process_page, from_=1900, to=2100, bg='white', textvariable=DoubleVar(value=1990), width = 15)
spinStartYear.grid(column=1, row=3)

Label(process_page, text="End Year:", borderwidth=10).grid(sticky=W, column=0, row=4)
spinEndYear = Spinbox(process_page, from_=1900, to=2100, bg='white', textvariable=DoubleVar(value=2019), width = 15)
spinEndYear.grid(column=1, row=4)

Label(process_page, text="Topics length:", borderwidth=10).grid(sticky=W, column=0, row=5)
spinTopicsLength = Spinbox(process_page, from_=0, to=1000, bg='white', textvariable=DoubleVar(value=10), width = 15)
spinTopicsLength.grid(column=1, row=5)

Label(process_page, text="Window (years):", borderwidth=10).grid(sticky=W, column=0, row=6)
spinTopicsLength = Spinbox(process_page, from_=0, to=100, bg='white', textvariable=DoubleVar(value=2), width = 15)
spinTopicsLength.grid(column=1, row=6)

process_page.grid_columnconfigure(2, pad=50)

Label(process_page, text="Custom topics:", borderwidth=10).grid(sticky=W, column=2, row=0, padx=15)
entryCustomTopics = scrolledtext.ScrolledText(process_page, undo=True,  bg='white', width=70, height=10)
entryCustomTopics.grid(column=2, row=1, rowspan=5)


run_button = Button(process_page, text="Run", command=scientoPy)
run_button.grid(column=0, row=7, sticky=W)

root.mainloop()
