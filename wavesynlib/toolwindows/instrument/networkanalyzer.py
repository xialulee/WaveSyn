# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 18:37:32 2016

@author: Feng-cong Li
"""
import os

import numpy as np
from skrf.io.touchstone import Touchstone

import six.moves.tkinter as tk

from wavesynlib.widgets.tk import json_to_tk
from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer


class TouchstoneViewer(FigureWindow):
    window_name = 'WaveSyn-TouchstoneViewer'
    
    def __init__(self, *args, **kwargs):
        FigureWindow.__init__(self, *args, **kwargs)
        
        tool_tabs = self._tool_tabs
        
        widgets_desc = [
dict(
    class_='Group', pack=dict(side='left', fill='y'), setattr={'name':'Load'}, children=[
        dict(class_='Button', config=dict(text='Load', command=self._on_load))
    ]
)
]

        tab = tk.Frame(tool_tabs)
        json_to_tk(tab, widgets_desc)
        tool_tabs.add(tab, text='S2P Files')
        
        self._make_view_tab()
        self._make_marker_tab()
        self._make_export_tab()
        self._make_window_manager_tab()
        
        figure_book = self.figure_book
        figure_book.make_figures(
            figure_meta = [
                dict(name='Real', polar=False),
                dict(name='Image', polar=False),
                dict(name='Mag (dB)', polar=False),
                dict(name='Phase (deg)', polar=False)
            ]
        )
        
        self.__freq_range = np.r_[0:1]
        
        
        real_figure = figure_book[0]
        real_figure.plot_function = lambda current_data, *args, **kwargs:\
            real_figure.plot(self.__freq_range, current_data.real, *args, **kwargs)        
            
        imag_figure = figure_book[1]
        imag_figure.plot_function = lambda current_data, *args, **kwargs:\
            imag_figure.plot(self.__freq_range, current_data.imag, *args, **kwargs)
            
        mag_figure = figure_book[2]
        mag_figure.plot_function = lambda current_data, *args, **kwargs:\
            mag_figure.plot(self.__freq_range, 20*np.log10(np.abs(current_data)), *args, **kwargs)
            
        phase_figure = figure_book[3]
        phase_figure.plot_function = lambda current_data, *args, **kwargs:\
            phase_figure.plot(self.__freq_range, np.angle(current_data)/2/np.pi*360, *args, **kwargs)
            
        self.__filename = ''
            
    def _on_load(self):
        with code_printer():
            self.load(self.root_node.lang_center.wavesynscript.constants.ASK_OPEN_FILENAME)
    
    @Scripting.printable
    def load(self, filename):
        kwargs = {}
        if self.__filename:
            kwargs['initialdir'] = os.path.split(self.__filename)[0]
        kwargs['filetypes'] = [('Touchstone Files', '*.s2p'), ('All Files', '*.*')]
        filename = self.root_node.gui.dialogs.constant_handler_ASK_OPEN_FILENAME(
            filename,
            **kwargs
        )
        if not filename:
            return
        s2p = Touchstone(str(filename))
        f, s = s2p.get_sparameter_arrays()
        self.__freq_range = f
        X, Y, Z = s.shape
        for y in range(Y):
            for z in range(Z):
                self.current_data = s[:, z, y]
                self.plot_current_data()
        self.__filename = filename
        
        