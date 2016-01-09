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

from wavesynlib.application                  import Application, get_gui_image_path, WaveSynThread
from wavesynlib.basewindow                   import FigureWindow
from wavesynlib.guicomponents.tk             import Group, ParamItem, ScrolledList
from wavesynlib.languagecenter.utils         import auto_subs, set_attributes
from wavesynlib.languagecenter.wavesynscript import Scripting

from wavesynlib.algorithms import pattern2corrmtx



class OptimizeGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__gui_images = []
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        frm = Frame(self)
        frm.pack(side=TOP)
        
        imageMLbl = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_M_Label.png')
        )
        self.__gui_images.append(imageMLbl)
        Label(frm, image=imageMLbl).pack(side=LEFT)
        
        self.__M = ParamItem(frm)
        self.__M.label.config(text='M')
        self.__M.entry_width = 6
        self.__M.entry_text = 10
        self.__M.entry.bind('<Return>', lambda dumb: self._on_solve_button_click())
        self.__M.checker_function = self._app.check_int
        self.__M.pack(side=RIGHT)
        
        self._app.balloon.bind_widget(frm, balloonmsg='The number of the array elements.')

        imageSolveBtn = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_Solve_Button.png')
        )
        self.__gui_images.append(imageSolveBtn)

        self.__btnSolve = Button(self, image=imageSolveBtn, command=self._on_solve_button_click)
        self.__btnSolve.pack(side=TOP)
        self._app.balloon.bind_widget(self.__btnSolve, balloonmsg='Launch the solver to synthesize the correlation matrix.')
        
        frm = Frame(self)
        frm.pack(side=TOP)
        imageDisplayBtn = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_Display_Button.png')
        )
        self.__gui_images.append(imageDisplayBtn)
        Label(frm, image=imageDisplayBtn).pack(side=LEFT)
        self.__bDisplay = IntVar(0)
        chkDisplay = Checkbutton(frm, text="Display", variable=self.__bDisplay)
        chkDisplay.pack(side=TOP)
        self._app.balloon.bind_widget(frm, balloonmsg='Display solver output.')
        
        self.name = 'Optimize'
                
    def _on_solve_button_click(self):
        printCode   = True
        topwin = self.__topwin
        center, width = topwin.edit_group.beam_data
        topwin.figure_book.clear()
        

        topwin.set_ideal_pattern(center, width)
        topwin.plot_ideal_pattern()        
        # Create a new thread for solving the correlation matrix.
        def solveFunc():
            printCode   = True
            topwin.solve(M=self.__M.get_int(), display=self.__bDisplay.get())
        WaveSynThread.start(func=solveFunc)
        # Though method "start" will not return until the solve returns, the GUI will still 
        # responding to user input because Tk.update is called by start repeatedly.
        # While the thread is not alive, the optimization procedure is finished.                        
        topwin.plot_current_data() 
        
        

class EditGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        frm = Frame(self)
        
        self.__center = ParamItem(frm)
        set_attributes(self.__center,        
            label_text   = 'center(deg)',        
            entry_text   = 0,    
            checker_function   = self._app.check_int,
            entry_width  = 5,    
            label_width  = 10
        )                       
        self.__center.pack(side=TOP)        
        self._app.balloon.bind_widget(self.__center, balloonmsg='Specify the beam center here.')
        
        self.__width = ParamItem(frm)
        set_attributes(self.__width,
            label_text   = 'width(deg)',
            entry_text   = 20,
            checker_function   = self._app.check_int,
            entry_width  = 5,
            label_width  = 10
        )
        self.__width.pack(side=TOP)
        self._app.balloon.bind_widget(self.__width, balloonmsg='Specify the beam width here.')
        
        self.__gui_images = []
                
                
        imageAddBtn = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_Add_Button.png')
        )
        self.__gui_images.append(imageAddBtn)
        btn = Button(frm, image=imageAddBtn, command=self._on_add_button_click)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Add new beam to the ideal pattern.')
        
        imageDelBtn = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_Del_Button.png')
        )
        self.__gui_images.append(imageDelBtn)
        btn = Button(frm, image=imageDelBtn, command=self._on_delete_button_click)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Remove the selected beam in the listbox.')
        
        imageClrBtn = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_Clear_Button.png')
        )
        self.__gui_images.append(imageClrBtn)
        btn = Button(frm, image=imageClrBtn, command=self._on_clear_button_click)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Clear the listbox of the beam parameters.')
        
        imagePlotBtn = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_Plot_Button.png')
        )
        self.__gui_images.append(imagePlotBtn)
        btn = Button(frm, image=imagePlotBtn, command=self._on_plot_ideal_pattern)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Plot the ideal pattern.')
        
        frm.pack(side=LEFT, fill=Y)
        
        self.__paramlist = ScrolledList(self)
        self.__paramlist.list.config(height=4, width=10)
        self.__paramlist.pack(side=LEFT)
        self.name = 'Edit Ideal Pattern'
        
        self.optgrp = None
        
    def _on_add_button_click(self):
        self.__paramlist.list.insert(END, '{0}, {1}'.format(self.__center.get_int(), self.__width.get_int()))
        
    def _on_delete_button_click(self):
        self.__paramlist.list.delete(ANCHOR)
        
    def _on_clear_button_click(self):
        self.__paramlist.clear()
        
    def _on_plot_ideal_pattern(self):
        printCode   = True
        center, width = self.beam_data
        self.__topwin.set_ideal_pattern(center, width)
        self.__topwin.plot_ideal_pattern()
        
    @property
    def beam_data(self):
        beamParams = self.__paramlist.list.get(0, END)
        if not beamParams:
            self._app.print_error('An error occurred!')
            self._app.print_tip(
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
        self.__gui_images = []
        imageMatFileBtn = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_SaveMat_Button.png')
        )
        self.__gui_images.append(imageMatFileBtn)
        Button(frm, image=imageMatFileBtn, command=self._on_save_mat_file).pack(side=TOP)
        Button(frm, text='mat', width=6).pack(side=TOP)
        frm.pack(side=LEFT)
        
        frm = Frame(self)
        imageExcelFileBtn = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_SaveExcel_Button.png')
        )
        self.__gui_images.append(imageExcelFileBtn)
        Button(frm, image=imageExcelFileBtn).pack(side=TOP)
        Button(frm, text='xlsx', width=6).pack(side=TOP)
        frm.pack(side=LEFT)
        
        self.name = 'Corr Matrix'
        
    def _on_save_mat_file(self):
        printCode   = True
        filename = asksaveasfilename(filetypes=[('Matlab mat files', '*.mat')])
        if not filename:
            return
            
        def linkFunc(filename):
            printCode   = True
            clipboard   = Application.instance.clipboard
            clipboard.clear()
            clipboard.write(auto_subs('load $filename'))

        self.__topwin.save_mat_file(filename)
        tip = [
            {
                'type':'text', 
                'content':auto_subs('''The correlation matrix has been saved in the mat file "$filename" successully.
You can extract the data in Matlab using the following command:''')
            },
            {
                'type':'link', 
                'content':auto_subs('>> load $filename'),
                'command':lambda dumb: linkFunc(filename=filename)
            },
            {
                'type':'text', 
                'content':'''and variable named "R" will appear in your Matlab workspace.
(Click the underlined Matlab command and copy it to the clipboard)'''
            }
        ]
        self._app.print_tip(tip)  



