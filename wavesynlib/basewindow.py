# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:58:34 2014

@author: Feng-cong Li
"""
from __future__ import print_function, division

from tkColorChooser import askcolor

from Tkinter import *
from ttk import *
from Tkinter import Frame, PanedWindow, Label
from tkFileDialog import asksaveasfilename
from PIL import ImageTk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.ticker import MultipleLocator
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as pyplot

from numpy          import deg2rad, rad2deg


from wavesynlib.application    import Application, Scripting, uiImagePath
from wavesynlib.objectmodel    import ModelNode, NodeList, NodeDict
from wavesynlib.common         import autoSubs, evalFmt, setMultiAttr
from wavesynlib.common         import MethodDelegator, Observable

from wavesynlib.guicomponents import Group, ParamItem, ScrolledList, LabeledScale


colorMap = {
    'c': 'cyan',
    'm': 'magenta',
    'y': 'yellow',
    'k': 'black',
    'r': 'red',
    'g': 'forestgreen',
    'b': 'blue'
}


def askClassName():
    win = Toplevel()
    
    moduleName  = StringVar()
    className   = StringVar()
    
    moduleItem  = ParamItem(win)
    moduleItem.labelText    = 'Module Name'
    moduleItem.pack()
    moduleItem.entryVar     = moduleName
    
    classItem   = ParamItem(win)
    classItem.labelText     = 'Class Name'
    classItem.pack()
    classItem.entryVar      = className
    
    Button(win, text='OK', command=win.quit).pack()

    win.protocol('WM_DELETE_WINDOW', win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()
    return moduleName.get(), className.get()



class WindowNode(ModelNode):
    windowName = ''

    _xmlrpcexport_  = ['close']    
    
    def __init__(self, *args, **kwargs):
        super(WindowNode, self).__init__(*args, **kwargs)
        self._toplevel = Toplevel()
        self._toplevel.title(evalFmt('{self.windowName} id={id(self)}'))        
        self._toplevel.protocol('WM_DELETE_WINDOW', self.onClose)
                
    methodNameMap   = {
        'update':'update', 
        'windowAttributes':'wm_attributes'
    }
    
    for methodName in methodNameMap:
        locals()[methodName]    = MethodDelegator('_toplevel', methodNameMap[methodName])        
        
        
    @Scripting.printable
    def close(self):
        Application.instance.notifyWinQuit(self)
        self._toplevel.destroy() # For Toplevel objects, use destroy rather than quit.
        
    def onClose(self):
        printCode   = True
        self.close()
        
    @property
    def nodePath(self):
        if isinstance(self.parentNode, WindowDict):
            return evalFmt('{self.parentNode.nodePath}[{id(self)}]')
        else:
            return ModelNode.nodePath
            



class WindowDict(NodeDict):
    def __init__(self, nodeName=''):
        super(WindowDict, self).__init__(nodeName=nodeName)
                
    def __setitem__(self, key, val):
        if not isinstance(val, WindowNode):
            raise TypeError, evalFmt('{self.nodePath} only accepts instance of WindowNode or of its subclasses.')
        if key != id(val):
            raise ValueError, 'The key should be identical to the ID of the window.'
        NodeDict.__setitem__(self, key, val)
        
    def add(self, node):
        self[id(node)] = node
        return id(node)
        
        
        
class WindowComponent(object):
    @property        
    def topWindow(self):
        if hasattr(self, '_topWindow'):
            return self._topWindow
        else:
            node    = self
            while True:
                node    = node.parentNode
                if isinstance(node, WindowNode):
                    self._topWindow    = node
                    return node      
        

  
class DataFigure(ModelNode):
    class Indicators(ModelNode):
        def __init__(self, nodeName='', dataFig=None, callback=None):
            super(DataFigure.Indicators, self).__init__(nodeName=nodeName)
            self.__dataFig  = dataFig
            if dataFig is not None:
                self.__ax   = dataFig.axes
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
    
    def __init__(self, master, nodeName='', figsize=(5,4), dpi=100, isPolar=False):
        super(DataFigure, self).__init__(nodeName=nodeName)
        
        figure = Figure(figsize, dpi)
        
        canvas = FigureCanvasTkAgg(figure, master=master)
        canvas.show()
        
        self.__canvas = canvas
        toolbar = NavigationToolbar2TkAgg(canvas, master)
        toolbar.update()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=YES)
        toolbar.pack()        
        
        with self.attributeLock:
            # All the properties being set in this block will be locked automatically,
            # i.e. these properties cannot be replaced.
            setMultiAttr(self,
                figure      = figure,
                lineObjects = [],       
                axes        = figure.add_subplot(111, polar=isPolar),
                isPolar     = isPolar
            )
        self.indicators = self.Indicators(dataFig=self)

        
        self.plotFunction = None
        
        self.index  = None # Used by FigureList
        
        self.__majorGrid    = isPolar
        self.__minorGrid    = False
        
        self.__indicatorsMeta   = []

    @property
    def nodePath(self):
        if isinstance(self.parentNode, FigureList):
            return evalFmt('{self.parentNode.nodePath}[{self.index}]')
        else:
            return ModelNode.nodePath               
        
    def plot(self, *args, **kwargs):
        lineObject = self.axes.plot(*args, **kwargs)
        self.lineObjects.append(lineObject)
        self.update()
                               
    @property
    def majorGrid(self):
        return self.__majorGrid
        
    @majorGrid.setter
    def majorGrid(self, val):
        self.__majorGrid    = val
        self.axes.grid(val, 'major')
        
    @property
    def minorGrid(self):
        return self.__minorGrid
        
    @minorGrid.setter
    def minorGrid(self, val):
        self.__minorGrid    = val
        self.axes.grid(val, 'minor')
        
    @property
    def xLim(self):
        return self.axes.get_xlim()
        
    @property
    def yLim(self):
        return self.axes.get_ylim()
        
    def getTick(self, name):
        ax          = self.axes
        meth    = self.tickParams[name]
        tick    = getattr(getattr(ax, meth[0]), 'get_'+meth[1])()()
        if len(tick) >= 2:
            tick    = tick[1] - tick[0]
            return tick
        else:
            return None
    
    @Scripting.printable        
    def setTick(self, name, val):
        ax          = self.axes
        meth        = self.tickParams[name]
        if val is not None:
            getattr(getattr(ax, meth[0]), 'set_'+meth[1])(MultipleLocator(float(val)))
        self.update()
            
    tickParams  = {
        'majorXTick':   ('xaxis', 'major_locator'), 
        'majorYTick':   ('yaxis', 'major_locator'), 
        'minorXTick':   ('xaxis', 'minor_locator'), 
        'minorYTick':   ('yaxis', 'minor_locator')
    }
    for param in tickParams:
        prop   = property(lambda self, name=param: self.getTick(name))
        locals()[param]   = prop.setter(lambda self, val, name=param: self.setTick(name, val))

        

    @Scripting.printable
    def grid(self, b, which='major', axis='both', **kwargs):
        if b=='on': 
            b   = True
        elif b=='off':
            b   = False        
        self.axes.grid(b, which, axis, **kwargs)
        if which == 'major':
            self.__majorGrid    = b
        elif which == 'minor':
            self.__minorGrid    = b            
        self.update()


    @Scripting.printable    
    def update(self):
        self.__canvas.show()


    @Scripting.printable
    def copyBitmap(self, dpi=300):
        from wavesynlib.interfaces.windows import clipb
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

                               
    def clear(self):
        self.axes.clear()
        del self.lineObjects[:]
        self.update()

    
    @Scripting.printable    
    def axis(self, r):
        return self.axes.axis(r)
        
    @Scripting.printable
    def autoScale(self):
        self.axes.autoscale()
        self.update()
            
    def deleteLine(self, idx):
        lineObject = self.lineObjects[idx]
        lineObject.remove()
        del self.lineObjects[idx]

#    def remove_unsel_lines(self):
#        sel = self.__slist.list.curselection()
#        if len(sel) > 0:
#            sel = int(sel[0])
#            linemeta = self.__meta_of_lines[sel]
#            k = 0
#            for idx in range(len(self.__meta_of_lines)):
#                if self.__meta_of_lines[k] != linemeta:
#                    self.__meta_of_lines[k].lineobj.remove()
#                    self.__slist.list.delete(0)
#                    del self.__meta_of_lines[0]
#                    self.update()
#                else:
#                    k += 1

        
class FigureList(NodeList):
    def __init__(self, nodeName=''):
        super(FigureList, self).__init__(nodeName=nodeName)
        
    def append(self, val):        
        if not isinstance(val, DataFigure):
            raise TypeError, evalFmt('{self.nodePath} only accepts instance of DataFigure or of its subclasses.')
        NodeList.append(self, val)
        

class FigureBook(Observable, FigureList):         
    '''FigureBook is a widget including multiple DataFigure objects and a Tkinter list widget. 
It is used to show the different aspects of a mathematical object.
For example, FigureBook is used to show the envelope, phase, autocorrelation, and FTM of a vector.

FigureBook supports Observable protocal. When some of its properties change, it will notify its observers, 
and its notifyObservers method will pass the following paramters to its observers:
----Grid Properties----
majorGrid:  Bool, indicates that whether the major grid is on or off.
minorGrid:  Bool, indicates the minor grid.
----Axis Limits----
xLim:       the lower and upper limits of the x axis.
yLim:       the lower and upper limits of the y axis.
----Tick----
majorXTick: the x axis' tick of the major grid.
majorYTick: the y axis' ...
minorXTick: the x axis' tick of the minor grid.
minorYTick: the y axis' ...'''    

    class GridGroupObserver(object):
        '''This class is used by FigureBook. FigureBook is a class supports observable protocal.
Meanwhile, FigureBook can also observe other objects. This class, GridGroupObserver, can be used to observe
an instance of the GridGroup class.     
    '''
        def __init__(self, figureBook):
            self.__figureBook   = figureBook
            
        def update(self, majorGrid, minorGrid, props=None):
            printCode   = True
            if not props:
                props   = {'major':{}, 'minor':{}}
            currentFigure   = self.__figureBook.currentFigure

            currentFigure.grid(majorGrid, which='major', **props['major'])
            currentFigure.grid(minorGrid, which='minor', **props['minor'])                   
            
    class AxisGroupObserver(object):
        def __init__(self, figureBook):
            self.__figureBook   = figureBook
            
        def update(self, xLim, yLim, majorXTick, majorYTick, minorXTick, minorYTick, autoScale=False):
            printCode   = True
            currentFigure   = self.__figureBook.currentFigure
            if autoScale:
                currentFigure.autoScale()
                return
            lim = list(xLim)
            if currentFigure.isPolar:
                lim = list(deg2rad(lim))
                majorXTick  = deg2rad(majorXTick)
                if minorXTick is not None:
                    minorXTick  = deg2rad(minorXTick)
            lim.extend(yLim)
            currentFigure.axis(lim)
            for XY in ('X', 'Y'):
                for mm in ('major', 'minor'):
                    currentFigure.setTick(mm+XY+'Tick', locals()[mm+XY+'Tick'])

    class ClearGroupObserver(object):
        def __init__(self, figureBook):
            self.__figureBook   = figureBook
            
        def update(self, delType):
            printCode   = True            
            if delType == 'all':

                self.__figureBook.clear()
            elif delType == 'sel':
                self.__figureBook.deleteSelLines(idx=None)
            else:
                return
                
    class IndicatorGroupObserver(object):
        def __init__(self, figureBook):
            self.__figureBook   = figureBook
            
        def update(self, meta):
            printCode   = True
            if meta['type'] in ('axvspan', 'axhspan'):
                if meta['type'] == 'axvspan':
                    theMin  = meta['xmin']
                    theMax  = meta['xmax']
                else:
                    theMin  = meta['ymin']
                    theMax  = meta['ymax']
                props   = meta['props']
#                self.__figureBook.currentFigure.indicators.axvspan(xmin, xmax, **props)
                getattr(self.__figureBook.currentFigure.indicators, meta['type'])(theMin, theMax, **props)
                self.__figureBook.updateIndicatorList()

        
    def __init__(self, *args, **kwargs):
        '''
nodeName:   The name of this node. Usually set by ModelNode.__setattr__ automatically.
figureMeta: Meta information of figure.
The rest parameters are passed to PanedWindow.__init__.
'''
        nodeName    = kwargs.pop('nodeName', '')
        # lock
        
        super(FigureBook, self).__init__(nodeName=nodeName)

        figureMeta = None if 'figureMeta' not in kwargs \
            else kwargs.pop('figureMeta')
        kwargs['orient'] = HORIZONTAL
        
        panedWindow = PanedWindow(*args, **kwargs)

        panedWindow.config(sashwidth=4, sashrelief=GROOVE, bg='forestgreen')        
       
#        figureTabsStyle = Style()
#        figureTabsStyle.configure('Figure.TNotebook', tabposition='sw')       
#        figureTabs    = Notebook(panedWindow, style='Figure.TNotebook')
        figureTabs  = Notebook(panedWindow)
        
        self.figureTabs   = figureTabs
        figureTabs.bind('<<NotebookTabChanged>>', self.onTabChange)
        self.lockAttribute('figureTabs')
        
        if figureMeta:
            self.makeFigures(figureMeta)
            
        self.lockElements()    
        
        panedWindow.add(figureTabs, stretch='always')
        

        listPan     = PanedWindow(panedWindow, orient=VERTICAL)
        listPan.config(sashwidth=4, sashrelief=GROOVE, bg='forestgreen')        
        panedWindow.add(listPan, stretch='never')

        
        listFrm     = Frame(listPan)
        listPan.add(listFrm, stretch='always')        
        Label(listFrm, text='Curves', bg='#b5d6b0').pack(side=TOP, fill=X)                
        self.__list = ScrolledList(listFrm, relief=GROOVE)
        self.__list.listConfig(width=20)
        self.__list.listClick = self.onListClick
        self.__list.pack(fill=BOTH, expand=YES)  

        listFrm     = Frame(listPan)        
        listPan.add(listFrm, stretch='never')
        Label(listFrm, text='Indicators', bg='#b5d6b0').pack(side=TOP, fill=X)
        self.__indicatorListbox = ScrolledList(listFrm, relief=GROOVE)
        self.__indicatorListbox.listConfig(width=20)
        self.__indicatorListbox.pack(fill=BOTH, expand=YES)
        
      
        

        with self.attributeLock:
            setMultiAttr(self,
                panedWindow = panedWindow,
                gridGroupObserver   = self.GridGroupObserver(self), 
                axisGroupObserver   = self.AxisGroupObserver(self),
                clearGroupObserver  = self.ClearGroupObserver(self),
                indicatorGroupObserver  = self.IndicatorGroupObserver(self),
                dataPool    = []
            )
            
    def notifyObservers(self, **kwargs):
        cf      = self.currentFigure
        props   = ['majorGrid', 'minorGrid', 'xLim', 'yLim', 
                   'majorXTick', 'majorYTick', 'minorXTick', 'minorYTick']
        for p in props:
            if p not in kwargs:
                kwargs[p]   = getattr(cf, p)
        if cf.isPolar:
            kwargs['xLim']  = rad2deg(kwargs['xLim'])
            kwargs['majorXTick']    = rad2deg(kwargs['majorXTick'])
            if kwargs['minorXTick'] is not None:
                kwargs['minorXTick']    = rad2deg(kwargs['minorXTick'])
        super(FigureBook, self).notifyObservers(**kwargs)            
        
    def pack(self, *args, **kwargs):
        self.panedWindow.pack(*args, **kwargs)        
        
    def makeFigures(self, figureMeta):
        for meta in figureMeta:
            frm = Frame(self.figureTabs)
            fig = DataFigure(frm, isPolar=meta['polar'])
            self.figureTabs.add(frm, text=meta['name'])
            self.append(fig)        
        
    @property        
    def currentFigure(self):
        return self[self.figureTabs.index(CURRENT)]
        
    @property
    def currentFigureIndex(self):
        return self.figureTabs.index(CURRENT)
                
    def plot(self, *args, **kwargs):
        try:
            curveName = kwargs.pop('curveName')
        except KeyError:
            curveName = 'curve'
            
        for fig in self:
            fig.plotFunction(*args, **kwargs)
        self.__list.insert(END, curveName)
        
        if 'color' in kwargs:
            color   = colorMap[kwargs['color']]
        else:
            color   = colorMap[self[0].lineObjects[-1][0].get_color()]
        self.__list.itemConfig(END, fg=color)
        self.notifyObservers()
    
    @Scripting.printable
    def clear(self):
        for fig in self:
            fig.clear()
        self.__list.clear()
        del self.dataPool[:]
        self.currentFigure.indicators.clear()
        self.updateIndicatorList()
        
        
    def onTabChange(self, event): 
        self.notifyObservers()
        self.updateIndicatorList()          
        
    def onListClick(self, index, label):
        index = int(index)
        for figure in self:
            for line in figure.lineObjects:
                pyplot.setp(line, linewidth=1)
            pyplot.setp(figure.lineObjects[index], linewidth=2)
            figure.update()
            
    @Scripting.printable            
    def exportMatlabScript(self, filename):
        with open(filename, 'w') as file:
            for figure in self:
                print('%Generated by WaveSyn.',
                      'figure;', sep = '\n',
                      file=file)
                for line in figure.lineObjects:
                    params = {}
                    for name in ('xdata', 'ydata', 'color'):
                        params[name] = pyplot.getp(line[0], name)
                    params['func'] = 'polar' if figure.isPolar else 'plot'
                    params['xdata'] = ','.join((str(i) for i in params['xdata']))
                    params['ydata'] = ','.join((str(i) for i in params['ydata']))
                    print("{func}([{xdata}], [{ydata}], '{color}');hold on".format(**params), file=file)
                    # To do: Grid
                    
                    
    @Scripting.printable                    
    def deleteSelLines(self, idx=None):
        if idx is None:
            idx = self.__list.curSelection # idx is a tuple of strings.
            if len(idx) <= 0:
                return
            if len(idx) > 1:
                raise ValueError, 'Multi-selection is not supported.'
            idx = int(idx[0])
        for fig in self:
            fig.lineObjects[idx][0].remove()
            del fig.lineObjects[idx]
            fig.update()
        self.__list.delete(idx)
        del self.dataPool[idx]
        
    def updateIndicatorList(self):
        iList   = self.__indicatorListbox
        iList.delete(0, END)
        meta    = self.currentFigure.indicators.meta
        for m in meta:
            if m['type'] == 'axvspan':
                xmin    = m['xmin']
                xmax    = m['xmax']
                iList.insert(END, '{0}|{1}/{2}'.format('axvspan',xmin,xmax))
            elif m['type'] == 'axhspan':
                ymin    = m['ymin']
                ymax    = m['ymax']
                iList.insert(END, '{0}|{1}/{2}'.format('axhspan',ymin,ymax))
        



class GridGroup(Observable, Group):
    class FigureObserver(object):
        def __init__(self, gridGroup):
            self.__gridGroup    = gridGroup            
        def update(self, **kwargs):
            if 'majorGrid' in kwargs:
                self.__gridGroup.major  = kwargs['majorGrid']
            if 'minorGrid'  in kwargs:
                self.__gridGroup.minor  = kwargs['minorGrid']    
    
    def __init__(self, *args, **kwargs):
        if 'valueChecker' in kwargs:
            valueChecker    = kwargs.pop('valueChecker')
            checkPositiveFloat  = valueChecker.checkPositiveFloat
        else:
            checkPositiveFloat  = None
            
        if 'balloon' in kwargs:
            kwargs.pop('balloon')
        
        super(GridGroup, self).__init__(*args, **kwargs)
        
        major = IntVar(0)
        minor = IntVar(0)
        self.__major = major
        self.__minor = minor
        self.__figureObserver   = self.FigureObserver(self)
                                
        def askgridprop():
            win = Toplevel()
            color = ['#000000', '#000000']

            propvars = [StringVar() for i in range(4)]
            guidata = (
                {
                    'linestyle': ('Major Line Style', propvars[0], None),
########################################################################################################
                    'linewidth': ('Major Line Width', propvars[1], checkPositiveFloat)
                },
                {
                    'linestyle': ('Minor Line Style', propvars[2], None),
                    'linewidth': ('Minor Line Width', propvars[3], checkPositiveFloat)
#########################################################################################################
                }
            )

            for d in guidata:
                for key in d:
                    pitem = ParamItem(win)
                    pitem.pack()
                    pitem.labelText = d[key][0]
                    pitem.entry['textvariable'] = d[key][1]
                    if d[key][2]:
                        pitem.checkFunc = d[key][2]

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

        def onPropertyClick():
            ret = askgridprop()

            props  = {'major':{}, 'minor':{}}
            for idx, name in enumerate(('major', 'minor')):
                for key in ret[idx]:
                    value = ret[idx][key][1].get()
                    if value:
                        props[name][key] = value
            major.set(1)
            minor.set(1)
            self.notifyObservers(majorGrid=major.get(), minorGrid=minor.get(), props=props)
                                    
        chkGridMajor    = Checkbutton(self, text='Grid Major', variable=major, command=self.onChkClick)
        chkGridMajor.pack(fill=X)
        self.chkGridMajor   = chkGridMajor
        
        chkGridMinor    = Checkbutton(self, text='Grid Minor', variable=minor, command=self.onChkClick)
        chkGridMinor.pack(fill=X)
        self.chkGridMinor   = chkGridMinor        
        
        btnProperty     = Button(self, text='Property', command=onPropertyClick)
        btnProperty.pack()
        self.btnProperty    = btnProperty
        
        self.name = 'Grid'
        
    @property
    def figureObserver(self):
        return self.__figureObserver


    def onChkClick(self):
        self.notifyObservers(majorGrid=self.__major.get(), minorGrid=self.__minor.get())
        

        
    class __EnableDelegator(object):
        def __init__(self, widgetName):
            self.widgetName = widgetName
            
        def __get__(self, obj, type=None):
            def enable(state):                
                en  = NORMAL if state else DISABLED
                getattr(obj, self.widgetName).config(state=en)
            return enable
            
    enableWidgets   = dict(
        enableGridMajor =  'chkGridMajor',
        enableGridMinor =  'chkGridMinor',
        enableProperty  =  'btnProperty'
    )
    
    for methodName in enableWidgets:
        locals()[methodName]    = __EnableDelegator(enableWidgets[methodName])
        


    @property
    def major(self):
        return self.__major.get()

    @major.setter
    def major(self, value):
        self.__major.set(value)

    @property
    def minor(self):
        return self.__minor.get()

    @minor.setter
    def minor(self, value):
        self.__minor.set(value)  



class AxisGroup(Observable, Group):
    class FigureObserver(object):
        def __init__(self, axisGroup):
            self.__axisGroup    = axisGroup            
        def update(self, **kwargs):
            for XY in ('X', 'Y'):
                for mm in ('major', 'minor'):
                    prop    = ''.join((mm,XY,'Tick'))
                    if prop in kwargs:
                        val = kwargs[prop]
                        setattr(self.__axisGroup, prop, val)
            if 'xLim' in kwargs:
                self.__axisGroup.xLim   = kwargs['xLim']
            if 'yLim' in kwargs:
                self.__axisGroup.yLim   = kwargs['yLim']
    
    def __init__(self, *args, **kwargs):
#        app = Application.instance
        if 'valueChecker' in kwargs:
            valueChecker    = kwargs.pop('valueChecker')
            checkFloat  = valueChecker.checkFloat
        else:
            checkFloat  = None
            
        if 'balloon' in kwargs:
            balloonBindWidget   = kwargs.pop('balloon').bind_widget
        else:
            balloonBindWidget   = lambda *args, **kwargs: None
       
        super(AxisGroup, self).__init__(*args, **kwargs)
        self.__params = [StringVar() for i in range(8)]
        paramfrm =Frame(self)
        paramfrm.pack()
        names = ['xmin', 'xmax', 'ymin', 'ymax', 'major xtick', 'major ytick', 'minor xtick', 'minor ytick']
        images= ['ViewTab_XMin.png', 'ViewTab_XMax.png', 'ViewTab_YMin.png', 'ViewTab_YMax.png', 'ViewTab_MajorXTick.png', 'ViewTab_MajorYTick.png', 'ViewTab_MinorXTick.png', 'ViewTab_MinorYTick.png']
        for c in range(4):
            for r in range(2):
                temp = ParamItem(paramfrm)
                image   = ImageTk.PhotoImage(file=uiImagePath(images[c*2+r]))
                setMultiAttr(temp,
                    checkFunc   = checkFloat,
                    #labelText   = names[c*2+r],
                    labelImage  = image,
                    labelWidth  = 5 if c*2+r < 4 else 10,
                    entryWidth  = 5,
                    entryVar    = self.__params[c*2+r]
                )
                temp.entry.bind('<Return>', self.onConfirmClick)
                temp.grid(row=r, column=c)
                balloonBindWidget(temp, balloonmsg=names[c*2+r])
              

        btnfrm = Frame(self)
        btnfrm.pack()
        Button(btnfrm, text='Confirm', command=self.onConfirmClick).pack(side=LEFT)
        Button(btnfrm, text='Auto', command=self.onAutoClick).pack(side=RIGHT)
        self.name = 'Axis'        
        self.__figureObserver   = self.FigureObserver(self)


    @property
    def figureObserver(self):
        return self.__figureObserver


    @property
    def xLim(self):
        return tuple(map(lambda svar: float(svar.get()), self.__params[0:2]))

    @xLim.setter
    def xLim(self, value):
        self.__params[0].set(str(value[0]))
        self.__params[1].set(str(value[1]))

    @property
    def yLim(self):
        return tuple(map(lambda svar: float(svar.get()), self.__params[2:4]))

    @yLim.setter
    def yLim(self, value):
        self.__params[2].set(str(value[0]))
        self.__params[3].set(str(value[1]))
               
    for propName, propIdx   in (('majorXTick', 4), ('majorYTick', 5), ('minorXTick', 6), ('minorYTick', 7)):
        prop  = property(lambda self, idx=propIdx: float(self.__params[idx].get()))
        locals()[propName]  = prop.setter(lambda self, val, idx=propIdx: self.__params[idx].set(str(val)))



    def onConfirmClick(self, event=None):
        def toFloat(x):
            try:
                return float(x)
            except:
                return None
        p = [toFloat(v.get()) for v in self.__params]
        self.notifyObservers(xLim=p[0:2], yLim=p[2:4], majorXTick=p[4], majorYTick=p[5], minorXTick=p[6], minorYTick=p[7])

    def onAutoClick(self):
        self.notifyObservers(xLim=None, yLim=None, majorXTick=None, majorYTick=None, minorXTick=None, minorYTick=None, autoScale=True)



class ClearGroup(Observable, Group):
    def __init__(self, *args, **kwargs):
        super(ClearGroup, self).__init__(*args, **kwargs)
        Button(self, text='Clear All', command=self.onClearAll).pack()
        Button(self, text='Del Sel', command=self.onDelSel).pack()
        Button(self, text='Del UnSel', command=self.onDelUnSel).pack()
        self.name = 'Clear Plot'

    def onClearAll(self):
        self.notifyObservers('all')

    def onDelSel(self):
        self.notifyObservers('sel')

    def onDelUnSel(self):
#        printCode   = True
        #self.__topwin.figureBook.remove_unsel_lines()            
        pass



class IndicatorGroup(Observable, Group):
    def __init__(self, *args, **kwargs):
        super(IndicatorGroup, self).__init__(*args, **kwargs)
        indicatorList    = Combobox(self, value=[], takefocus=1, stat='readonly', width=9)
        indicatorList['value']  = ['axvspan', 'axhspan']
        indicatorList.current(0)
        self.__indicatorList    = indicatorList
        self.__indicatorList.pack()
        Button(self, text='Add', command=self.onAdd).pack()
        self.name   = 'Indicators'
        
    def onAdd(self):
        indicatorType   = self.__indicatorList.get()
        def askSpan(orient='v'):
            win = Toplevel()
            pxmin   = ParamItem(win)
            pxmin.pack()
            pxmin.labelText = 'xmin' if orient=='v' else 'ymin'
            pxmax   = ParamItem(win)
            pxmax.pack()
            pxmax.labelText = 'xmax' if orient=='v' else 'ymax'
            def formatter(val):
                val = float(val)
                val /= 100.
                return '{0:0.2f}'.format(val)
            alphaScale  = LabeledScale(win, from_=0, to=100, name='alpha', formatter=formatter)
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
                theMin, theMax, alpha  = askSpan(indicatorType[2])
            except ValueError:
                return
            meta    = {
                'type':     indicatorType,
                'props':    {'alpha':alpha}
            }
            if indicatorType == 'axvspan':
                meta['xmin']    = theMin 
                meta['xmax']    = theMax
                meta['ymin']    = 0.0
                meta['ymax']    = 1.0
            else:
                meta['xmin']    = 0.0
                meta['xmax']    = 1.0
                meta['ymin']    = theMin
                meta['ymax']    = theMax
            self.notifyObservers(meta)            



class FigureExportGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        self.__uiImages = []
        imageFigureExportBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_ExportFigure_Button.png')
        )
        self.__uiImages.append(imageFigureExportBtn)
        frm = Frame(self); frm.pack(side=LEFT)
        Button(frm, image=imageFigureExportBtn, command=self.onExportMatlabScript).pack(side=TOP)
        Button(frm, text='Script', command=self.onExportMatlabScript, width=6).pack(side=TOP)
        
        self.name = 'Figure'
        

    def onExportMatlabScript(self):
        printCode   = True
        filename = asksaveasfilename(filetypes=[('Matlab script files', '*.m')])
        if not filename:
            return
        self.__topwin.figureBook.exportMatlabScript(filename)
        self._app.printTip(
            autoSubs(
                '''A Matlab script file has been saved as $filename.
By running this script, Matlab will literally "re-plot" the curves shown here.'''
            )
        ) 
                
                
class FigureWindow(WindowNode):
    _xmlrpcexport_  = ['plotCurrentData']    
    
    def __init__(self, *args, **kwargs):
        super(FigureWindow, self).__init__(*args, **kwargs)               
        toolTabs    = Notebook(self._toplevel)
        toolTabs.pack(fill=X)       
        with self.attributeLock:
            self.toolTabs   = toolTabs
        
        figureBook  = FigureBook(self._toplevel)
        figureBook.pack(expand=YES, fill=BOTH)                
        self.figureBook = figureBook
        
        app = Application.instance
        self.balloon    = app.balloon
        self.valueChecker   = app.valueChecker
        
        
    @property
    def currentData(self):
        if self.figureBook.dataPool:
            return self.figureBook.dataPool[-1]
            
    @currentData.setter
    def currentData(self, data):
        if data is not None:
            self.figureBook.dataPool.append(data)
            
    @property
    def dataPool(self):
        return self.figureBook.dataPool
         
  
    def makeViewTab(self):
        toolTabs    = self.toolTabs
        frmView = Frame(toolTabs)
        
        grpGrid = GridGroup(frmView, bd=2, relief=GROOVE, balloon=self.balloon, valueChecker=self.valueChecker)
        grpGrid.pack(side=LEFT, fill=Y)
        grpGrid.addObserver(self.figureBook.gridGroupObserver)
        self.figureBook.addObserver(grpGrid.figureObserver)
      
        
        grpAxis = AxisGroup(frmView, bd=2, relief=GROOVE, balloon=self.balloon, valueChecker=self.valueChecker)
        grpAxis.pack(side=LEFT, fill=Y)
        grpAxis.addObserver(self.figureBook.axisGroupObserver)
        self.figureBook.addObserver(grpAxis.figureObserver)
      
        
        grpClear = ClearGroup(frmView, bd=2, relief=GROOVE)
        grpClear.pack(side=LEFT, fill=Y)
        grpClear.addObserver(self.figureBook.clearGroupObserver)
        
        grpIndicator    = IndicatorGroup(frmView, bd=2, relief=GROOVE)
        grpIndicator.pack(side=LEFT, fill=Y)
        grpIndicator.addObserver(self.figureBook.indicatorGroupObserver)
        
        with self.attributeLock:    
            setMultiAttr(self,
                grpGrid  = grpGrid,
                grpAxis  = grpAxis,
                grpClear = grpClear,
                grpIndicator    = grpIndicator,
                viewFrame  = frmView
            )
            
        toolTabs.add(frmView, text='View')
            
            
    def makeExportTab(self):
        toolTabs    = self.toolTabs
        frmExport   = Frame(toolTabs)
        grpFigureExport   = FigureExportGroup(frmExport, bd=2, relief=GROOVE, topwin=self)
        grpFigureExport.pack(side=LEFT, fill=Y)
        
        with self.attributeLock:
            setMultiAttr(self,
                 grpFigureExport  = grpFigureExport,
                 exportFrame      = frmExport
            )
            
        toolTabs.add(frmExport, text='Export')
            

    @Scripting.printable    
    def plotCurrentData(self):        
        self.figureBook.plot(self.currentData)                    
 
