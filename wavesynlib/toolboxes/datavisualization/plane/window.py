# Created on Sun Sep 13 15:36 2020
# @author: Feng-cong Li

import hy

from pathlib import Path
from numpy import arctan2, ndarray, sqrt

import tkinter
from tkinter.ttk import Button
from tkinter.simpledialog import askstring

from PIL import ImageTk

from wavesynlib.fileutils.photoshop.psd import get_pil_image
from wavesynlib.languagecenter.wavesynscript import Scripting
from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk

from .widgets import load_grp
from .dialogs import ask_drawmode, ask_scatter_properties



class PlaneWindow(FigureWindow):
    window_name = "WaveSyn-PlaneWindow"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def on_connect(self):
        super().on_connect()
        tool_tabs = self._tool_tabs
        widgets_desc = [load_grp]

        tab = tkinter.Frame(tool_tabs)
        widgets = hywidgets_to_tk(tab, widgets_desc, self.root_node.gui.balloon)
        widgets["loadvar_btn"]["command"] = self.__on_load_var_btn_click
        tool_tabs.add(tab, text="Data")

        self._make_view_tab()
        self._make_marker_tab()
        self._make_export_tab()
        self._make_window_manager_tab()

        figure_book = self.figure_book
        figure_book.make_figures(
            figure_meta = [
                dict(name="Cartesian", polar=False),
                dict(name="Polar",     polar=True) ])


    def __on_load_var_btn_click(self):
        var_name = askstring("Var Name", "Please enter variable name:")
        data = Scripting.namespaces["locals"][var_name]
        drawmode = ask_drawmode()
        if drawmode == "scatter":
            prop = ask_scatter_properties()
            prop = {key:value for key, value in prop.items() if value is not None}
            #print(prop)
        self.__draw(drawmode, data, prop)


    def __cart_scatter(self, x, y, **prop):
        self.figure_book[0].scatter(x, y, **prop)


    def __polar_scatter(self, x, y, **prop):
        r = sqrt(x**2 + y**2)
        a = arctan2(y, x)
        self.figure_book[1].scatter(a, r, **prop)


    def __draw(self, drawmode, data, prop):
        def scatter():
            if isinstance(data, ndarray):
                x = data[:, 0]
                y = data[:, 1]
            self.figure_book[0].plot_function = self.__cart_scatter
            self.figure_book[1].plot_function = self.__polar_scatter
            self.figure_book.plot(x, y, **prop)
        funcs = {"scatter": scatter}
        funcs[drawmode]()
