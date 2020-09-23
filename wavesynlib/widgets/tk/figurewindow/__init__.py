# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:58:34 2014

@author: Feng-cong Li
"""
from tkinter.colorchooser import askcolor
from tkinter import IntVar, StringVar, Toplevel, Frame, Label
from tkinter.ttk import Button, Checkbutton, Combobox
from tkinter.filedialog import asksaveasfilename
from tkinter.simpledialog import askstring

from PIL import ImageTk

import matplotlib

from numpy import deg2rad, rad2deg, ndarray

import hy
from wavesynlib.widgets.tk.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.wavesynscript import (
    Scripting, WaveSynScriptAPI, code_printer)
from wavesynlib.languagecenter.utils import set_attributes
from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.widgets.tk.group import Group
from wavesynlib.widgets.tk.scrolledlist import ScrolledList
from wavesynlib.widgets.tk.labeledentry import LabeledEntry
from wavesynlib.widgets.tk.labeledscale import LabeledScale
from wavesynlib.fileutils.photoshop import psd

from .figurebook import FigureBook



class GridGroup(Observable, Group):
    class FigureObserver:
        def __init__(self, grid_group):
            self.__grid_group    = grid_group
            
        def update(self, **kwargs):
            if 'major_grid' in kwargs:
                self.__grid_group.major_checkbox = kwargs['major_grid']
            if 'minor_grid'  in kwargs:
                self.__grid_group.minor  = kwargs['minor_grid']  
                
    
    def __init__(self, *args, **kwargs):
        if 'value_checker' in kwargs:
            value_checker    = kwargs.pop('value_checker')
            check_nonnegative_float  = value_checker.check_nonnegative_float
        else:
            check_nonnegative_float  = None
            
        if 'balloon' in kwargs:
            kwargs.pop('balloon')
        
        super().__init__(*args, **kwargs)
        
        self.__gui_images = []
        
        major = IntVar(0)
        minor = IntVar(0)
        self.__major = major
        self.__minor = minor
        self.__figure_observer = self.FigureObserver(self)
                                
        def askgridprop():
            win = Toplevel()
            color = ['#000000', '#000000']

            propvars = [StringVar() for i in range(4)]
            guidata = (
                {
                    'linestyle': ('Major Line Style', propvars[0], None),
                    'linewidth': ('Major Line Width', propvars[1], check_nonnegative_float)
                },
                {
                    'linestyle': ('Minor Line Style', propvars[2], None),
                    'linewidth': ('Minor Line Width', propvars[3], check_nonnegative_float)
                }
            )

            for d in guidata:
                for key in d:
                    pitem = LabeledEntry(win)
                    pitem.pack()
                    pitem.label_text = d[key][0]
                    pitem.entry['textvariable'] = d[key][1]
                    if d[key][2]:
                        pitem.checker_function = d[key][2]

            def setmajorcolor():
                c = askcolor()
                color[0] = c[1]

            def setminorcolor():
                c = askcolor()
                color[1] = c[1]
                
            Button(win, text='Major Line Color', command=setmajorcolor).pack()
            Button(win, text='Minor Line Color', command=setminorcolor).pack()

            win.protocol('WM_DELETE_WINDOW', win.quit)
            win.focus_set()
            win.grab_set()
            win.mainloop()
            win.destroy()
            
            c_major = StringVar(); c_major.set(color[0])
            c_minor = StringVar(); c_minor.set(color[1])
            guidata[0]['color'] = ('Major Line Color', c_major, None)
            guidata[1]['color'] = ('Minor Line Color', c_minor, None)
            return guidata

        def on_property_button_click():
            ret = askgridprop()
            props  = {'major':{}, 'minor':{}}
            for index, name in enumerate(('major', 'minor')):
                for key in ret[index]:
                    value = ret[index][key][1].get()
                    if value:
                        props[name][key] = value
            major.set(1)
            minor.set(1)
            self.notify_observers(major_grid=major.get(), 
                                  minor_grid=minor.get(), props=props)
                                    
        with open(Scripting.root_node.get_gui_image_path("GridTab_Major.psd"), "rb") as image_file:
            icon = ImageTk.PhotoImage(psd.get_pil_image(image_file, read_channels=4)[0])
        self.__gui_images.append(icon)
        major_grid_checkbutton = Checkbutton(self, text='Grid Major', 
                                             image=icon,
                                             compound='left',
                                             variable=major, 
                                             command=self._on_check_click)
        major_grid_checkbutton.pack(fill='x')
        self.major_grid_checkbutton = major_grid_checkbutton
        
        with open(Scripting.root_node.get_gui_image_path("GridTab_Minor.psd"), "rb") as image_file:
            icon = ImageTk.PhotoImage(psd.get_pil_image(image_file, read_channels=4)[0])
        self.__gui_images.append(icon)
        minor_grid_checkbutton = Checkbutton(self, text='Grid Minor', 
                                             image=icon,
                                             compound='left',
                                             variable=minor, 
                                             command=self._on_check_click)
        minor_grid_checkbutton.pack(fill='x')
        self.minor_grid_checkbutton = minor_grid_checkbutton        
        
        property_button = Button(self, text='Property', 
                             command=on_property_button_click)
        property_button.pack()
        self.property_button    = property_button
        
        self.name = 'Grid'
        
    @property
    def figure_observer(self):
        return self.__figure_observer

    def _on_check_click(self):
        self.notify_observers(major_grid=self.__major.get(), 
                              minor_grid=self.__minor.get())
                
        
    class __EnableDelegator:
        def __init__(self, widget_name):
            self.widget_name = widget_name
            
        def __get__(self, obj, type=None):
            def enable(state):                
                en  = 'normal' if state else 'disabled'
                getattr(obj, self.widget_name).config(state=en)
            return enable
        
            
    enableWidgets   = dict(
        enableGridMajor = 'major_grid_checkbutton',
        enableGridMinor = 'minor_grid_checkbutton',
        enableProperty  = 'property_button'
    )
    
    
    for method_name in enableWidgets:
        locals()[method_name] = __EnableDelegator(enableWidgets[method_name])
        
        
    @property
    def major_checkbox(self):
        return self.__major.get()
    

    @major_checkbox.setter
    def major_checkbox(self, value):
        self.__major.set(value)
        

    @property
    def minor(self):
        return self.__minor.get()
    

    @minor.setter
    def minor(self, value):
        self.__minor.set(value)  
        


class AxisGroup(Observable, Group):
    class FigureObserver:
        def __init__(self, axis_group):
            self.__axis_group    = axis_group            
        def update(self, **kwargs):
            for XY in ('X', 'Y'):
                for mm in ('major', 'minor'):
                    prop    = ''.join((mm,XY,'Tick'))
                    if prop in kwargs:
                        val = kwargs[prop]
                        setattr(self.__axis_group, prop, val)
            if 'xlim' in kwargs:
                self.__axis_group.xlim   = kwargs['xlim']
            if 'ylim' in kwargs:
                self.__axis_group.ylim   = kwargs['ylim']
                
    
    def __init__(self, *args, **kwargs):
        if 'value_checker' in kwargs:
            value_checker    = kwargs.pop('value_checker')
            check_float  = value_checker.check_float
        else:
            check_float  = None
            
        if 'balloon' in kwargs:
            balloon_bind_widget = kwargs.pop('balloon').bind_widget
        else:
            balloon_bind_widget = lambda *args, **kwargs: None
       
        super(AxisGroup, self).__init__(*args, **kwargs)
        self.__params = [StringVar() for i in range(8)]
        paramfrm =Frame(self)
        paramfrm.pack()
        names = ['xmin', 'xmax', 'ymin', 'ymax', 'major xtick', 'major ytick', 'minor xtick', 'minor ytick']
        images= ['xmin20x20.png', 'xmax20x20.png', 'ymin20x20.png', 'ymax20x20.png', 'ViewTab_MajorXTick.png', 'ViewTab_MajorYTick.png', 'ViewTab_MinorXTick.png', 'ViewTab_MinorYTick.png']
        for c in range(4):
            for r in range(2):
                temp = LabeledEntry(paramfrm)
                #image   = ImageTk.PhotoImage(file=Scripting.root_node.get_gui_image_path(images[c*2+r]))
                set_attributes(temp,
                    checker_function  = check_float,
                    label_common_icon = images[c*2+r],
                    label_width       = 5 if c*2+r < 4 else 10,
                    entry_width       = 5,
                    entry_variable    = self.__params[c*2+r]
                )
                temp.entry.bind('<Return>', self._on_confirm_button_click)
                temp.grid(row=r, column=c)
                balloon_bind_widget(temp, balloonmsg=names[c*2+r])

        btnfrm = Frame(self)
        btnfrm.pack()
        Button(btnfrm, text='Confirm', command=self._on_confirm_button_click).pack(side='left')
        Button(btnfrm, text='Auto', command=self._on_auto_button_click).pack(side='right')
        self.name = 'Axis'        
        self.__figure_observer   = self.FigureObserver(self)
        

    @property
    def figure_observer(self):
        return self.__figure_observer
    

    @property
    def xlim(self):
        return tuple(map(lambda svar: float(svar.get()), self.__params[0:2]))
    

    @xlim.setter
    def xlim(self, value):
        self.__params[0].set(str(value[0]))
        self.__params[1].set(str(value[1]))
        

    @property
    def ylim(self):
        return tuple(map(lambda svar: float(svar.get()), self.__params[2:4]))
    

    @ylim.setter
    def ylim(self, value):
        self.__params[2].set(str(value[0]))
        self.__params[3].set(str(value[1]))
        
               
    for property_name, property_index   in (('major_x_tick', 4), ('major_y_tick', 5), ('minor_x_tick', 6), ('minor_y_tick', 7)):
        prop  = property(lambda self, index=property_index: float(self.__params[index].get()))
        locals()[property_name]  = prop.setter(lambda self, val, index=property_index: self.__params[index].set(str(val)))


    def _on_confirm_button_click(self, event=None):
        def to_float(x):
            try:
                return float(x)
            except:
                return None
        p = [to_float(v.get()) for v in self.__params]
        self.notify_observers(xlim=p[0:2], ylim=p[2:4], major_x_tick=p[4], major_y_tick=p[5], minor_x_tick=p[6], minor_y_tick=p[7])


    def _on_auto_button_click(self):
        self.notify_observers(xlim=None, ylim=None, major_x_tick=None, major_y_tick=None, minor_x_tick=None, minor_y_tick=None, auto_scale=True)



class ClearGroup(Observable, Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Button(self, text='Clear All', command=self._on_clear_all).pack()
        Button(self, text='Del Sel', command=self._on_delete_selected).pack()
        Button(self, text='Del UnSel', command=self.onDelUnSel).pack()
        self.name = 'Clear Plot'
        

    def _on_clear_all(self):
        self.notify_observers('all')
        

    def _on_delete_selected(self):
        self.notify_observers('sel')
        

    def onDelUnSel(self):           
        raise NotImplementedError



class LabelGroup(Observable, Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Button(self, text='Title', command=self._on_title_click).pack()
        Button(self, text='Label', command=self._on_label_click).pack()
        Button(self, text='Legend', command=self._on_legend_click).pack()
        self.name   = 'Label'
        
        
    def _on_title_click(self):
        title_string = askstring('Title', 
                                 'Enter the title of current figure:')
        self.notify_observers('title', title_string)
        
    
    def _on_label_click(self):
        raise NotImplementedError
        
    
    def _on_legend_click(self):
        raise NotImplementedError
        


class IndicatorGroup(Observable, Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__indicator_combo = indicator_combo = Combobox(self, value=[], 
                                                            takefocus=1, 
                                                            stat='readonly', 
                                                            width=9)
        indicator_combo['value']  = ['axvspan', 'axhspan']
        indicator_combo.current(0)        
        indicator_combo.pack()
        Button(self, text='Add', command=self._on_add).pack()
        self.name = 'Indicators'
        
        
    def _on_add(self):
        indicatorType = self.__indicator_combo.get()
        def askSpan(orient='v'):
            win = Toplevel()
            pxmin = LabeledEntry(win)
            pxmin.pack()
            pxmin.label_text = 'xmin' if orient=='v' else 'ymin'
            pxmax = LabeledEntry(win)
            pxmax.pack()
            pxmax.label_text = 'xmax' if orient=='v' else 'ymax'
            def formatter(val):
                val = float(val)
                val /= 100.
                return '{0:0.2f}'.format(val)
            alphaScale = LabeledScale(win, from_=0, to=100, name='alpha', formatter=formatter)
            alphaScale.set(50.0)
            alphaScale.pack()
            win.protocol('WM_DELETE_WINDOW', win.quit)
            win.focus_set()
            win.grab_set()
            win.mainloop()
            xmin    = pxmin.entry.get()
            xmax    = pxmax.entry.get()
            alpha   = alphaScale.get() / 100.
            win.destroy()
            return map(float, (xmin, xmax, alpha))

        if indicatorType in ('axvspan', 'axhspan'):
            try:
                the_min, the_max, alpha  = askSpan(indicatorType[2])
            except ValueError:
                return
            meta    = {
                'type':     indicatorType,
                'props':    {'alpha':alpha}
            }
            if indicatorType == 'axvspan':
                meta['xmin']    = the_min 
                meta['xmax']    = the_max
                meta['ymin']    = 0.0
                meta['ymax']    = 1.0
            else:
                meta['xmin']    = 0.0
                meta['xmax']    = 1.0
                meta['ymin']    = the_min
                meta['ymax']    = the_max
            self.notify_observers(meta) 
            


class FigureExportGroup(Group): # To Do: Use observer protocol.
    def __init__(self, *args, **kwargs):
        self._app = Scripting.root_node
        self.__topwin = kwargs.pop('topwin')
        super().__init__(*args, **kwargs)
        self.__gui_images = []
        imageFigureExportBtn = ImageTk.PhotoImage(
            file=Scripting.root_node.get_gui_image_path('Pattern_ExportFigure_Button.png')
        )
        self.__gui_images.append(imageFigureExportBtn)
        frm = Frame(self); frm.pack(side='left')
        Button(
            frm, 
            image=imageFigureExportBtn, 
            command=self._on_export_matlab_script).pack(side='top')
        Button(
            frm, 
            text='Script', 
            command=self._on_export_matlab_script, width=6).pack(side='top')
        
        self.name = 'Figure'
        
        
    def _on_export_matlab_script(self):
        filename = asksaveasfilename(filetypes=[('Matlab script files', '*.m')])
        if not filename:
            return
        with code_printer():
            self.__topwin.figure_book.export_matlab_script(filename)
        self._app.gui.console.show_tips(f'''A Matlab script file has been saved as {filename}.
By running this script, Matlab will literally "re-plot" the curves shown here.''') 
            
                
                
class FigureWindow(TkToolWindow):
    _xmlrpcexport_  = ['plot_current_data']  
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)               
        
        figure_book = FigureBook(self.tk_object)
        figure_book.pack(expand='yes', fill='both')
        self.figure_book = figure_book
        
        app = Scripting.root_node
        self.balloon = app.gui.balloon
        self.value_checker = app.gui.value_checker
        
                
    @property
    def current_data(self):
        if self.figure_book.data_pool:
            return self.figure_book.data_pool[-1]
        
            
    @current_data.setter
    def current_data(self, data):
        if data is not None:
            self.figure_book.data_pool.append(data)
            
            
    @property
    def data_pool(self):
        return self.figure_book.data_pool
    
        
    def data_pool_append(self, data):
        self.figure_book.data_pool.append(data)
        
           
    def _make_view_tab(self):
        tool_tabs    = self._tool_tabs
        view_frame = Frame(tool_tabs)
        
        grid_group = GridGroup(view_frame, bd=2, relief='groove', 
                               balloon=self.balloon, 
                               value_checker=self.value_checker)
        grid_group.pack(side='left', fill='y')
        grid_group.add_observer(self.figure_book.grid_group_observer)
        self.figure_book.add_observer(grid_group.figure_observer)
              
        axis_group = AxisGroup(view_frame, bd=2, relief='groove', 
                               balloon=self.balloon, 
                               value_checker=self.value_checker)
        axis_group.pack(side='left', fill='y')
        axis_group.add_observer(self.figure_book.axis_group_observer)
        self.figure_book.add_observer(axis_group.figure_observer)
      
        
        clear_group = ClearGroup(view_frame, bd=2, relief='groove')
        clear_group.pack(side='left', fill='y')
        clear_group.add_observer(self.figure_book.clear_group_observer)
        
        
        with self.attribute_lock:    
            set_attributes(self,
                grid_group = grid_group,
                axis_group = axis_group,
                clear_group = clear_group,
                view_frame = view_frame
            )
            
        tool_tabs.add(view_frame, text='View')
        
        
    def _make_marker_tab(self):
        tool_tabs = self._tool_tabs
        marker_frame = Frame(tool_tabs)
        
        label_group = LabelGroup(marker_frame, bd=2, relief='groove')
        label_group.pack(side='left', fill='y')
        label_group.add_observer(self.figure_book.label_group_observer)        
        
        indicator_group    = IndicatorGroup(marker_frame, bd=2, relief='groove')
        indicator_group.pack(side='left', fill='y')
        indicator_group.add_observer(self.figure_book.indicator_group_observer)
        
        with self.attribute_lock:
            set_attributes(self,
                label_group        = label_group,
                indicator_group    = indicator_group
            )
        
        tool_tabs.add(marker_frame, text='Marker')
            
            
    def _make_export_tab(self):
        tool_tabs = self._tool_tabs
        export_frame = Frame(tool_tabs)
        figure_export_group = FigureExportGroup(export_frame, bd=2, 
                                                relief='groove', topwin=self)
        figure_export_group.pack(side='left', fill='y')
        
        with self.attribute_lock:
            set_attributes(self,
                 figure_export_group = figure_export_group,
                 export_frame = export_frame
            )
            
        tool_tabs.add(export_frame, text='Export')
            

    @WaveSynScriptAPI    
    def draw_current_data(self):        
        self.figure_book.draw(self.current_data)

    
    def draw(self, data):
        self.figure_book.draw(data)                    
 
