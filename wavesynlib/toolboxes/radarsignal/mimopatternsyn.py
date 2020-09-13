# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:48:34 2014

@author: Feng-cong Li
"""
from tkinter import IntVar, Frame
from tkinter.ttk import Button, Checkbutton
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror

from PIL import ImageTk

from numpy import r_, pi
from scipy.io import savemat

import _thread as thread

import hy
from wavesynlib.toolwindows.figurewindow import FigureWindow
from wavesynlib.widgets.tk.group import Group 
from wavesynlib.widgets.tk.scrolledlist import ScrolledList
from wavesynlib.widgets.tk.labeledentry import LabeledEntry
from wavesynlib.languagecenter.utils import auto_subs, set_attributes
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer, WaveSynScriptAPI
from wavesynlib.algorithms import pattern2corrmtx



class OptimizeGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Scripting.root_node
        self.__gui_images = []
        self.__topwin = kwargs.pop('topwin')
        super().__init__(*args, **kwargs)
        
        imageMLbl = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('Pattern_M_Label.png')
        )
        self.__gui_images.append(imageMLbl)        
        self.__M = LabeledEntry(self)
        self.__M.label.config(text='M', image=imageMLbl, compound='left')
        self.__M.entry_width = 6
        self.__M.entry_text = 10
        self.__M.entry.bind(
            '<Return>', 
            lambda dumb: self._on_solve_button_click())
        self.__M.checker_function = self._app.gui.value_checker.check_int
        self.__M.pack()
        
        self._app.gui.balloon.bind_widget(
            self.__M, 
            balloonmsg='The number of the array elements.')

        image_solve = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('run20x20.png'))
        self.__gui_images.append(image_solve)

        self.__btnSolve = Button(
            self, 
            text='Solve', 
            image=image_solve, 
            compound='left', 
            command=self._on_solve_button_click)
        self.__btnSolve.pack(side='top', fill='x')
        self._app.gui.balloon.bind_widget(
            self.__btnSolve, 
            balloonmsg='Launch the solver to synthesize the correlation matrix.')
        
        image_display = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('Pattern_Display_Button.png'))
        self.__gui_images.append(image_display)
        self.__bDisplay = IntVar(0)
        chk_display = Checkbutton(
            self, 
            text="Display", 
            image=image_display, 
            compound='left', 
            variable=self.__bDisplay)
        chk_display.pack(side='top')
        self._app.gui.balloon.bind_widget(
            chk_display, 
            balloonmsg='Display solver output.')
        chk_display_width = chk_display.winfo_width()
        self.__btnSolve['width'] = chk_display_width
        
        self.name = 'Optimize'
        
                
    def _on_solve_button_click(self):
        with code_printer():
            topwin = self.__topwin
            beam_data = topwin.edit_group.beam_data
            if not beam_data:
                showerror('Error', 'Please input the specification of the ideal beam pattern.')
                return
            topwin.figure_book.clear()        
            topwin.set_ideal_pattern(*beam_data)
            topwin.plot_ideal_pattern()        

        M = self.__M.get_int()
        display = self.__bDisplay.get()            

        with code_printer():
            topwin.solve.new_thread_run(M=M, verbose=bool(display), on_finish=["plot"])



class EditGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Scripting.root_node
        self.__topwin = kwargs.pop('topwin')
        super().__init__(*args, **kwargs)
        frm = Frame(self)
        
        self.__center = LabeledEntry(frm)
        set_attributes(self.__center,        
            label_text   = 'center(deg)',        
            entry_text   = 0,    
            checker_function   = self._app.gui.value_checker.check_int,
            entry_width  = 5,    
            label_width  = 10
        )                       
        self.__center.pack(side='top')        
        self._app.gui.balloon.bind_widget(
            self.__center, 
            balloonmsg='Specify the beam center here.')
        
        self.__width = LabeledEntry(frm)
        set_attributes(self.__width,
            label_text   = 'width(deg)',
            entry_text   = 20,
            checker_function   = self._app.gui.value_checker.check_int,
            entry_width  = 5,
            label_width  = 10
        )
        self.__width.pack(side='top')
        self._app.gui.balloon.bind_widget(
            self.__width, 
            balloonmsg='Specify the beam width here.')
        
        self.__gui_images = []
                
                
        imageAddBtn = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('Pattern_Add_Button.png'))
        self.__gui_images.append(imageAddBtn)
        btn = Button(frm, image=imageAddBtn, command=self._on_add_button_click)
        btn.pack(side='left')
        self._app.gui.balloon.bind_widget(btn, balloonmsg='Add new beam to the ideal pattern.')
        
        imageDelBtn = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('Pattern_Del_Button.png'))
        self.__gui_images.append(imageDelBtn)
        btn = Button(
            frm, 
            image=imageDelBtn, 
            command=self._on_delete_button_click)
        btn.pack(side='left')
        self._app.gui.balloon.bind_widget(
            btn, 
            balloonmsg='Remove the selected beam in the listbox.')
        
        imageClrBtn = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('Pattern_Clear_Button.png'))
        self.__gui_images.append(imageClrBtn)
        btn = Button(
            frm, 
            image=imageClrBtn, 
            command=self._on_clear_button_click)
        btn.pack(side='left')
        self._app.gui.balloon.bind_widget(
            btn, 
            balloonmsg='Clear the listbox of the beam parameters.')
        
        imagePlotBtn = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('Pattern_Plot_Button.png'))
        self.__gui_images.append(imagePlotBtn)
        btn = Button(
            frm, 
            image=imagePlotBtn, 
            command=self._on_plot_ideal_pattern)
        btn.pack(side='left')
        self._app.gui.balloon.bind_widget(
            btn, 
            balloonmsg='Plot the ideal pattern.')
        
        frm.pack(side='left', fill='y')
        
        self.__paramlist = ScrolledList(self)
        self.__paramlist.list.config(height=4, width=10)
        self.__paramlist.pack(side='left')
        self.name = 'Edit Ideal Pattern'
        
        self.optgrp = None
        
        
    def _on_add_button_click(self):
        self.__paramlist.list.insert('end', f'{self.__center.get_int()}, {self.__width.get_int()}')
        
        
    def _on_delete_button_click(self):
        self.__paramlist.list.delete('anchor')
        
        
    def _on_clear_button_click(self):
        self.__paramlist.clear()
        
        
    def _on_plot_ideal_pattern(self):
        with code_printer():
            center, width = self.beam_data
            self.__topwin.set_ideal_pattern(center, width)
            self.__topwin.plot_ideal_pattern()
            
        
    @property
    def beam_data(self):
        beamParams = self.__paramlist.list.get(0, 'end')
        if not beamParams:
            self._app.print_error('An error occurred!')
            self._app.gui.console.show_tips(
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
        self._app = Scripting.root_node
        self.__topwin = kwargs.pop('topwin')
        super().__init__(*args, **kwargs)
        
        frm = Frame(self)
        self.__gui_images = []
        imageMatFileBtn = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('Pattern_SaveMat_Button.png'))
        self.__gui_images.append(imageMatFileBtn)
        Button(
            frm, 
            image=imageMatFileBtn, 
            command=self._on_save_mat_file).pack(side='top')
        Button(
            frm, 
            text='mat', 
            width=6).pack(side='top')
        frm.pack(side='left')
        
        frm = Frame(self)
        imageExcelFileBtn = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('Pattern_SaveExcel_Button.png'))
        self.__gui_images.append(imageExcelFileBtn)
        Button(frm, image=imageExcelFileBtn).pack(side='top')
        Button(frm, text='xlsx', width=6).pack(side='top')
        frm.pack(side='left')
        
        self.name = 'Corr Matrix'
        
        
    def _on_save_mat_file(self):
        filename = asksaveasfilename(filetypes=[('Matlab mat files', '*.mat')])
        if not filename:
            return
            
        def linkFunc(filename):
            with code_printer():
                clipboard   = Scripting.root_node.interfaces.os.clipboard
                clipboard.clear()
                clipboard.write(auto_subs('load $filename'))
        with code_printer():
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
            self._app.gui.console.show_tips(tip)  



class PatternWindow(FigureWindow):                   
    window_name = 'WaveSyn-PatternFitting'        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The toolbar {
        tool_tabs = self._tool_tabs
            # Algorithm tab {
        frmAlgo = Frame(tool_tabs)
        grpSolve = OptimizeGroup(frmAlgo, topwin=self)
        grpSolve.pack(side='left', fill='y')
        edit_group = EditGroup(frmAlgo, topwin=self)
        edit_group.pack(side='left', fill='y')
        self.__edit_group = edit_group
        
        tool_tabs.add(frmAlgo, text='Algorithm')
            # } End Algorithm tab
            
            # View Tab {
        self._make_view_tab()
            # } End View tab
        
            # Marker Tab {
        self._make_marker_tab()
            #} End Marker tab
        
            # Export tab {
        self._make_export_tab()
        frmExport   = self.export_frame
        grpExport = FileExportGroup(frmExport, topwin=self)
        grpExport.pack(side='left', fill='y')
            # } End Export tab
        
        self._make_window_manager_tab()
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
        figCart.plot_function = lambda *args, **kwargs: \
            figCart.plot(*args, **kwargs)
        figPolar = figure_book[1]
        figPolar.plot_function = lambda angles, pattern, **kwargs: \
            figPolar.plot(angles/180.*pi, pattern, **kwargs)
               
        self.angles = r_[-90:90.1:0.1]
        self.__problem = pattern2corrmtx.Problem()
        self.__piecewisePattern = pattern2corrmtx.PiecewisePattern()
        self.R = None
        
                
    @property
    def edit_group(self):
        return self.__edit_group
    
    
    @WaveSynScriptAPI    
    def set_ideal_pattern(self, center, width):
        self.__piecewisePattern.createPiecewisePattern(
            self.angles,
            center,
            width)
        

    @WaveSynScriptAPI    
    def plot_ideal_pattern(self):
        pattern = self.__piecewisePattern        
        self.figure_book.plot(
            pattern.samplesAngle, 
            pattern.samplesMagnitude,
            curve_name='Ideal Pattern',
            color='b')
        
    
    @WaveSynScriptAPI        
    def plot_current_data(self):
        R   = self.R
        if R is None:
            pass # To do: raise a error
#        self.figure_book.plot(self.angles, pattern2corrmtx.corrmtx2pattern(R, self.angles),
#            curve_name='Synthesized Pattern', color='g')
        self.plot(R)
        
            
    def plot(self, data):
        self.figure_book.plot(
            self.angles, 
            pattern2corrmtx.corrmtx2pattern(data, self.angles), 
            curve_name='Synthesized Pattern', 
            color='g')
        
            
    @WaveSynScriptAPI(thread_safe=True)    
    def solve(self, M, verbose=False, on_finish=[]):
        self.__problem.M = M
        self.__problem.idealPattern = self.__piecewisePattern
        self.R = self.__problem.solve(verbose=verbose)
        if "plot" in on_finish:
            @self.root_node.thread_manager.main_thread_do(block=False)
            def plot():
                self.plot_current_data()
        return self.R

        
    @WaveSynScriptAPI    
    def save_mat_file(self, filename, varname='R', format='5'):
        savemat(filename, {varname:self.R}, format=format)
