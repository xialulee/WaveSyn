from tkinter import PanedWindow, Frame, Label
from tkinter.ttk import Notebook

from numpy import ndarray

import matplotlib
import matplotlib.pyplot as pyplot
from numpy import deg2rad, rad2deg

from wavesynlib.languagecenter.wavesynscript import (
    NodeList,
    WaveSynScriptAPI,
    code_printer)
from wavesynlib.languagecenter.designpatterns import Observable
from wavesynlib.languagecenter.utils import set_attributes

from wavesynlib.widgets.tk.scrolledlist import ScrolledList

from .datafigure import DataFigure
from .colormap import colormap



class FigureList(NodeList):
    def __init__(self, node_name=''):
        super().__init__(node_name=node_name)
        
    def append(self, val):        
        if not isinstance(val, DataFigure):
            raise TypeError(f'{self.node_path} only accepts instance of DataFigure or of its subclasses.')
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
minor_y_tick: the y axis' ...
----Curve List----
curve_selected: will appear in kwargs when an item in the curve list being clicked.
'''    


    class GridGroupObserver:
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
            with code_printer():
                current_figure.turn_grid(major_grid, which='major', 
                                         **props['major'])
                current_figure.turn_grid(minor_grid, which='minor', 
                                         **props['minor']) 

                  
            
    class AxisGroupObserver:
        def __init__(self, figure_book):
            self.__figure_book = figure_book
            
            
        def update(self, xlim, ylim, major_x_tick, major_y_tick, minor_x_tick, minor_y_tick, auto_scale=False):
            with code_printer():
                current_figure = self.__figure_book.current_figure
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
                        
                        

    class ClearGroupObserver:
        def __init__(self, figure_book):
            self.__figure_book   = figure_book
            
        def update(self, delType):           
            with code_printer():
                if delType == 'all':
                    self.__figure_book.clear()
                elif delType == 'sel':
                    self.__figure_book.delete_selected_lines(index=None)
                else:
                    return
                
                

    class LabelGroupObserver:
        def __init__(self, figure_book):
            self.__figure_book   = figure_book
            
        def update(self, labelType, labelString):
            nameMap     = {'title':'set_title', 'xlabel':'setXLabel', 'ylabel':'setYLabel'}            
            with code_printer():
                current_figure   = self.__figure_book.current_figure
                getattr(current_figure, nameMap[labelType])(labelString)
                
                
                        
    class IndicatorGroupObserver:
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

                with code_printer():
                    getattr(self.__figure_book.current_figure.indicators, 
                            meta['type'])(the_min, the_max, **props)
                    self.__figure_book.update_indicator_list()
                    
                    
                
    class DataFigureObserver:
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
        super().__init__(node_name=node_name)

        self.__selected_curve = (None, None)

        figure_meta = None if 'figure_meta' not in kwargs \
            else kwargs.pop('figure_meta')
        kwargs['orient'] = 'horizontal'
        
        paned_window = PanedWindow(*args, **kwargs)

        paned_window.config(sashwidth=4, sashrelief='groove', bg='forestgreen')        
       
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
        

        listPan     = PanedWindow(paned_window, orient='vertical')
        listPan.config(sashwidth=4, sashrelief='groove', bg='forestgreen')        
        paned_window.add(listPan, stretch='never')

        
        listFrm     = Frame(listPan)
        listPan.add(listFrm, stretch='always')        
        Label(listFrm, text='Curves', bg='#b5d6b0').pack(side='top', fill='x')
        self.__list = ScrolledList(listFrm, relief='groove')
        self.__list.list_config(width=20)
        self.__list.list_click_callback = self._on_list_click
        self.__list.pack(fill='both', expand='yes')

        listFrm     = Frame(listPan)        
        listPan.add(listFrm, stretch='never')
        Label(listFrm, text='Indicators', bg='#b5d6b0').pack(side='top', fill='x')
        self.__indicator_listbox = ScrolledList(listFrm, relief='groove')
        self.__indicator_listbox.list_config(width=20)
        self.__indicator_listbox.pack(fill='both', expand='yes')
                      
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


    @property
    def selected_curve(self):
        return self.__selected_curve
            
            
    def append(self, val):
        val.add_observer(self.data_figure_observer)
        return super().append(val)
    
            
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
                
        super().notify_observers(**kwargs)       
        
        
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
        return self[self.figureTabs.index('current')]
    
        
    @property
    def current_figure_index(self):
        return self.figureTabs.index('current')
    
                
    def draw(self, *args, **kwargs):
        try:
            curve_name = kwargs.pop('curve_name')
        except KeyError:
            curve_name = 'curve'
            
        for figure in self:
            figure.plot_function(*args, **kwargs)
        self.__list.insert('end', curve_name)
        
        color = None
        if 'color' in kwargs:
            color = colormap.get(kwargs['color'], None)
        if not color:
            line_object = self[0].line_objects[-1]
            if isinstance(line_object, matplotlib.container.StemContainer):
                color = line_object.stemlines.get_color()[0]
            elif isinstance(line_object, matplotlib.collections.PathCollection):
                color = "#000000"
            else:
                color = line_object[0].get_color()
            if isinstance(color, ndarray):
                color = [int(c*255) for c in color]
                color = "#{:02x}{:02x}{:02x}".format(*color)
            else:
                color = colormap.get(color, color)
            
        self.__list.item_config('end', fg=color)
        self.notify_observers()
    
    
    @WaveSynScriptAPI
    def clear(self):
        for fig in self:
            fig.clear()
        self.__list.clear()
        del self.data_pool[:]
        self.current_figure.indicators.clear()
        self.update_indicator_list()
        self.notify_observers(major_grid=False, minor_grid=False)
        

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
        self.__selected_curve = (index, label)
        self.notify_observers(curve_selected=True)
            
            
    @WaveSynScriptAPI            
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
                    
                                        
    @WaveSynScriptAPI                    
    def delete_selected_lines(self, index=None):
        if index is None:
            index = self.__list.current_selection # index is a tuple of strings.
            if len(index) <= 0:
                return
            if len(index) > 1:
                raise ValueError('Multi-selection is not supported.')
            index = int(index[0])
        for figure in self:
            figure.line_objects[index][0].remove()
            del figure.line_objects[index]
            figure.update()
        self.__list.delete(index)
        del self.data_pool[index]
        
        
    def update_indicator_list(self):
        listbox = self.__indicator_listbox
        listbox.delete(0, 'end')
        
        meta = self.current_figure.indicators.meta
        for m in meta:
            if m['type'] == 'axvspan':
                xmin    = m['xmin']
                xmax    = m['xmax']
                listbox.insert('end', '{0}|{1}/{2}'.format('axvspan',xmin,xmax))
            elif m['type'] == 'axhspan':
                ymin    = m['ymin']
                ymax    = m['ymax']
                listbox.insert('end', '{0}|{1}/{2}'.format('axhspan',ymin,ymax))
