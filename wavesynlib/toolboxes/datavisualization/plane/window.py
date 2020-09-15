# Created on Sun Sep 13 15:36 2020
# @author: Feng-cong Li

import hy

from pathlib import Path
from numpy import arange, arctan2, ndarray, sqrt, vstack

import tkinter
from tkinter.ttk import Button
from tkinter.simpledialog import askstring

from PIL import ImageTk

from shapely.geometry import Polygon

from wavesynlib.fileutils.photoshop.psd import get_pil_image
from wavesynlib.languagecenter.wavesynscript import Scripting
from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk

from .widgets import load_grp
from .dialogs import (
    ask_drawmode, 
    ask_plot_properties,
    ask_stem_properties,
    ask_scatter_properties)



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


    @staticmethod
    def __ask_draw_properties():
        drawmode = ask_drawmode()
        prop = {
            "plot": ask_plot_properties,
            "stem": ask_stem_properties,
            "scatter": ask_scatter_properties
        }[drawmode]()
        prop = {key:value for key, value in prop.items() if value is not None}
        return drawmode, prop


    def __on_load_var_btn_click(self):
        var_name = askstring("Var Name", "Please enter variable name:")
        data = Scripting.namespaces["locals"][var_name]
        drawmode, prop = self.__ask_draw_properties()
        data_info = {
            "source":   "console",
            "name":     var_name,
            "drawmode": drawmode}
        self.__draw(drawmode, data, data_info, prop)


    def draw_data(self, data, data_info):
        drawmode, prop = self.__ask_draw_properties()
        data_info["drawmode"] = drawmode
        self.__draw(drawmode, data, data_info, prop)


    @staticmethod
    def xy_to_ar(x, y):
        r = sqrt(x**2 + y**2)
        a = arctan2(y, x)
        return a, r


    def __cart_plot(self, *data, **prop):
        self.figure_book[0].plot(*data, **prop)


    def __polar_plot(self, *data, **prop):
        if len(data) == 1:
            y = data[0]
            x = arange(len(y))
        elif len(data) == 2:
            x = data[0]
            y = data[1]
        else:
            raise ValueError("Too many input data.")
        self.figure_book[1].plot(*self.xy_to_ar(x, y), **prop)


    def __cart_stem(self, *data, **prop):
        self.figure_book[0].stem(*data, **prop)


    def __polar_stem(self, *data, **prop):
        if len(data) == 1:
            y = data[0]
            x = arange(len(y))
        elif len(data) == 2:
            x = data[0]
            y = data[1]
        else:
            raise ValueError("Too many input data.")
        self.figure_book[1].stem(*self.xy_to_ar(x, y), **prop)


    def __cart_scatter(self, x, y, **prop):
        self.figure_book[0].scatter(x, y, **prop)


    def __polar_scatter(self, x, y, **prop):
        self.figure_book[1].scatter(*self.xy_to_ar(x, y), **prop)


    def __draw(self, drawmode, data, data_info, prop):
        if isinstance(data, Polygon):
            data_x, data_y = data.exterior.xy
            data = vstack([data_x, data_y]).T

        prop["curve_name"] = f"{data_info['source']}:{data_info['name']}:{data_info['drawmode']}"

        def scatter():
            if isinstance(data, ndarray):
                x = data[:, 0]
                y = data[:, 1]
            self.figure_book[0].plot_function = self.__cart_scatter
            self.figure_book[1].plot_function = self.__polar_scatter
            self.figure_book.plot(x, y, **prop)

        def handle_data_for_plot_stem():
            if isinstance(data, ndarray):
                if data.shape[1] == 1:
                    draw_data = [data]
                else:
                    draw_data = [data[:, 0], data[:, 1]]
                return draw_data

        def plot():
            line_data = handle_data_for_plot_stem()
            self.figure_book[0].plot_function = self.__cart_plot
            self.figure_book[1].plot_function = self.__polar_plot
            self.figure_book.plot(*line_data, **prop)

        def stem():
            stem_data = handle_data_for_plot_stem()
            self.figure_book[0].plot_function = self.__cart_stem
            self.figure_book[1].plot_function = self.__polar_stem
            self.figure_book.plot(*stem_data, **prop)

        funcs = {"scatter": scatter, "plot":plot, "stem":stem}
        funcs[drawmode]()
