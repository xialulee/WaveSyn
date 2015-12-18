# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:48:34 2014

@author: Feng-cong Li
"""
from __future__ import print_function, division

from Tkinter import *
from ttk import *
from tkFileDialog import asksaveasfilename
from PIL import ImageTk

from numpy import *
from scipy.io import savemat

from wavesynlib.application import Application, uiImagePath, ScriptCode, Scripting, WaveSynThread
from wavesynlib.basewindow import FigureWindow
from wavesynlib.guicomponents.tk import Group, ParamItem, ScrolledList
from wavesynlib.common import setMultiAttr, autoSubs

from wavesynlib.algorithms import pattern2corrmtx



class OptimizeGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__uiImages = []
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        frm = Frame(self)
        frm.pack(side=TOP)
        
        imageMLbl = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_M_Label.png')
        )
        self.__uiImages.append(imageMLbl)
        Label(frm, image=imageMLbl).pack(side=LEFT)
        
        self.__M = ParamItem(frm)
        self.__M.label.config(text='M')
        self.__M.entryWidth = 6
        self.__M.entryText = 10
        self.__M.entry.bind('<Return>', lambda dumb: self.onSolve())
        self.__M.checkFunc = self._app.checkInt
        self.__M.pack(side=RIGHT)
        
        self._app.balloon.bind_widget(frm, balloonmsg='The number of the array elements.')

        imageSolveBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Solve_Button.png')
        )
        self.__uiImages.append(imageSolveBtn)

        self.__btnSolve = Button(self, image=imageSolveBtn, command=self.onSolve)
        self.__btnSolve.pack(side=TOP)
        self._app.balloon.bind_widget(self.__btnSolve, balloonmsg='Launch the solver to synthesize the correlation matrix.')
        
        frm = Frame(self)
        frm.pack(side=TOP)
        imageDisplayBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Display_Button.png')
        )
        self.__uiImages.append(imageDisplayBtn)
        Label(frm, image=imageDisplayBtn).pack(side=LEFT)
        self.__bDisplay = IntVar(0)
        chkDisplay = Checkbutton(frm, text="Display", variable=self.__bDisplay)
        chkDisplay.pack(side=TOP)
        self._app.balloon.bind_widget(frm, balloonmsg='Display solver output.')
        
        self.name = 'Optimize'
                
    def onSolve(self):
        printCode   = True
        topwin = self.__topwin
        center, width = topwin.grpEdit.beamData
        topwin.figureBook.clear()
        

        topwin.setIdealPattern(center, width)
        topwin.plotIdealPattern()        
        # Create a new thread for solving the correlation matrix.
        def solveFunc():
            printCode   = True
            topwin.solve(M=self.__M.getInt(), display=self.__bDisplay.get())
        WaveSynThread.start(func=solveFunc)
        # Though method "start" will not return until the solve returns, the GUI will still 
        # responding to user input because Tk.update is called by start repeatedly.
        # While the thread is not alive, the optimization procedure is finished.                        
        topwin.plotCurrentData() 
        
        

class EditGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        frm = Frame(self)
        
        self.__center = ParamItem(frm)
        setMultiAttr(self.__center,        
            labelText   = 'center(deg)',        
            entryText   = 0,    
            checkFunc   = self._app.checkInt,
            entryWidth  = 5,    
            labelWidth  = 10
        )                       
        self.__center.pack(side=TOP)        
        self._app.balloon.bind_widget(self.__center, balloonmsg='Specify the beam center here.')
        
        self.__width = ParamItem(frm)
        setMultiAttr(self.__width,
            labelText   = 'width(deg)',
            entryText   = 20,
            checkFunc   = self._app.checkInt,
            entryWidth  = 5,
            labelWidth  = 10
        )
        self.__width.pack(side=TOP)
        self._app.balloon.bind_widget(self.__width, balloonmsg='Specify the beam width here.')
        
        self.__uiImages = []
                
                
        imageAddBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Add_Button.png')
        )
        self.__uiImages.append(imageAddBtn)
        btn = Button(frm, image=imageAddBtn, command=self.onAdd)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Add new beam to the ideal pattern.')
        
        imageDelBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Del_Button.png')
        )
        self.__uiImages.append(imageDelBtn)
        btn = Button(frm, image=imageDelBtn, command=self.onDel)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Remove the selected beam in the listbox.')
        
        imageClrBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Clear_Button.png')
        )
        self.__uiImages.append(imageClrBtn)
        btn = Button(frm, image=imageClrBtn, command=self.onClear)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Clear the listbox of the beam parameters.')
        
        imagePlotBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Plot_Button.png')
        )
        self.__uiImages.append(imagePlotBtn)
        btn = Button(frm, image=imagePlotBtn, command=self.onPlotIdealPattern)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Plot the ideal pattern.')
        
        frm.pack(side=LEFT, fill=Y)
        
        self.__paramlist = ScrolledList(self)
        self.__paramlist.list.config(height=4, width=10)
        self.__paramlist.pack(side=LEFT)
        self.name = 'Edit Ideal Pattern'
        
        self.optgrp = None
        
    def onAdd(self):
        self.__paramlist.list.insert(END, '{0}, {1}'.format(self.__center.getInt(), self.__width.getInt()))
        
    def onDel(self):
        self.__paramlist.list.delete(ANCHOR)
        
    def onClear(self):
        self.__paramlist.clear()
        
    def onPlotIdealPattern(self):
        printCode   = True
        center, width = self.beamData
        self.__topwin.setIdealPattern(center, width)
        self.__topwin.plotIdealPattern()
        
    @property
    def beamData(self):
        beamParams = self.__paramlist.list.get(0, END)
        if not beamParams:
            self._app.printError('An error occurred!')
            self._app.printTip(
                [
                    {
                        'type':'text',
                        'content':'''This exception happens when the listbox of the beam parameters are empty.
To make a valid ideal pattern, at least one beam should be specified.
'''
                    }
                ]
            )
            return
        center, width = zip(*[map(float, param.split(',')) for param in beamParams])
        return center, width            
        



class FileExportGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        
        frm = Frame(self)
        self.__uiImages = []
        imageMatFileBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_SaveMat_Button.png')
        )
        self.__uiImages.append(imageMatFileBtn)
        Button(frm, image=imageMatFileBtn, command=self.onSaveMat).pack(side=TOP)
        Button(frm, text='mat', width=6).pack(side=TOP)
        frm.pack(side=LEFT)
        
        frm = Frame(self)
        imageExcelFileBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_SaveExcel_Button.png')
        )
        self.__uiImages.append(imageExcelFileBtn)
        Button(frm, image=imageExcelFileBtn).pack(side=TOP)
        Button(frm, text='xlsx', width=6).pack(side=TOP)
        frm.pack(side=LEFT)
        
        self.name = 'Corr Matrix'
        
    def onSaveMat(self):
        printCode   = True
        filename = asksaveasfilename(filetypes=[('Matlab mat files', '*.mat')])
        if not filename:
            return
            
        def linkFunc(filename):
            printCode   = True
            clipboard   = Application.instance.clipboard
            clipboard.clear()
            clipboard.append(autoSubs('load $filename'))

        self.__topwin.saveMat(filename)
        tip = [
            {
                'type':'text', 
                'content':autoSubs('''The correlation matrix has been saved in the mat file "$filename" successully.
You can extract the data in Matlab using the following command:''')
            },
            {
                'type':'link', 
                'content':autoSubs('>> load $filename'),
                'command':lambda dumb: linkFunc(filename=filename)
            },
            {
                'type':'text', 
                'content':'''and variable named "R" will appear in your Matlab workspace.
(Click the underlined Matlab command and copy it to the clipboard)'''
            }
        ]
        self._app.printTip(tip)  



class PatternWindow(FigureWindow):                   
    windowName = 'WaveSyn-PatternFitting'        
    def __init__(self, *args, **kwargs):
        FigureWindow.__init__(self, *args, **kwargs)
        # The toolbar {
        toolTabs    = self.toolTabs
            # Algorithm tab {
        frmAlgo = Frame(toolTabs)
        grpSolve = OptimizeGroup(frmAlgo, topwin=self)
        grpSolve.pack(side=LEFT, fill=Y)
        grpEdit = EditGroup(frmAlgo, topwin=self)
        grpEdit.pack(side=LEFT, fill=Y)
        self.__grpEdit = grpEdit
        
        toolTabs.add(frmAlgo, text='Algorithm')
            # } End Algorithm tab
            
            # View Tab {
        self.makeViewTab()
            # } End View tab
        
            # Marker Tab {
        self.makeMarkerTab()
            #} End Marker tab
        
            # Export tab {
        self.makeExportTab()
        frmExport   = self.exportFrame
        grpExport = FileExportGroup(frmExport, topwin=self)
        grpExport.pack(side=LEFT, fill=Y)
            # } End Export tab
        # } End toolbar
        
        self.idealPattern = None
        self.angles = None


        figureBook  = self.figureBook
        figureBook.makeFigures(
            figureMeta=[
                dict(name='Cartesian'   , polar=False),
                dict(name='Polar'       , polar=True)
            ]        
        )
        figCart = figureBook[0]
        figCart.plotFunction = lambda *args, **kwargs: figCart.plot(*args, **kwargs)
        figPolar    = figureBook[1]
        figPolar.plotFunction = lambda angles, pattern, **kwargs: figPolar.plot(angles/180.*pi, pattern, **kwargs)
               
        self.angles = r_[-90:90.1:0.1]
        self.__problem = pattern2corrmtx.Problem()
        self.__piecewisePattern = pattern2corrmtx.PiecewisePattern()
        self.R = None
        
                
    @property
    def grpEdit(self):
        return self.__grpEdit
    
    @Scripting.printable    
    def setIdealPattern(self, center, width):
        self.__piecewisePattern.createPiecewisePattern(
            self.angles,
            center,
            width
        )

    @Scripting.printable    
    def plotIdealPattern(self):
        pattern = self.__piecewisePattern        
        self.figureBook.plot(
            pattern.samplesAngle, 
            pattern.samplesMagnitude,
            curveName='Ideal Pattern',
            color='b'
        )
    
    @Scripting.printable        
    def plotCurrentData(self):
        R   = self.R
        if R is None:
            pass # To do: raise a error
        self.figureBook.plot(self.angles, pattern2corrmtx.corrmtx2pattern(R, self.angles),
            curveName='Synthesized Pattern', color='g')
            
    @Scripting.printable    
    def solve(self, M, display=False):
        self.__problem.M = M
        self.__problem.idealPattern = self.__piecewisePattern
        self.R = self.__problem.solve(verbose=display)
        
    @Scripting.printable    
    def saveMat(self, filename, varname='R', format='5'):
        savemat(filename, {varname:self.R}, format=format)