class PatternWindow(FigureWindow):                   
    windowName = 'WaveSyn-PatternFitting'        
    def __init__(self, *args, **kwargs):
        FigureWindow.__init__(self, *args, **kwargs)
        # The toolbar {
        tool_tabs    = self.tool_tabs
            # Algorithm tab {
        frmAlgo = Frame(tool_tabs)
        grpSolve = OptimizeGroup(frmAlgo, topwin=self)
        grpSolve.pack(side=LEFT, fill=Y)
        edit_group = EditGroup(frmAlgo, topwin=self)
        edit_group.pack(side=LEFT, fill=Y)
        self.__edit_group = edit_group
        
        tool_tabs.add(frmAlgo, text='Algorithm')
            # } End Algorithm tab
            
            # View Tab {
        self.make_view_tab()
            # } End View tab
        
            # Marker Tab {
        self.make_marker_tab()
            #} End Marker tab
        
            # Export tab {
        self.make_export_tab()
        frmExport   = self.exportFrame
        grpExport = FileExportGroup(frmExport, topwin=self)
        grpExport.pack(side=LEFT, fill=Y)
            # } End Export tab
        # } End toolbar
        
        self.idealPattern = None
        self.angles = None


        figure_book  = self.figure_book
        figure_book.make_figures(
            figure_meta=[
                dict(name='Cartesian'   , polar=False),
                dict(name='Polar'       , polar=True)
            ]        
        )
        figCart = figure_book[0]
        figCart.plot_function = lambda *args, **kwargs: figCart.plot(*args, **kwargs)
        figPolar    = figure_book[1]
        figPolar.plot_function = lambda angles, pattern, **kwargs: figPolar.plot(angles/180.*pi, pattern, **kwargs)
               
        self.angles = r_[-90:90.1:0.1]
        self.__problem = pattern2corrmtx.Problem()
        self.__piecewisePattern = pattern2corrmtx.PiecewisePattern()
        self.R = None
        
                
    @property
    def edit_group(self):
        return self.__edit_group
    
    @Scripting.printable    
    def set_ideal_pattern(self, center, width):
        self.__piecewisePattern.createPiecewisePattern(
            self.angles,
            center,
            width
        )

    @Scripting.printable    
    def plot_ideal_pattern(self):
        pattern = self.__piecewisePattern        
        self.figure_book.plot(
            pattern.samplesAngle, 
            pattern.samplesMagnitude,
            curveName='Ideal Pattern',
            color='b'
        )
    
    @Scripting.printable        
    def plot_current_data(self):
        R   = self.R
        if R is None:
            pass # To do: raise a error
        self.figure_book.plot(self.angles, pattern2corrmtx.corrmtx2pattern(R, self.angles),
            curveName='Synthesized Pattern', color='g')
            
    @Scripting.printable    
    def solve(self, M, display=False):
        self.__problem.M = M
        self.__problem.idealPattern = self.__piecewisePattern
        self.R = self.__problem.solve(verbose=display)
        
    @Scripting.printable    
    def save_mat_file(self, filename, varname='R', format='5'):
        savemat(filename, {varname:self.R}, format=format)