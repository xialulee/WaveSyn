# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:58:34 2014

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

from six.moves.tkinter_colorchooser import askcolor
from six.moves.tkinter import *
from six.moves.tkinter_ttk import *
from six.moves.tkinter import Frame, PanedWindow, Label
from six.moves.tkinter_tkfiledialog import asksaveasfilename
from six.moves.tkinter_tksimpledialog import askstring

from PIL import ImageTk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.ticker import MultipleLocator
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as pyplot

from numpy import deg2rad, rad2deg

from wavesynlib.application import get_gui_image_path
from wavesynlib.toolwindows.basewindow import TkToolWindow
from wavesynlib.languagecenter.wavesynscript import Scripting
from wavesynlib.languagecenter.utils import (
    auto_subs, eval_format, set_attributes)
from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, NodeList, code_printer)
from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.guicomponents.tk import (
    Group, LabeledEntry, ScrolledList, LabeledScale)

color_map = {
    'c': 'cyan',
    'm': 'magenta',
    'y': 'yellow',
    'k': 'black',
    'r': 'red',
    'g': 'forestgreen',
    'b': 'blue'
}

def ask_class_name():
    win = Toplevel()
    
    module_name  = StringVar()
    class_name   = StringVar()
    
    module_item  = LabeledEntry(win)
    module_item.label_text    = 'Module Name'
    module_item.pack()
    module_item.entry_variable     = module_name
    
    class_item   = LabeledEntry(win)
    class_item.label_text     = 'Class Name'
    class_item.pack()
    class_item.entry_variable      = class_name
    
    Button(win, text='OK', command=win.quit).pack()

    win.protocol('WM_DELETE_WINDOW', win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()
    return module_name.get(), class_name.get()


class DataFigure(ModelNode, Observable):
    class Indicators(ModelNode):
        def __init__(self, node_name='', data_figure=None, callback=None):
            super(DataFigure.Indicators, self).__init__(node_name=node_name)
            self.__dataFig  = data_figure
            if data_figure is not None:
                self.__ax   = data_figure.axes
            self.__meta = []
            if callback is None:
                callback    = lambda *args, **kwargs: None
            self.__callback = callback
            
        @Scripting.printable
        def axvspan(self, xmin, xmax, ymin=0, ymax=1, **kwargs):
            obj = self.__ax.axvspan(xmin, xmax, ymin, ymax, **kwargs)
            self.__meta.append(
                {
                    'type':  'axvspan',
                    'xmin':  xmin,
                    'xmax':  xmax,
                    'ymin':  ymin,
                    'ymax':  ymax,
                    'props': kwargs,
                    'object':obj
                }
            )
            self.__dataFig.update()
            
        @Scripting.printable
        def axhspan(self, ymin, ymax, xmin=0, xmax=1, **kwargs):
            obj = self.__ax.axhspan(ymin, ymax, xmin, xmax, **kwargs)
            self.__meta.append(
                {
                    'type':  'axhspan',
                    'xmin':  xmin,
                    'xmax':  xmax,
                    'ymin':  ymin,
                    'ymax':  ymax,
                    'props': kwargs,
                    'object':obj
                }
            )
            self.__dataFig.update() 
            
        def clear(self):
            self.__meta = []
            
        @property
        def meta(self):
            return self.__meta
    
    def __init__(self, master, node_name='', figure_size=(5,4), dpi=100, is_polar=False):
        super(DataFigure, self).__init__(node_name=node_name)
        
        figure = Figure(figure_size, dpi)
        
        canvas = FigureCanvasTkAgg(figure, master=master)
        canvas.show()
        
        self.__canvas = canvas
        toolbar = NavigationToolbar2TkAgg(canvas, master)
        toolbar.update()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=YES)
        toolbar.pack()       
        
        # canvas.mpl_connect('button_press_event', lambda event:print(event)) # test mpl_connect
        
        with self.attribute_lock:
            # All the properties being set in this block will be locked automatically,
            # i.e. these properties cannot be replaced.
            set_attributes(self,
                figure      = figure,
                line_objects = [],       
                axes        = figure.add_subplot(111, polar=is_polar),
                is_polar     = is_polar
            )

        self.indicators = self.Indicators(data_figure=self)
        self.plot_function = None
        self.index  = None # Used by FigureList
        
        self.__major_grid    = is_polar
        self.__minor_grid    = False

        self.__indicatorsMeta   = []

    @property
    def node_path(self):
        if isinstance(self.parent_node, FigureList):
            return eval_format('{self.parent_node.node_path}[{self.index}]')
        else:
            return ModelNode.node_path               
        
    def plot(self, *args, **kwargs):
        line_object = self.axes.plot(*args, **kwargs)
        self.line_objects.append(line_object)
        self.update()
        
    def show_image(self, *args, **kwargs):
        self.axes.imshow(*args, **kwargs)
        self.update()
                               
    @property
    def major_grid(self):
        return self.__major_grid
        
    @major_grid.setter
    def major_grid(self, val):
        self.__major_grid    = val
        self.axes.grid(val, 'major')
        
    @property
    def minor_grid(self):
        return self.__minor_grid
        
    @minor_grid.setter
    def minor_grid(self, val):
        self.__minor_grid    = val
        self.axes.grid(val, 'minor')
        
    @property
    def xlim(self):
        return self.axes.get_xlim()
        
    @property
    def ylim(self):
        return self.axes.get_ylim()
        
    def get_tick(self, name):
        ax          = self.axes
        meth    = self.tick_parameters[name]
        tick    = getattr(getattr(ax, meth[0]), 'get_'+meth[1])()()
        if len(tick) >= 2:
            tick    = tick[1] - tick[0]
            return tick
        else:
            return None
    
    @Scripting.printable        
    def set_tick(self, name, val):
        ax          = self.axes
        meth        = self.tick_parameters[name]
        if val is not None:
            getattr(getattr(ax, meth[0]), 'set_'+meth[1])(MultipleLocator(float(val)))
        self.update()
            
    tick_parameters  = {
        'major_x_tick':   ('xaxis', 'major_locator'), 
        'major_y_tick':   ('yaxis', 'major_locator'), 
        'minor_x_tick':   ('xaxis', 'minor_locator'), 
        'minor_y_tick':   ('yaxis', 'minor_locator')
    }
    for param in tick_parameters:
        prop = property(lambda self, name=param: self.get_tick(name))
        locals()[param] = prop.setter(lambda self, val, name=param: 
                                      self.set_tick(name, val))

    @Scripting.printable
    def turn_grid(self, b, which='major', axis='both', **kwargs):
        b = {'on':True, 'off':False}.get(b, b)
        self.axes.grid(b, which, axis, **kwargs)
        if which == 'major':
            self.__major_grid    = b
        elif which == 'minor':
            self.__minor_grid    = b            
        self.update()

    @Scripting.printable    
    def update(self):
        self.__canvas.show()
        self.notify_observers()

    @Scripting.printable
    def copy_bitmap(self, dpi=300):
        from wavesynlib.interfaces.windows.clipboard import clipb # To Do: use interfaces.clipboard instead.
        from os import path, remove
        filename    = ''
        flag        = False
        for i in range(10000):
            for j in range(10000):
                filename    = '{0}-{1}.png'.format(i,j)
                if not path.exists(filename):
                    flag    = True
                    break
            if flag:
                break
        if not filename:
            raise Exception('Fail to find a valid filename.')
        try:
            self.figure.savefig(filename, dpi=dpi)
            clipb.image2clipb(filename)
        finally:
            remove(filename)

    @Scripting.printable
    def set_title(self, title):
        self.axes.set_title(title)
        self.update()
                               
    def clear(self):
        self.axes.clear()
        del self.line_objects[:]
        self.update()
   
    @Scripting.printable    
    def axis(self, r):
        retval  = self.axes.axis(r)
        self.update()
        return retval
        
    @Scripting.printable
    def auto_scale(self):
        self.axes.autoscale()
        self.update()
            
    def delete_line(self, index):
        line_object = self.line_objects[index]
        line_object.remove()
        del self.line_objects[index]

