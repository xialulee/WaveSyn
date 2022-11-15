from math import ceil, pi

from numpy import array, arcsin, ones_like, r_, rad2deg, vstack, sin, cos

from PIL import ImageTk

from pandas import DataFrame
import quantities as pq

from tkinter import Frame
from tkinter.ttk import Button
from tkinter.simpledialog import askstring, askfloat

from wavesynlib.widgets.tk.figurewindow import FigureWindow
from wavesynlib.widgets.tk.group import Group
from wavesynlib.widgets.tk.scrolledlist import ScrolledList
from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk

from wavesynlib.languagecenter.datatypes.color import WaveSynColor
from wavesynlib.languagecenter.wavesynscript import (
    WaveSynScriptAPI, Scripting, code_printer)

from .widgets import parameter_grp, export_data_grp
from .dialogs import ask_dvplane, ask_export_to_console
from .algorithms import calc_directions



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
        self.__data = None


    def on_connect(self):
        super().on_connect()
        tool_tabs = self._tool_tabs

        self.__M = 0
        self.__d = 0

        array_frame = Frame(tool_tabs)

        widgets_desc = [parameter_grp]
        widgets = hywidgets_to_tk(array_frame, widgets_desc, self.root_node.gui.balloon)
        widgets["run_btn"]["command"] = self.__on_run_btn_click
        self.__array_tab = widgets

        self._ambig_group = ambig_group = AmbiguityGroup(array_frame)
        ambig_group.pack(side="left", fill="y")
        tool_tabs.add(array_frame, text="Array")

        self._make_view_tab()
        self._make_marker_tab()
        self._make_export_tab()
        export_widgets_desc = [export_data_grp]
        export_widgets = hywidgets_to_tk(
            self.export_frame, 
            export_widgets_desc,
            self.root_node.gui.balloon)
        export_widgets["export_to_console_btn"]["command"] = self.__on_export_to_console_btn_click
        export_widgets["export_to_dvplane_btn"]["command"] = self.__on_export_to_dvplane_btn_click

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
        def on_curve_selected(event):
            kwargs = event.kwargs
            if "curve_selected" in kwargs:
                _list = self._ambig_group._list
                _list.clear()
                index = self.figure_book.selected_curve[0]
                angle_coll = self.__data.loc[index].angle_coll
                for angle in angle_coll:
                    _list.append(f"{rad2deg(angle): 3.2f}°")


    @WaveSynScriptAPI
    def show_directions(self, num_elem, dist_elem):
        self._ambig_group._list.clear()
        self.__M = M = num_elem
        self.__d = d = dist_elem
        self.figure_book.clear()
        self.__array_tab["num_elem_lent"].entry_text = str(M)
        self.__array_tab["dist_elem_lent"].entry_text = str(d)

        self.__data = data = calc_directions(M, d)
        index_width = len(str(M))
        for index, row in data.iterrows():
            angle_coll = row.angle_coll
            mag = ones_like(angle_coll)
            self.figure_book.draw(
                angle_coll, 
                mag, 
                color=WaveSynColor(hsv=(index/(M+0.1*M), 1.0, 0.9)).to_matplotlib(),
                curve_name=f"{index:0{index_width}d}, {rad2deg(angle_coll[0]): 3.2f}°")


    @WaveSynScriptAPI
    def export_data_to_console(self, var_name, unit="rad"):
        unit = getattr(pq, unit)
        data = []
        for index, row in self.data.iterrows():
            data.append({
                "dft_index":  row.dft_index,
                "angle_coll": (row.angle_coll * pq.rad).rescale(unit)})
        data = DataFrame(data)
        Scripting.namespaces["locals"][var_name] = data


    @WaveSynScriptAPI
    def export_to_dvplane(self, winid, radius, data_info=None):
        if not data_info:
            data_info = {
                "source": "dftdirections",
                "name":   "" }
        if winid == "new":
            winid = self.root_node.gui.windows.create(
                module_name="wavesynlib.toolboxes.datavisualization.plane.window", 
                class_name="PlaneWindow")
        window = self.root_node.gui.windows[winid]

        angles = []
        for index, row in self.__data.iterrows():
            angles.extend(row.angle_coll)
        angles = array(angles)
        xy = vstack([radius*cos(angles), radius*sin(angles)])
        xy = xy.T

        window.draw_data(xy, data_info)


    @property
    def data(self):
        return self.__data


    def __on_run_btn_click(self):
        with code_printer():
            self.show_directions(
                num_elem=self.__array_tab["num_elem_lent"].get_int(),
                dist_elem=self.__array_tab["dist_elem_lent"].get_float())


    def __on_export_to_console_btn_click(self):
        varname, unit = ask_export_to_console()
        if not varname:
            raise ValueError("Variable name should not be empty. ")
        with code_printer():
            self.export_data_to_console(var_name=varname, unit=unit)


    def __on_export_to_dvplane_btn_click(self):
        sel_exist, winid_str = ask_dvplane(self)
        radius = askfloat(
            "Radius", 
            "Please input radius:",
            initialvalue=1.0)
        if sel_exist:
            winid = int(winid_str)
        else:
            winid = "new"
        with code_printer():
            self.export_to_dvplane(winid, radius=radius)



