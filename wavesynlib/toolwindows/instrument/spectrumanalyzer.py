# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 16:40:36 2016

@author: Feng-cong Li
"""
import csv
import numpy as np

import tkinter as tk

import hy
from wavesynlib.widgets.tk.jsontotk import json_to_tk
from wavesynlib.widgets.tk.group import Group
from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.languagecenter.wavesynscript import Scripting, WaveSynScriptAPI, code_printer
from wavesynlib.interfaces.devcomm.instruments.visainterface import get_resource_manager


class RigolDSA1030Driver:
    def __init__(self, name=None):
        self.__name = name
        self.__instrument = None
        
        
    def connect(self, name=None):
        if name is None:
            name = self.__name
        else:
            self.__name = name
        
        if name is None:
            raise ValueError('The name of the instrument is needed.')
            
        rm = get_resource_manager()
        inst = rm.open_resource(name)
        self.__instrument = inst
    

    @property
    def instrument(self):
        return self.__instrument


    @property
    def frequency_start(self):
        return float(self.__instrument.ask(':SENS:FREQ:STAR?'))
        
        
    @property
    def frequency_stop(self):
        return float(self.__instrument.ask(':SENS:FREQ:STOP?'))
        
    
    @property
    def frequency_span(self):
        return float(self.__instrument.ask(':SENS:FREQ:SPAN?'))
        
    
    @property
    def frequency_center(self):
        return float(self.__instrument.ask(':SENS:FREQ:CENT?'))
        
        
    @property
    def traces(self):
        reader = csv.reader([self.__instrument.ask(':TRAC? '+'TRACE1')])
        data = reader.next()
        data[0] = data[0].split()[-1]
        return [np.array([float(d) for d in data])]



class SpectrumViewer(FigureWindow):
    window_name = 'WaveSyn-SpectrumViewer'
    
    def __init__(self, *args, **kwargs):
        FigureWindow.__init__(self, *args, **kwargs)
        
        tool_tabs = self._tool_tabs
        
        def on_refresh():
            with code_printer():
                self.refresh()
        
        widgets_desc = [
dict(
    class_=Group, pack=dict(side='left', fill='y'), setattr={'name':'Instrument'}, children=[
        dict(class_='LabeledEntry', name='entry_inst_name', setattr={'label_text':'Name', 'entry_width':8}),
        dict(class_='Button', pack=dict(fill='x'), config=dict(text='Connect', command=self._on_connect_click)),
        dict(class_='Button', pack=dict(fill='x'), config=dict(text='Refresh', command=on_refresh))
    ]
),        
        
dict(
    class_=Group, pack=dict(side='left', fill='y'), setattr={'name':'Frequency'}, children=[
        dict(class_='Label', name='label_start_stop'),
        dict(class_='Label', name='label_center_span')
    ]
)        
]
        tab = tk.Frame(tool_tabs)
        self.__tab_widgets = json_to_tk(tab, widgets_desc)
        tool_tabs.add(tab, text='Analyzer')
        
        self._make_view_tab()
        self._make_marker_tab()
        self._make_export_tab()
        self._make_window_manager_tab()
        
        figure_book = self.figure_book
        figure_book.make_figures(
            figure_meta = [
                dict(name='Curve', polar=False)
            ]
        )
        
                        
        self.__driver = None
        
        figure = figure_book[0]
        
        def plot_function(current_data, *args, **kwargs):
            driver = self.__driver
            start = driver.frequency_start
            stop = driver.frequency_stop
            point_num = len(current_data)
            frequencies = np.linspace(start, stop, point_num)
            figure.plot(frequencies, current_data, *args, **kwargs)
            
        figure.plot_function = plot_function
        
    
    @WaveSynScriptAPI            
    def connect(self, name):
        # To Do: Load driver dialog.
        self.__driver = driver = RigolDSA1030Driver(name)
        driver.connect()
        self.refresh()
        
        
        
    def _on_connect_click(self):
        name_entry = self.__tab_widgets['entry_inst_name']
        name = name_entry.entry_text
        self.connect(name)
        
    
    @WaveSynScriptAPI    
    def refresh(self):
        # To Do: Design a driver model for supporting different SAs.
        driver = self.__driver
        span = driver.frequency_span
        center = driver.frequency_center
        start = driver.frequency_start
        stop = driver.frequency_stop
        
        widgets = self.__tab_widgets
        widgets['label_start_stop']['text'] = 'start: {}, stop: {}'.format(start, stop)
        widgets['label_center_span']['text'] = 'center: {}, span: {}'.format(center, span)
        
        self.figure_book.clear()
        for trace in driver.traces:
            self.current_data = trace
            self.plot_current_data()
        
    
    


