from pandas import DataFrame
from tkinter.filedialog import asksaveasfilename

from wavesynlib.widgets.tk import dataframedisplay



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

        def saveas_cvs(data):
            files = [
                ("CSV Files", "*.csv"), 
                ("All Files", "*.*") ]
            filename = asksaveasfilename(filetypes=files, defaultextension=".csv")
            data.to_csv(filename)

        self.__root.gui.console.show_tips([
            {
                "type":"link",
                "content":"Display in a window.",
                "command": lambda *args: dataframedisplay.show(data)},

            {
                "type":"link",
                "content":"Save as CSV file.",
                "command": lambda *args: saveas_cvs(data) }])

