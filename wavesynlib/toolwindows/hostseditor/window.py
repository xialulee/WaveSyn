import tkinter as tk

import hy
from wavesynlib.widgets.scrolledtree import ScrolledTree
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow



class TableView:
    def __init__(self, *args, **kwargs):
        self.__tree_view = tree_view = ScrolledTree(*args, **kwargs)
        tree_view.tree["columns"] = ("ip", "host_name", "comments")
        tree_view.hide_icon_column()
        tree_view.heading("ip", text="IP")
        tree_view.heading("host_name", text="Host Name")
        tree_view.heading("comments", text="Comments")


    def _add_entry(self, entry):
        self.__tree_view.insert("", "end", text="", values=entry)


    def pack(self, *args, **kwargs):
        self.__tree_view.pack(*args, **kwargs)



class Editor(TkToolWindow):
    window_name = "WaveSyn-HostsEditor"


    def __init__(self):
        super().__init__()
        self._make_window_manager_tab()
        self.__table = table = TableView(self.tk_object)
        table.pack(expand="yes", fill="both")
        

    def on_connect(self):
        super().on_connect()
        self.__load()


    def __load(self):
        path = self.root_node.interfaces.net.dns.hosts_file.get_path()
        with open(path) as f:
            table = self.__table
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                fields = line.split(maxsplit=2)
                if len(fields) < 2:
                    continue
                fields.append("")
                table._add_entry(fields[:3])
