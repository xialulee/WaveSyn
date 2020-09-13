# Created on Sun Sep 13 15:36 2020
# @author: Feng-cong Li

import hy

from pathlib import Path
import tkinter
from tkinter.ttk import Button

from PIL import ImageTk

from wavesynlib.fileutils.photoshop.psd import get_pil_image
from wavesynlib.languagecenter.wavesynscript import Scripting
from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk

from .widgets import load_grp



class PlaneWindow(FigureWindow):
    windowe_name = "WaveSyn-PlaneWindow"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def on_connect(self):
        super().on_connect()
        tool_tabs = self._tool_tabs
        widgets_desc = [load_grp]

        tab = tkinter.Frame(tool_tabs)
        widgets = hywidgets_to_tk(tab, widgets_desc, self.root_node.gui.balloon)
        tool_tabs.add(tab, text="Data")

        self._make_view_tab()
        self._make_marker_tab()
        self._make_export_tab()
        self._make_window_manager_tab()

        figure_book = self.figure_book