#    def remove_unsel_lines(self):
#        sel = self.__slist.list.curselection()
#        if len(sel) > 0:
#            sel = int(sel[0])
#            linemeta = self.__meta_of_lines[sel]
#            k = 0
#            for index in range(len(self.__meta_of_lines)):
#                if self.__meta_of_lines[k] != linemeta:
#                    self.__meta_of_lines[k].lineobj.remove()
#                    self.__slist.list.delete(0)
#                    del self.__meta_of_lines[0]
#                    self.update()
#                else:
#                    k += 1

        
class FigureList(NodeList):
    def __init__(self, node_name=''):
        super(FigureList, self).__init__(node_name=node_name)
        
    def append(self, val):        
        if not isinstance(val, DataFigure):
            raise TypeError, eval_format('{self.node_path} only accepts instance of DataFigure or of its subclasses.')
        NodeList.append(self, val)
        

class FigureBook(Observable, FigureList):         
    '''FigureBook is a widget including multiple DataFigure objects and a Tkinter list widget. 
It is used to show the different aspects of a mathematical object.
For example, FigureBook is used to show the envelope, phase, autocorrelation, and FTM of a vector.

FigureBook supports Observable protocal. When some of its properties change, it will notify its observers, 
and its notify_observers method will pass the following paramters to its observers:
----Grid Properties----
major_grid:  Bool, indicates that whether the major grid is on or off.
minor_grid:  Bool, indicates the minor grid.
----Axis Limits----
xlim:       the lower and upper limits of the x axis.
ylim:       the lower and upper limits of the y axis.
----Tick----
major_x_tick: the x axis' tick of the major grid.
major_y_tick: the y axis' ...
minor_x_tick: the x axis' tick of the minor grid.
minor_y_tick: the y axis' ...'''    

    class GridGroupObserver(object):
        '''This class is used by FigureBook. FigureBook is a class supports observable protocal.
Meanwhile, FigureBook can also observe other objects. This class, GridGroupObserver, can be used to observe
an instance of the GridGroup class.     
    '''
        def __init__(self, figure_book):
            self.__figure_book   = figure_book
            
        def update(self, major_grid, minor_grid, props=None):
            if not props:
                props   = {'major':{}, 'minor':{}}
                
            switch_name_map = {True:'on', False:'off'}
            major_grid = switch_name_map[major_grid]
            minor_grid = switch_name_map[minor_grid]
            
            current_figure = self.__figure_book.current_figure
            with code_printer:
                current_figure.turn_grid(major_grid, which='major', 
                                         **props['major'])
                current_figure.turn_grid(minor_grid, which='minor', 
                                         **props['minor'])                   
            
    class AxisGroupObserver(object):
        def __init__(self, figure_book):
            self.__figure_book   = figure_book
            
        def update(self, xlim, ylim, major_x_tick, major_y_tick, minor_x_tick, minor_y_tick, auto_scale=False):
            with code_printer:
                current_figure   = self.__figure_book.current_figure
                if auto_scale:
                    current_figure.auto_scale()
                    return
                lim = list(xlim)
                if current_figure.is_polar:
                    lim = list(deg2rad(lim))
                    major_x_tick  = deg2rad(major_x_tick)
                    if minor_x_tick is not None:
                        minor_x_tick  = deg2rad(minor_x_tick)
                lim.extend(ylim)
                current_figure.axis(lim)
                for XY in ('x_', 'y_'):
                    for mm in ('major_', 'minor_'):
                        current_figure.set_tick(mm+XY+'tick', locals()[mm+XY+'tick'])

    class ClearGroupObserver(object):
        def __init__(self, figure_book):
            self.__figure_book   = figure_book
            
        def update(self, delType):           
            with code_printer:
                if delType == 'all':
                    self.__figure_book.clear()
                elif delType == 'sel':
                    self.__figure_book.delete_selected_lines(index=None)
                else:
                    return

    class LabelGroupObserver(object):
        def __init__(self, figure_book):
            self.__figure_book   = figure_book
            
        def update(self, labelType, labelString):
            nameMap     = {'title':'set_title', 'xlabel':'setXLabel', 'ylabel':'setYLabel'}            
            with code_printer:
                current_figure   = self.__figure_book.current_figure
                getattr(current_figure, nameMap[labelType])(labelString)
                        
    class IndicatorGroupObserver(object):
        def __init__(self, figure_book):
            self.__figure_book   = figure_book
            
        def update(self, meta):            
            if meta['type'] in ('axvspan', 'axhspan'):
                if meta['type'] == 'axvspan':
                    the_min  = meta['xmin']
                    the_max  = meta['xmax']
                else:
                    the_min  = meta['ymin']
                    the_max  = meta['ymax']
                props   = meta['props']

                with code_printer:
                    getattr(self.__figure_book.current_figure.indicators, 
                            meta['type'])(the_min, the_max, **props)
                    self.__figure_book.update_indicator_list()
                
    class DataFigureObserver(object):
        def __init__(self, figure_book):
            self.__figure_book   = figure_book
            
        def update(self, *args, **kwargs):
            self.__figure_book.notify_observers(*args, **kwargs)
        
    def __init__(self, *args, **kwargs):
        '''
node_name:   The name of this node. Usually set by ModelNode.__setattr__ automatically.
figure_meta: Meta information of figure.
The rest parameters are passed to PanedWindow.__init__.
'''
        node_name    = kwargs.pop('node_name', '')
        super(FigureBook, self).__init__(node_name=node_name)

        figure_meta = None if 'figure_meta' not in kwargs \
            else kwargs.pop('figure_meta')
        kwargs['orient'] = HORIZONTAL
        
        paned_window = PanedWindow(*args, **kwargs)

        paned_window.config(sashwidth=4, sashrelief=GROOVE, bg='forestgreen')        
       
