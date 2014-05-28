# -*- coding: utf-8 -*-
"""
Created on Fri May 23 15:58:34 2014

@author: Feng-cong Li
"""
from __future__ import print_function, division

from tkColorChooser import askcolor

from Tkinter import *
from ttk import *
from Tkinter import Frame, PanedWindow

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.ticker import MultipleLocator
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as pyplot


from application import Application, Scripting
from objectmodel import ModelNode, NodeList, NodeDict
from common import autoSubs, evalFmt, setMultiAttr
from guicomponents import Group, ParamItem, ScrolledList


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
    def __init__(self, *args, **kwargs):
        super(WindowNode, self).__init__(*args, **kwargs)
        self._toplevel = Toplevel()
        self._toplevel.title(evalFmt('{self.windowName} id={id(self)}'))        
        self._toplevel.protocol('WM_DELETE_WINDOW', self.onClose)
        
    def update(self):
        self._toplevel.update()
        
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

  
class DataFigure(ModelNode):
    def __init__(self, master, topwin, nodeName='', figsize=(5,4), dpi=100, isPolar=False):
        super(DataFigure, self).__init__(nodeName=nodeName)
        
        figure = Figure(figsize, dpi)
        self.__topwin   = topwin
        
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

        
        self.plotFunction = None
        
        self.index  = None # Used by FigureList
        
        self.__majorGrid    = isPolar
        self.__minorGrid    = False

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


    @Scripting.printable    
    def update(self):
        self.__canvas.show()

    def updateViewTab(self):    
        grpAxis = self.__topwin.grpAxis
        axes    = self.axes
        
        grpAxis.xlim    = axes.get_xlim()
        grpAxis.ylim    = axes.get_ylim()
        
        #To do: using a list with tuples instead
        attr_func   = {
            'major_xtick':  axes.xaxis.get_major_locator,
            'major_ytick':  axes.yaxis.get_major_locator,
            'minor_xtick':  axes.xaxis.get_minor_locator,
            'minor_ytick':  axes.yaxis.get_minor_locator
        }
        
        for attr in attr_func:
            tick    = attr_func[attr]()()
            if len(tick) >= 2:
                tick    = tick[1] - tick[0]
                setattr(grpAxis, attr, tick)
                
        self.__topwin.grpGrid.major = self.majorGrid
        self.__topwin.grpGrid.minor = self.minorGrid                

    def clear(self):
        self.axes.clear()
        del self.lineObjects[:]
        self.update()
        self.__topwin.grpGrid.major = 0
        self.__topwin.grpGrid.minor = 0
        
    def axis(self, r):
        return self.axes.axis(r)
            
    def deleteLine(self, idx):
        lineObject = self.lineObjects[idx]
        lineObject.remove()
        del self.lineObjects[idx]

    def remove_unsel_lines(self):
        sel = self.__slist.list.curselection()
        if len(sel) > 0:
            sel = int(sel[0])
            linemeta = self.__meta_of_lines[sel]
            k = 0
            for idx in range(len(self.__meta_of_lines)):
                if self.__meta_of_lines[k] != linemeta:
                    self.__meta_of_lines[k].lineobj.remove()
                    self.__slist.list.delete(0)
                    del self.__meta_of_lines[0]
                    self.update()
                else:
                    k += 1

        
class FigureList(NodeList):
    def __init__(self, nodeName=''):
        super(FigureList, self).__init__(nodeName=nodeName)
        
    def append(self, val):        
        if not isinstance(val, DataFigure):
            raise TypeError, evalFmt('{self.nodePath} only accepts instance of DataFigure or of its subclasses.')
        NodeList.append(self, val)
        

