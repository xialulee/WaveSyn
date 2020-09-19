import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator

from wavesynlib.languagecenter.wavesynscript import (
    ModelNode, NodeList, 
    WaveSynScriptAPI)
from wavesynlib.languagecenter.utils import set_attributes
from wavesynlib.languagecenter.designpatterns import Observable



class Indicators(ModelNode):
    def __init__(self, node_name='', data_figure=None, callback=None):
        super().__init__(node_name=node_name)
        self.__dataFig  = data_figure
        if data_figure is not None:
            self.__ax   = data_figure.axes
        self.__meta = []
        if callback is None:
            callback    = lambda *args, **kwargs: None
        self.__callback = callback
        
        
    @WaveSynScriptAPI
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
                'object':obj })
        self.__dataFig.update()
        
        
    @WaveSynScriptAPI
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
                'object':obj })
        self.__dataFig.update() 

        
    def clear(self):
        self.__meta = []

        
    @property
    def meta(self):
        return self.__meta



class DataFigure(ModelNode, Observable):
    def __init__(self, master, node_name='', figure_size=(5,4), dpi=100, is_polar=False):
        super().__init__(node_name=node_name)
        
        figure = Figure(figure_size, dpi)
        
        canvas = FigureCanvasTkAgg(figure, master=master)
        canvas.draw()
        
        self.__canvas = canvas
        toolbar = NavigationToolbar2Tk(canvas, master)
        toolbar.update()
        canvas.get_tk_widget().pack(side='top', fill='both', expand='yes')
        toolbar.pack()       
        
        # canvas.mpl_connect('button_press_event', lambda event:print(event)) # test mpl_connect
        
        with self.attribute_lock:
            # All the properties being set in this block will be locked automatically,
            # i.e. these properties cannot be replaced.
            set_attributes(self,
                figure      = figure,
                line_objects = [],       
                axes        = figure.add_subplot(111, polar=is_polar),
                is_polar     = is_polar)

        self.indicators = Indicators(data_figure=self)
        self.plot_function = None
        self.index  = None # Used by FigureList
        
        self.__major_grid    = is_polar
        self.__minor_grid    = False

        self.__indicatorsMeta   = []
        

    @property
    def node_path(self):
        if isinstance(self.parent_node, NodeList):
            return f'{self.parent_node.node_path}[{self.index}]'
        else:
            return super().node_path  
             
        
    def plot(self, *args, **kwargs):
        line_object = self.axes.plot(*args, **kwargs)
        self.line_objects.append(line_object)
        self.update()


    def stem(self, *args, **kwargs):
        kwargs["use_line_collection"] = True
        color = kwargs.pop("color", None)
        line_object = self.axes.stem(*args, **kwargs)
        if color:
            line_object.markerline.set_color(color)
            line_object.stemlines.set_color(color)
        self.line_objects.append(line_object)
        self.update()


    def scatter(self, *args, **kwargs):
        graph_object = self.axes.scatter(*args, **kwargs)
        self.line_objects.append(graph_object)
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
        
    
    @WaveSynScriptAPI        
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
            

    @WaveSynScriptAPI
    def turn_grid(self, b, which='major', axis='both', **kwargs):
        b = {'on':True, 'off':False}.get(b, b)
        self.axes.grid(b, which, axis, **kwargs)
        if which == 'major':
            self.__major_grid    = b
        elif which == 'minor':
            self.__minor_grid    = b            
        self.update()


    @WaveSynScriptAPI    
    def update(self):
        self.__canvas.draw()
        self.notify_observers()
        

    # To do: fix clipboard copy functionality.
    #@WaveSynScriptAPI
    #def copy_bitmap(self, dpi=300):
        #from wavesynlib.interfaces.os.windows.clipboard import clipb # To Do: use interfaces.clipboard instead.
        #from os import path, remove
        #filename    = ''
        #flag        = False
        #for i in range(10000):
            #for j in range(10000):
                #filename    = '{0}-{1}.png'.format(i,j)
                #if not path.exists(filename):
                    #flag    = True
                    #break
            #if flag:
                #break
        #if not filename:
            #raise Exception('Fail to find a valid filename.')
        #try:
            #self.figure.savefig(filename, dpi=dpi)
            #clipb.image2clipb(filename)
        #finally:
            #remove(filename)
            

    @WaveSynScriptAPI
    def set_title(self, title):
        self.axes.set_title(title)
        self.update()
        
                               
    def clear(self):
        self.axes.clear()
        del self.line_objects[:]
        self.update()
        
   
    @WaveSynScriptAPI    
    def axis(self, r):
        retval  = self.axes.axis(r)
        self.update()
        return retval
    
        
    @WaveSynScriptAPI
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