#        figureTabsStyle = Style()
#        figureTabsStyle.configure('Figure.TNotebook', tabposition='sw')       
#        figureTabs    = Notebook(paned_window, style='Figure.TNotebook')
        figureTabs  = Notebook(paned_window)
        
        self.figureTabs   = figureTabs
        figureTabs.bind('<<NotebookTabChanged>>', self._on_tab_change)
        self.lock_attribute('figureTabs')
        
        if figure_meta:
            self.make_figures(figure_meta)
            
        self.lock_elements()    
        
        paned_window.add(figureTabs, stretch='always')
        

        listPan     = PanedWindow(paned_window, orient=VERTICAL)
        listPan.config(sashwidth=4, sashrelief=GROOVE, bg='forestgreen')        
        paned_window.add(listPan, stretch='never')

        
        listFrm     = Frame(listPan)
        listPan.add(listFrm, stretch='always')        
        Label(listFrm, text='Curves', bg='#b5d6b0').pack(side=TOP, fill=X)                
        self.__list = ScrolledList(listFrm, relief=GROOVE)
        self.__list.list_config(width=20)
        self.__list.list_click_callback = self._on_list_click
        self.__list.pack(fill=BOTH, expand=YES)  

        listFrm     = Frame(listPan)        
        listPan.add(listFrm, stretch='never')
        Label(listFrm, text='Indicators', bg='#b5d6b0').pack(side=TOP, fill=X)
        self.__indicator_listbox = ScrolledList(listFrm, relief=GROOVE)
        self.__indicator_listbox.list_config(width=20)
        self.__indicator_listbox.pack(fill=BOTH, expand=YES)
                      
        with self.attribute_lock:
            set_attributes(self,
                paned_window = paned_window,
                grid_group_observer = self.GridGroupObserver(self), 
                axis_group_observer = self.AxisGroupObserver(self),
                clear_group_observer = self.ClearGroupObserver(self),
                label_group_observer = self.LabelGroupObserver(self),
                indicator_group_observer = self.IndicatorGroupObserver(self),
                data_figure_observer = self.DataFigureObserver(self),
                data_pool    = []
            )
            
    def append(self, val):
        val.add_observer(self.data_figure_observer)
        return super(FigureBook, self).append(val)
            
    def notify_observers(self, **kwargs):
        current_figure = self.current_figure
        
        attributes = ['major_grid', 'minor_grid', 'xlim', 'ylim', 
                      'major_x_tick', 'major_y_tick', 'minor_x_tick', 
                      'minor_y_tick']
        for attribute in attributes:
            if attribute not in kwargs:
                kwargs[attribute] = getattr(current_figure, attribute)
                
        if current_figure.is_polar:
            kwargs['xlim'] = rad2deg(kwargs['xlim'])
            kwargs['major_x_tick']    = rad2deg(kwargs['major_x_tick'])
            if kwargs['minor_x_tick'] is not None:
                kwargs['minor_x_tick']    = rad2deg(kwargs['minor_x_tick'])
                
        super(FigureBook, self).notify_observers(**kwargs)            
        
    def pack(self, *args, **kwargs):
        self.paned_window.pack(*args, **kwargs)        
        
    def make_figures(self, figure_meta):
        for meta in figure_meta:
            frm = Frame(self.figureTabs)
            fig = DataFigure(frm, is_polar=meta['polar'])
            self.figureTabs.add(frm, text=meta['name'])
            self.append(fig)        
        
    @property        
    def current_figure(self):
        return self[self.figureTabs.index(CURRENT)]
        
    @property
    def current_figure_index(self):
        return self.figureTabs.index(CURRENT)
                
    def plot(self, *args, **kwargs):
        try:
            curve_name = kwargs.pop('curve_name')
        except KeyError:
            curve_name = 'curve'
            
        for figure in self:
            figure.plot_function(*args, **kwargs)
        self.__list.insert(END, curve_name)
        
        if 'color' in kwargs:
            color = color_map[kwargs['color']]
        else:
            color = color_map[self[0].line_objects[-1][0].get_color()]
            
        self.__list.item_config(END, fg=color)
        self.notify_observers()
    
    @Scripting.printable
    def clear(self):
        for fig in self:
            fig.clear()
        self.__list.clear()
        del self.data_pool[:]
        self.current_figure.indicators.clear()
        self.update_indicator_list()

    def _on_tab_change(self, event): 
        self.notify_observers()
        self.update_indicator_list()          
        
    def _on_list_click(self, index, label):
        index = int(index)
        for figure in self:
            for line in figure.line_objects:
                pyplot.setp(line, linewidth=1)
            pyplot.setp(figure.line_objects[index], linewidth=2)
            figure.update()
            
    @Scripting.printable            
    def export_matlab_script(self, filename):
        with open(filename, 'w') as file:
            for figure in self:
                print('%Generated by WaveSyn.',
                      'figure;', sep = '\n',
                      file=file)
                for line in figure.line_objects:
                    params = {}
                    for name in ('xdata', 'ydata', 'color'):
                        params[name] = pyplot.getp(line[0], name)
                    params['func'] = 'polar' if figure.is_polar else 'plot'
                    params['xdata'] = ','.join((str(i) for i in params['xdata']))
                    params['ydata'] = ','.join((str(i) for i in params['ydata']))
                    print("{func}([{xdata}], [{ydata}], '{color}');hold on".format(**params), file=file)
                    # To do: Grid
                                        
    @Scripting.printable                    
    def delete_selected_lines(self, index=None):
        if index is None:
            index = self.__list.current_selection # index is a tuple of strings.
            if len(index) <= 0:
                return
            if len(index) > 1:
                raise ValueError, 'Multi-selection is not supported.'
            index = int(index[0])
        for figure in self:
            figure.line_objects[index][0].remove()
            del figure.line_objects[index]
            figure.update()
        self.__list.delete(index)
        del self.data_pool[index]
        
    def update_indicator_list(self):
        listbox = self.__indicator_listbox
        listbox.delete(0, END)
        
        meta = self.current_figure.indicators.meta
        for m in meta:
            if m['type'] == 'axvspan':
                xmin    = m['xmin']
                xmax    = m['xmax']
                listbox.insert(END, '{0}|{1}/{2}'.format('axvspan',xmin,xmax))
            elif m['type'] == 'axhspan':
                ymin    = m['ymin']
                ymax    = m['ymax']
                listbox.insert(END, '{0}|{1}/{2}'.format('axhspan',ymin,ymax))
        

