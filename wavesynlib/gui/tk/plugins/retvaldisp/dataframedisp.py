from pandas import DataFrame
from tkinter.filedialog import asksaveasfilename

from wavesynlib.widgets.tk import dataframedisplay

from . import BasePlugin



class Plugin(BasePlugin):
    _type = DataFrame

    def action(self, data):
        if not self.test_data(data):
            return

        def saveas_cvs(data):
            files = [
                ("CSV Files", "*.csv"), 
                ("All Files", "*.*") ]
            filename = asksaveasfilename(filetypes=files, defaultextension=".csv")
            data.to_csv(filename)

        self.root_node.gui.console.show_tips([
            {
                "type":"link",
                "content":"Display in a window.",
                "command": lambda *args: dataframedisplay.show(data)},

            {
                "type":"link",
                "content":"Save as CSV file.",
                "command": lambda *args: saveas_cvs(data) }])