class FigureBook(FigureList):         
    def __init__(self, *args, **kwargs):
        '''
nodeName:   The name of this node. Usually set by ModelNode.__setattr__ automatically.
figureMeta: Meta information of figure.
The rest parameters are passed to PanedWindow.__init__.
'''
        nodeName    = kwargs.pop('nodeName', '')
        topwin      = kwargs.pop('topwin')        
        self.__topwin = topwin
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
        
        self.__list = ScrolledList(panedWindow, relief=GROOVE)
        self.__list.listConfig(width=20)
        self.__list.listClick = self.onListClick
        panedWindow.add(self.__list, stretch='never')
        
        self.panedWindow    = panedWindow
        self.lockAttribute('panedWindow')
        
    def pack(self, *args, **kwargs):
        self.panedWindow.pack(*args, **kwargs)        
        
    def makeFigures(self, figureMeta):
        for meta in figureMeta:
            frm = Frame(self.figureTabs)
            fig = DataFigure(frm, self.__topwin, isPolar=meta['polar'])
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
        
        self.currentFigure.updateViewTab()
    
    @Scripting.printable
    def clear(self):
        for fig in self:
            fig.clear()
        self.__list.clear()
        
        
    def onTabChange(self, event):
        self.currentFigure.updateViewTab()            
        
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



