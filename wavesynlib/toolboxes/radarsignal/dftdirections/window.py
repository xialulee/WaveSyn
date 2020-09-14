import hy

from math import ceil, pi

from numpy import arcsin, ones_like, r_, rad2deg

from PIL import ImageTk

from tkinter import Frame
from tkinter.ttk import Button

from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.widgets.tk.group import Group
from wavesynlib.widgets.tk.scrolledlist import ScrolledList

from wavesynlib.languagecenter.datatypes.color import WaveSynColor
from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk

from .widgets import parameter_grp



class AmbiguityGroup(Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "Ambiguity"
        self._list = _list = ScrolledList(self)
        _list.list_config(height=4, width=10)
        _list.pack()



class DFTDirectionsWindow(FigureWindow):
    window_name = "WaveSyn-ULADFTDirections"


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def on_connect(self):
        super().on_connect()
        tool_tabs = self._tool_tabs

        self.__M = 0
        self.__d = 0

        array_frame = Frame(tool_tabs)

        widgets_desc = [parameter_grp]
        widgets = hywidgets_to_tk(array_frame, widgets_desc, self.root_node.gui.balloon)
        widgets["run_btn"]["command"] = lambda:\
            self.show_directions(
                M=widgets["num_elem_lent"].get_int(),
                d=widgets["dist_elem_lent"].get_float())

        self._ambig_group = ambig_group = AmbiguityGroup(array_frame)
        ambig_group.pack(side="left", fill="y")
        tool_tabs.add(array_frame, text="Array")

        self._make_view_tab()
        self._make_marker_tab()
        self._make_export_tab()

        self._make_window_manager_tab()

        figure_book = self.figure_book
        figure_book.make_figures(
            figure_meta=[
                {"name": "Cartesian", "polar":False},
                {"name":"Polar", "polar":True} ])

        fig_cart, fig_polar = figure_book
        fig_cart.plot_function = lambda *args, **kwargs: fig_cart.stem(*args, **kwargs)
        fig_polar.plot_function = lambda *args, **kwargs: fig_polar.stem(*args, **kwargs)

        @figure_book.add_observer
        def on_curve_selected(**kwargs):
            if "curve_selected" in kwargs:
                _list = self._ambig_group._list
                _list.clear()
                M = self.__M
                d = self.__d
                index = self.figure_book.selected_curve[0]
                k = index - M//2
                cd2 = ceil(d*2)
                steps = r_[(1-cd2):cd2] * M
                j = (k+steps)/d/M
                j = j[-1<=j]
                j = j[j<=1]
                j = arcsin(j)
                j = rad2deg(j)
                for i in j:
                    _list.append(f"{i: 3.2f}°")


    def show_directions(self, M, d):
        self._ambig_group._list.clear()
        self.__M = M
        self.__d = d
        self.figure_book.clear()
        k = r_[:M]
        k -= M//2
        cd2 = ceil(d*2)
        steps = r_[(1-cd2):cd2] * M
        for index, i in enumerate(k):
            j = (i+steps)/d/M
            j = j[-1<=j]
            j = j[j<=1]
            mag = ones_like(j)
            self.figure_book.plot(
                arcsin(j), 
                mag, 
                color=WaveSynColor(hsv=(index/(M+0.1*M), 1.0, 0.75)).to_matplotlib(),
                curve_name=f"{rad2deg(arcsin(i/d/M)): 3.2f}°")




