from pandas import DataFrame
from tkinter import Toplevel

from wavesynlib.widgets.tk.scrolledtree import ScrolledTree



class Plugin:
    _type = DataFrame


    def __init__(self, root_node):
        self.__root = root_node


    def test_data(self, data):
        if isinstance(data, self._type):
            return True
        else:
            return False


    def action(self, data):
        if not self.test_data(data):
            return
        self.__root.gui.console.show_tips([{
            "type":"link",
            "content":"Display this DataFrame object in a window.",
            "command":lambda *args:self.show_dataframe(data)}])


    def show_dataframe(self, dataframe):
        win = Toplevel()
        win.title("WaveSyn-DataFrameDisplay")
        st = ScrolledTree(win)
        st.pack(fill="both", expand="yes")
        st.load_dataframe(dataframe)
        