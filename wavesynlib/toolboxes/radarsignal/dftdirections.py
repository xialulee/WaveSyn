import hy

from math import ceil, pi

from numpy import arcsin, ones_like, r_, rad2deg

from PIL import ImageTk

from tkinter import Frame
from tkinter.ttk import Button

from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.widgets.tk.group import Group
from wavesynlib.widgets.tk.labeledentry import LabeledEntry
from wavesynlib.widgets.tk.scrolledlist import ScrolledList

from wavesynlib.languagecenter.datatypes.color import WaveSynColor
from wavesynlib.languagecenter.wavesynscript import Scripting



class ParametersGroup(Group):
    def __init__(self, *args, **kwargs):
        self.__topwin = topwin = kwargs.pop("topwin")
        super().__init__(*args, **kwargs)
        self.name = "Parameters"
        self.__gui_images = gui_images = []
        image_m = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path("Pattern_M_Label.png"))
        gui_images.append(image_m)
        self.__M = LabeledEntry(self)
        self.__M.label.config(text="M", image=image_m, compound="left")
        self.__M.label_width = 3
        self.__M.entry_width = 6
        self.__M.entry_text = 16
        self.__M.checker_function = Scripting.root_node.gui.value_checker.check_int
        self.__M.pack()
        Scripting.root_node.gui.balloon.bind_widget(
            self.__M,
            balloonmsg="The number of the array elements.")

        image_d = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path("Pattern_d_Label.png"))
        gui_images.append(image_d)
        self.__d = LabeledEntry(self)
        self.__d.label.config(text="d", image=image_d, compound="left")
        self.__d.label_width = 3
        self.__d.entry_width = 6
        self.__d.entry_text = 0.5
        self.__d.checker_function = Scripting.root_node.gui.value_checker.check_positive_float
        self.__d.pack()
        Scripting.root_node.gui.balloon.bind_widget(
            self.__d,
            balloonmsg="The space between elements (with respect to wavelength)")

        image_run = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path("run20x20.png"))
        gui_images.append(image_run)
        run_button = Button(
            self,
            text="",
            image=image_run,
            compound="left",
            command=lambda:topwin.show_directions(M=self.__M.get_int(), d=self.__d.get_float()))
        run_button.pack(side="top", fill="x")



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
        tool_tabs = self._tool_tabs

        self.__M = 0
        self.__d = 0

        array_frame = Frame(tool_tabs)
        param_group = ParametersGroup(array_frame, topwin=self)
        param_group.pack(side="left", fill="y")
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
                # print(self.figure_book.selected_curve)
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




