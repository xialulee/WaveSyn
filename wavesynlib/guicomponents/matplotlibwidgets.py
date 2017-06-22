# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 22:10:03 2014

@author: Feng-cong Li
"""
from tkinter import Tk, Frame
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

from matplotlib.widgets import  RectangleSelector
from matplotlib.patches import Circle
from pylab import rand, nonzero



class RectSelector:
    def __init__(self, ax, canvas):
        self.rectProps  = dict(facecolor='red', edgecolor = 'white',
                 alpha=0.5, fill=True)
        self.indicatorProps = dict(facecolor='white', edgecolor='black', alpha=0.5, fill=True)
        self.__selector = RectangleSelector(ax, self._on_select, drawtype='box', rectprops=self.rectProps)
        self.__axes     = ax
        self.__canvas   = canvas
        self.mode = None 
        # mode:
        #   None or 'rect': get the selected rect region
        #   'peak': get the peak point in the selected rect region
        self.__rect = None
        self.__peakpos = None
        self.__callback = None
        
        
    @property
    def callback(self):
        return self.__callback
    
    
    @callback.setter
    def callback(self, val):
        if not callable(val):
            raise ValueError
        self.__callback = val
        
        
    @property
    def rect(self):
        return self.__rect
    
    
    @property
    def peakpos(self):
        return self.__peakpos
        
        
    def _on_select(self, epress, erelease):
        start   = (int(epress.xdata), int(epress.ydata))
        stop    = (int(erelease.xdata), int(erelease.ydata))
        self.__rect = start + (stop[0]-start[0], stop[1]-start[1])

        if self.mode == 'peak':
            ax      = self.__axes
            data_matrix  = ax.axes.get_images()[0].get_array()
            clip_matrix  = data_matrix[start[1]:(stop[1]+1), start[0]:(stop[0]+1)]
            peak_pos     = nonzero(clip_matrix == clip_matrix.max())
            peak_pos     = (peak_pos[1][0] + start[0], peak_pos[0][0] + start[1])
            self.__peakpos = peak_pos
            circle      = Circle(peak_pos, 4, **self.indicatorProps)
            ax.add_patch(circle)
            self.__canvas.show()
            
        self.callback(self.__rect, self.__peakpos)
        
        
    def activate(self):
        self.__selector.set_active(True)
        
    def deactivate(self):
        self.__selector.set_active(False)
        
    @property
    def is_active(self):
        return self.__selector.active        



class ImageFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        figure = Figure((5,4), dpi=100)
        self.figure = figure
        canvas = FigureCanvasTkAgg(figure, master=master)
        canvas.mpl_connect('button_press_event', self._on_click)
        canvas.mpl_connect('key_press_event',self._on_keypress)
        canvas.show()
        self.__canvas  = canvas
        toolbar    = NavigationToolbar2TkAgg(canvas, master)
        toolbar.update()
        canvas.get_tk_widget().pack(side='top', fill='both', expand='yes')
        toolbar.pack()
        self.axes   = figure.add_subplot(111)
        self.__rectselector = RectSelector(self.axes, canvas)
        
        
    @property
    def rectselector(self):
        return self.__rectselector
    
        
    def _on_click(self, event):
        print('Clicked')
    
    
    def _on_keypress(self, event):
        print('Key press')
        print(self.rectselector.rect)
        


if __name__ == '__main__':
    root    = Tk()
    imgFrm  = ImageFrame(root)
    imgFrm.pack(side='top', fill='both', expand='yes')
    img = rand(100, 100)
    img[50:51, 50:51]   = 30  
    img[30:32, 70:71]   = 50
    imgFrm.axes.imshow(img)
    imgFrm.rectselector.mode = 'peak'
    imgFrm.rectselector.activate()
    root.mainloop()