class GridGroup(Observable, Group):
    class FigureObserver(object):
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
            check_positive_float  = value_checker.check_positive_float
        else:
            check_positive_float  = None
            
        if 'balloon' in kwargs:
            kwargs.pop('balloon')
        
        super(GridGroup, self).__init__(*args, **kwargs)
        
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
                    'linewidth': ('Major Line Width', propvars[1], check_positive_float)
                },
                {
                    'linestyle': ('Minor Line Style', propvars[2], None),
                    'linewidth': ('Minor Line Width', propvars[3], check_positive_float)
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
                                    
        major_grid_checkbutton = Checkbutton(self, text='Grid Major', 
                                             variable=major, 
                                             command=self._on_check_click)
        major_grid_checkbutton.pack(fill=X)
        self.major_grid_checkbutton = major_grid_checkbutton
        
        minor_grid_checkbutton = Checkbutton(self, text='Grid Minor', 
                                             variable=minor, 
                                             command=self._on_check_click)
        minor_grid_checkbutton.pack(fill=X)
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
                
    class __EnableDelegator(object):
        def __init__(self, widget_name):
            self.widget_name = widget_name
            
        def __get__(self, obj, type=None):
            def enable(state):                
                en  = NORMAL if state else DISABLED
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
    class FigureObserver(object):
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
        images= ['ViewTab_XMin.png', 'ViewTab_XMax.png', 'ViewTab_YMin.png', 'ViewTab_YMax.png', 'ViewTab_MajorXTick.png', 'ViewTab_MajorYTick.png', 'ViewTab_MinorXTick.png', 'ViewTab_MinorYTick.png']
        for c in range(4):
            for r in range(2):
                temp = LabeledEntry(paramfrm)
                image   = ImageTk.PhotoImage(file=get_gui_image_path(images[c*2+r]))
                set_attributes(temp,
                    checker_function   = check_float,
                    #label_text   = names[c*2+r],
                    label_image  = image,
                    label_width  = 5 if c*2+r < 4 else 10,
                    entry_width  = 5,
                    entry_variable    = self.__params[c*2+r]
                )
                temp.entry.bind('<Return>', self._on_confirm_button_click)
                temp.grid(row=r, column=c)
                balloon_bind_widget(temp, balloonmsg=names[c*2+r])

        btnfrm = Frame(self)
        btnfrm.pack()
        Button(btnfrm, text='Confirm', command=self._on_confirm_button_click).pack(side=LEFT)
        Button(btnfrm, text='Auto', command=self._on_auto_button_click).pack(side=RIGHT)
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
        super(ClearGroup, self).__init__(*args, **kwargs)
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
        super(LabelGroup, self).__init__(*args, **kwargs)
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
        super(IndicatorGroup, self).__init__(*args, **kwargs)
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
        super(FigureExportGroup, self).__init__(*args, **kwargs)
        self.__gui_images = []
        imageFigureExportBtn = ImageTk.PhotoImage(
            file=get_gui_image_path('Pattern_ExportFigure_Button.png')
        )
        self.__gui_images.append(imageFigureExportBtn)
        frm = Frame(self); frm.pack(side=LEFT)
        Button(frm, image=imageFigureExportBtn, command=self._on_export_matlab_script).pack(side=TOP)
        Button(frm, text='Script', command=self._on_export_matlab_script, width=6).pack(side=TOP)
        
        self.name = 'Figure'
        
    def _on_export_matlab_script(self):
        filename = asksaveasfilename(filetypes=[('Matlab script files', '*.m')])
        if not filename:
            return
        with code_printer:
            self.__topwin.figure_book.export_matlab_script(filename)
        self._app.print_tip(
            auto_subs(
                '''A Matlab script file has been saved as $filename.
By running this script, Matlab will literally "re-plot" the curves shown here.'''
            )
        ) 
                
                
class FigureWindow(TkToolWindow):
    _xmlrpcexport_  = ['plot_current_data']    
    
    def __init__(self, *args, **kwargs):
        super(FigureWindow, self).__init__(*args, **kwargs)               
        
        figure_book = FigureBook(self.tk_object)
        figure_book.pack(expand=YES, fill=BOTH)                
        self.figure_book = figure_book
        
        app = Scripting.root_node
        self.balloon = app.balloon
        self.value_checker = app.value_checker
                
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
        
        grid_group = GridGroup(view_frame, bd=2, relief=GROOVE, 
                               balloon=self.balloon, 
                               value_checker=self.value_checker)
        grid_group.pack(side=LEFT, fill=Y)
        grid_group.add_observer(self.figure_book.grid_group_observer)
        self.figure_book.add_observer(grid_group.figure_observer)
              
        axis_group = AxisGroup(view_frame, bd=2, relief=GROOVE, 
                               balloon=self.balloon, 
                               value_checker=self.value_checker)
        axis_group.pack(side=LEFT, fill=Y)
        axis_group.add_observer(self.figure_book.axis_group_observer)
        self.figure_book.add_observer(axis_group.figure_observer)
      
        
        clear_group = ClearGroup(view_frame, bd=2, relief=GROOVE)
        clear_group.pack(side=LEFT, fill=Y)
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
        tool_tabs    = self._tool_tabs
        marker_frame   = Frame(tool_tabs)
        
        label_group        = LabelGroup(marker_frame, bd=2, relief=GROOVE)
        label_group.pack(side=LEFT, fill=Y)
        label_group.add_observer(self.figure_book.label_group_observer)        
        
        indicator_group    = IndicatorGroup(marker_frame, bd=2, relief=GROOVE)
        indicator_group.pack(side=LEFT, fill=Y)
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
                                                relief=GROOVE, topwin=self)
        figure_export_group.pack(side=LEFT, fill=Y)
        
        with self.attribute_lock:
            set_attributes(self,
                 figure_export_group = figure_export_group,
                 export_frame = export_frame
            )
            
        tool_tabs.add(export_frame, text='Export')
            

    @Scripting.printable    
    def plot_current_data(self):        
        self.plot(self.current_data)

    
    def plot(self, data):
        self.figure_book.plot(data)                    
 