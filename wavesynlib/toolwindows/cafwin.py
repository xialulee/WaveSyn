# -*- coding: utf-8 -*-
"""
Created on Tue Apr 07 15:37:47 2015

@author: Feng-cong Li
"""
from __future__ import print_function, division
from Tkinter import *
from ttk import *
from Tkinter import Frame
from tkSimpleDialog import askstring
from tkFileDialog import askopenfilename

from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt

from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.widgets.tk import Group 
from wavesynlib.widgets.labeledentry import LabeledEntry
from wavesynlib.algorithms import ambiguityfunction


class LoadGroup(Group):
    def __init__(self, *args, **kwargs):
        #self._app = app = Application.instance
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        Button(self, text='Load *.mat', command=self.onLoadClick).pack()
        paramX = LabeledEntry(self)
        paramX.label_text = 'x = '
        paramX.entry_width = 6
        paramX.pack()
        self.__paramX = paramX
        paramY = LabeledEntry(self)
        paramY.label_text = 'y = '
        paramY.entry_width = 6
        paramY.pack()
        self.__paramY = paramY
        self.name = 'Load'
        
    def onLoadClick(self):
        dialogParam = {'filetypes':[('Matlab', '.mat')]}
        filename = askopenfilename(**dialogParam)
        if not filename:
            return
        matData = loadmat(filename)
        xName = askstring('Variable Name', 'Enter the name of the 1st sequence:')
        self.__paramX.entry_text = xName
        x = matData[xName].flatten()
        yName = askstring('Variable Name', 'Enter the name of the 2nd sequence:')
        y = matData[yName].flatten()
        self.__paramY.entry_text = yName
        dcaf = np.abs(ambiguityfunction.discaf(x, y))
        self.__topwin.figure_book[0].show_image(dcaf)
        self.__topwin.caf   = dcaf
        
        
class ColormapGroup(Group):
    def __init__(self, *args, **kwargs):
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        
        # Todo: 3D surface of CAF
        
        # see http://matplotlib.org/examples/color/colormaps_reference.html
        self.__cmaps    = cmaps = {'Sequential':     ['Blues', 'BuGn', 'BuPu',
                                     'GnBu', 'Greens', 'Greys', 'Oranges', 'OrRd',
                                     'PuBu', 'PuBuGn', 'PuRd', 'Purples', 'RdPu',
                                     'Reds', 'YlGn', 'YlGnBu', 'YlOrBr', 'YlOrRd'],
                 'Sequential (2)': ['afmhot', 'autumn', 'bone', 'cool', 'copper',
                                     'gist_heat', 'gray', 'hot', 'pink',
                                     'spring', 'summer', 'winter'],
                 'Diverging':      ['BrBG', 'bwr', 'coolwarm', 'PiYG', 'PRGn', 'PuOr',
                                     'RdBu', 'RdGy', 'RdYlBu', 'RdYlGn', 'Spectral',
                                     'seismic'],
                 'Qualitative':    ['Accent', 'Dark2', 'Paired', 'Pastel1',
                                     'Pastel2', 'Set1', 'Set2', 'Set3'],
                 'Miscellaneous':  ['gist_earth', 'terrain', 'ocean', 'gist_stern',
                                     'brg', 'CMRmap', 'cubehelix',
                                     'gnuplot', 'gnuplot2', 'gist_ncar',
                                     'nipy_spectral', 'jet', 'rainbow',
                                     'gist_rainbow', 'hsv', 'flag', 'prism']}                

        self.__cmapCategoryList     = cmapCategoryList  = Combobox(self, values=cmaps.keys(), takefocus=1, stat='readonly', width=12)
        cmapCategoryList.current(0)
        cmapCategoryList.bind('<<ComboboxSelected>>', self.onCategorySelect)
        cmapCategoryList.pack()
        
        self.__cmapList             = cmapList          = Combobox(self, value=cmaps[cmapCategoryList.get()], takefocus=1, stat='readonly', width=12)
        cmapList.current(0)
        cmapList.pack()
        
        Button(self, text='Apply', command=self.onApplyClick).pack()

        self.name = 'Color Map'
        
    def onCategorySelect(self, event):
        self.__cmapList['values']   = self.__cmaps[self.__cmapCategoryList.get()]
        self.__cmapList.current(0)
        
    def onApplyClick(self):
        caf      = self.__topwin.caf
        if caf is not None:
            self.__topwin.figure_book[0].show_image(caf, cmap=plt.get_cmap(self.__cmapList.get()))
            
        
        
        
class CAFWindow(FigureWindow):
    window_name = 'WaveSyn-(Cross) Ambiguity Function'
    def __init__(self, *args, **kwargs):
        FigureWindow.__init__(self, *args, **kwargs)
        # The toolbar {
        tool_tabs = self._tool_tabs
            # Data tab {
        frmCAF = Frame(tool_tabs)
        grpLoad = LoadGroup(frmCAF, topwin = self)
        grpLoad.pack(side=LEFT, fill=Y)
        colormap_group     = ColormapGroup(frmCAF, topwin=self)
        colormap_group.pack(side=LEFT, fill=Y)
        tool_tabs.add(frmCAF, text='CAF')
            # } End data tab
        
        self._make_view_tab()
        self._make_marker_tab()
        #} End toolbar
        
        figure_book = self.figure_book
        figure_book.make_figures(
            figure_meta=[
                {'name':'discrete-CAF', 'polar':False}
            ]
        )
        
        self.caf    = None
