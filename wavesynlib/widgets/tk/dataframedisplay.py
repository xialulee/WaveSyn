from tkinter import Toplevel

from wavesynlib.widgets.tk.labeledentry import LabeledEntry
from wavesynlib.widgets.tk.scrolledtree import ScrolledTree



def show(dataframe):
    win = Toplevel()
    win.title("WaveSyn-DataFrameDisplay")
    query_entry = LabeledEntry(win)
    query_entry.pack(fill="x", expand="yes")
    query_entry.label_text = "Query:"
    def query_func(event):
        if event.keysym == "Return":
            new_df = dataframe.query(query_entry.entry_text)
            show(new_df)
    query_entry.entry.bind("<Key>", query_func)
    st = ScrolledTree(win)
    st.pack(fill="both", expand="yes")
    st.load_dataframe(dataframe)
