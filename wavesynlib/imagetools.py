# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 22:10:03 2014

@author: Feng-cong Li
"""

from matplotlib.widgets import  RectangleSelector
from matplotlib.patches import Circle
from pylab import *

class PeakFinder(object):
    def __init__(self, ax, canvas):
        self.rectProps  = dict(facecolor='red', edgecolor = 'white',
                 alpha=0.5, fill=True)
        self.indicatorProps = dict(facecolor='white', edgecolor='black', alpha=0.5, fill=True)
        self.__selector = RectangleSelector(ax, self.onSelect, drawtype='box', rectprops=self.rectProps)
        self.__axes     = ax
        self.__canvas   = canvas
        
    def onSelect(self, epress, erelease):
        start   = map(int, (epress.xdata, epress.ydata))
        stop    = map(int, (erelease.xdata, erelease.ydata))
        ###################
        ax      = self.__axes
        dataMatrix  = ax.get_axes().get_images()[0].get_array()
        clipMatrix  = dataMatrix[start[1]:(stop[1]+1), start[0]:(stop[0]+1)]
        peakPos     = nonzero(clipMatrix == clipMatrix.max())
        peakPos     = (peakPos[1][0] + start[0], peakPos[0][0] + start[1])
        print peakPos
        circle      = Circle(peakPos, 4, **self.indicatorProps)
        ax.add_patch(circle)
        self.__canvas.show()
        ###################
    
    def activate(self):
        self.__selector.set_active(True)
        
    def deactivate(self):
        self.__selector.set_active(False)
        
    @property
    def isActivate(self):
        return self.__selector.active


from Tkinter    import *
from ttk        import *
from Tkinter    import Frame, PanedWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

class ImageFrame(Frame, object):
    def __init__(self, master):
        super(ImageFrame, self).__init__(master)
        figure = Figure(figsize=(5,4), dpi=100)
        self.figure = figure
        canvas = FigureCanvasTkAgg(figure, master=master)
        canvas.show()
        self.__canvas  = canvas
        toolbar    = NavigationToolbar2TkAgg(canvas, master)
        toolbar.update()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=YES)
        toolbar.pack()
        self.axes   = figure.add_subplot(111)
        self.peakFinder = PeakFinder(self.axes, canvas)
        

 


if __name__ == '__main__':
    root    = Tk()
    imgFrm  = ImageFrame(root)
    imgFrm.pack(side=TOP, fill=BOTH, expand=YES)
    img = rand(100, 100)
    img[50:51, 50:51]   = 30  
    img[30:32, 70:71]   = 50
    imgFrm.axes.imshow(img)
    imgFrm.peakFinder.activate()
    root.mainloop()