class GridGroup(Group):
    def __init__(self, *args, **kwargs):
        self.__topwin   = kwargs.pop('topwin')
        super(GridGroup, self).__init__(*args, **kwargs)
        app = Application.instance
        major = IntVar(0)
        minor = IntVar(0)
        self.__major = major
        self.__minor = minor
                        
                        
        def setgrid():
            currentFigure = self.__topwin.figureBook.currentFigure
            currentFigure.majorGrid = major.get()
            currentFigure.minorGrid = minor.get()
            currentFigure.update()


        def askgridprop():
            win = Toplevel()
            color = ['#000000', '#000000']

            propvars = [StringVar() for i in range(4)]
            guidata = (
                {
                    'linestyle': ('Major Line Style', propvars[0], None),
########################################################################################################
                    'linewidth': ('Major Line Width', propvars[1], app.checkPositiveFloat)
                },
                {
                    'linestyle': ('Minor Line Style', propvars[2], None),
                    'linewidth': ('Minor Line Width', propvars[3], app.checkPositiveFloat)
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

            for idx, name in enumerate(('major', 'minor')):
                for key in ret[idx]:
                    value = ret[idx][key][1].get()
                    if value:
                        self.__topwin.figureBook.currentFigure.axes.grid(None, name, **{key: value})
            major.set(1)
            minor.set(1)
            self.__topwin.figureBook.currentFigure.update()
                                    
        chkGridMajor    = Checkbutton(self, text='Grid Major', variable=major, command=self.onChkGridMajor)
        chkGridMajor.pack(fill=X)
        self.chkGridMajor   = chkGridMajor
        
        chkGridMinor    = Checkbutton(self, text='Grid Minor', variable=minor, command=setgrid)
        chkGridMinor.pack(fill=X)
        self.chkGridMinor   = chkGridMinor        
        
        btnProperty     = Button(self, text='Property', command=onPropertyClick)
        btnProperty.pack()
        self.btnProperty    = btnProperty
        
        self.name = 'Grid'
        
    def onChkGridMajor(self):        
        printCode    = True
        currentFigure   = self.__topwin.figureBook.currentFigure
        currentFigure.grid(self.__major.get(), which='major')
        currentFigure.update()
        

        
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


class AxisGroup(Group):
    def __init__(self, *args, **kwargs):
        self.__topwin = kwargs.pop('topwin')
        app = Application.instance
       
        super(AxisGroup, self).__init__(*args, **kwargs)
        self.__params = [StringVar() for i in range(8)]
        paramfrm =Frame(self)
        paramfrm.pack()
        names = ['xmin', 'xmax', 'ymin', 'ymax', 'major xtick', 'major ytick', 'minor xtick', 'minor ytick']
        for c in range(4):
            for r in range(2):
                temp = ParamItem(paramfrm)
                setMultiAttr(temp,
                    checkFunc   = app.checkFloat,
                    labelText   = names[c*2+r],
                    labelWidth  = 5 if c*2+r < 4 else 10,
                    entryWidth  = 5,
                    entryVar    = self.__params[c*2+r]
                )
                temp.grid(row=r, column=c)

        btnfrm = Frame(self)
        btnfrm.pack()
        Button(btnfrm, text='Confirm', command=self.onConfirmClick).pack(side=LEFT)
        Button(btnfrm, text='Auto', command=self.onAutoClick).pack(side=RIGHT)
        self.name = 'Axis'



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
               
    for propName, propIdx   in (('major_xtick', 4), ('major_ytick', 5), ('minor_xtick', 6), ('minor_ytick', 7)):
        prop  = property(lambda self, idx=propIdx: float(self.__params[idx].get()))
        locals()[propName]  = prop.setter(lambda self, val, idx=propIdx: self.__params[idx].set(str(val)))



    def onConfirmClick(self):
        def toFloat(x):
            try:
                return float(x)
            except:
                return None
        aparams = [toFloat(v.get()) for v in self.__params]
        currentFigure   = self.__topwin.figureBook.currentFigure
        currentFigure.axis(aparams[:4])
        axes    = currentFigure.axes
        axes.xaxis.set_major_locator(MultipleLocator(float(aparams[4])))
        axes.yaxis.set_major_locator(MultipleLocator(float(aparams[5])))
        if aparams[6] is not None:
            axes.xaxis.set_minor_locator(MultipleLocator(float(aparams[6])))
        if aparams[7] is not None:
            axes.yaxis.set_minor_locator(MultipleLocator(float(aparams[7])))
        currentFigure.update()

    def onAutoClick(self):
        currentFigure   = self.__topwin.figureBook.currentFigure
        currentFigure.axes.autoscale()
        currentFigure.update()
        currentFigure.updateViewTab()


class ClearGroup(Group):
    def __init__(self, *args, **kwargs):
        self.__topwin = kwargs.pop('topwin')

        super(ClearGroup, self).__init__(*args, **kwargs)
        self.__currentFigure = None
        Button(self, text='Clear All', command=self.onClearAll).pack()
        Button(self, text='Del Sel', command=self.onDelSel).pack()
        Button(self, text='Del UnSel', command=self.onDelUnSel).pack()
        self.name = 'Clear Plot'

    def onClearAll(self):
        printCode   = True
        self.__topwin.figureBook.clear()

    def onDelSel(self):
        printCode   = True
        self.__topwin.figureBook.deleteSelLines(idx=None)

    def onDelUnSel(self):
        printCode   = True
        #self.__topwin.figureBook.remove_unsel_lines()            

                
                
class FigureWindow(WindowNode):
    def __init__(self, *args, **kwargs):
        super(FigureWindow, self).__init__(*args, **kwargs)
        toolTabs    = Notebook(self._toplevel)
        toolTabs.pack(fill=X)
        with self.attributeLock:
            self.toolTabs   = toolTabs
        
        figureBook  = FigureBook(self._toplevel, topwin=self)
        figureBook.pack(expand=YES, fill=BOTH)                
        self.figureBook = figureBook
         
  
    def makeViewTab(self):
            # View Tab
        toolTabs    = self.toolTabs
        frmView = Frame(toolTabs)
        grpGrid = GridGroup(frmView, bd=2, relief=GROOVE, topwin=self)
        grpGrid.pack(side=LEFT, fill=Y)
      
        
        grpAxis = AxisGroup(frmView, bd=2, relief=GROOVE, topwin=self)
        grpAxis.pack(side=LEFT, fill=Y)
      
        
        grpClear = ClearGroup(frmView, bd=2, relief=GROOVE, topwin=self)
        grpClear.pack(side=LEFT, fill=Y)
        
        with self.attributeLock:    
            setMultiAttr(self,
                grpGrid  = grpGrid,
                grpAxis  = grpAxis,
                grpClear = grpClear  
            )
            
        toolTabs.add(frmView, text='View')
            # End View Tab        
####################################################   