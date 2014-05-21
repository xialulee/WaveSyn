# -*- coding: utf-8 -*-
"""
Created on Fri May 02 15:48:27 2014

@author: Feng-cong Li. xialulee@sina.com
"""
from __future__ import division
from __future__ import print_function


def dependenciesForMyprogram():
    '''This function is used to solve the bugs of py2exe'''
    from scipy.sparse.csgraph import _validation
    from scipy.special import _ufuncs_cxx

import threading
import Queue

import os
import os.path
import sys
REALSTDOUT = sys.stdout
REALSTDERR = sys.stderr

from Tkinter import *
from ttk import *
import Tix
from Tkinter import Frame, PanedWindow
from tkColorChooser import askcolor
from tkFileDialog import askopenfilename, asksaveasfilename

from PIL import ImageTk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.ticker import MultipleLocator
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as pyplot


from numpy import *
from scipy.io import savemat

from functools  import partial
from datetime   import datetime
from inspect    import getsourcefile
import webbrowser
import subprocess
import tempfile
import json
import traceback

# Some console functionalities are implemented by idlelib
##########################
from idlelib.AutoComplete import AutoComplete
from idlelib.Percolator import Percolator
from idlelib.ColorDelegator import ColorDelegator
##########################

from objectmodel import ModelNode, NodeDict, NodeList

from guicomponents import Group, StreamChain, TaskbarIcon, ParamItem, ScrolledList, ScrolledText
import guicomponents

from common import setMultiAttr, autoSubs, evalFmt, ObjectWithLock, Singleton, MethodDelegator



def checkValue(d, i, P, s, S, v, V, W, func):
    try:
        func(P)
        return True
    except ValueError:
        return True if P=='' or P=='-' else False
        
def checkPositiveFloat(d, i, P, s, S, v, V, W):
    try:
        float(P)
        return True
    except ValueError:
        return True if P=='' else False

       

        
# Scripting Sub-System
class ScriptCode(object):
    def __init__(self, code):
        self.code = code
        
class Scripting(ModelNode):
    rootName = 'wavesyn' # The name of the object model tree's root
    nameSpace = {'locals':{}, 'globals':{}}
    
    @staticmethod
    def paramsToStr(*args, **kwargs):
        def paramToStr(param):
            if isinstance(param, ScriptCode):
                return param.code
            else:
                return repr(param)
                
        strArgs = ', '.join([paramToStr(arg) for arg in args]) if args else ''
        strKwargs = ', '.join([evalFmt('{key}={paramToStr(kwargs[key])}') for key in kwargs]) \
            if kwargs else ''        
       
            
        if strArgs and strKwargs:
            params = ', '.join((strArgs, strKwargs))
        else:
            params = strArgs if strArgs else strKwargs
        return params
        
    def __init__(self, rootNode):
        ModelNode.__init__(self)
        self.__rootNode = rootNode
            
    def executeFile(self, filename):
        execfile(filename, **self.nameSpace) #?
                
    @staticmethod    
    def printable(method):
        def func(self, *args, **kwargs):
            callerLocals    = sys._getframe(1).f_locals
            #####################################
            #print(method.__name__, True if 'printCode' in callerLocals else False)
            #####################################            
            if 'printCode' in callerLocals and callerLocals['printCode']:
                ret = Application.instance.printAndEval(
                    evalFmt(
                        '{self.nodePath}.{method.__name__}({Scripting.paramsToStr(*args, **kwargs)})'
                    )
                )
            else:                          
                ret = method(self, *args, **kwargs)
            return ret
        func.__doc__    = method.__doc__
        func.__name__   = method.__name__
        return func

                                   
# End Scripting Sub-System
        
        


def makeMenu(win, menu, json=False):
    def funcGen(code, printCode=True):
        if printCode:
            f   = Application.instance.printAndEval
        else:
            f   = Application.instance.eval
        return lambda: f(code)
    def make(top, tree):
        for topItem in tree:
            if 'Command' in topItem:
                if json: # json cannot store callable objects.
                    printCode   = topItem.get('Print', True)
                    cmd = funcGen(topItem['Command'], printCode)
                else:
                    # Python data object can store callable object, 
                    # and topItem['Command'] should be a callable object in this circumstance.
                    cmd = topItem['Command'] 
                top.add_command(label=topItem['Name'], command=cmd, underline=topItem['UnderLine'])
            else:
                tearoff = 1 if 'TearOff' not in topItem else int(topItem['TearOff'])
                submenu = Menu(top, tearoff=tearoff)
                make(submenu, topItem['SubMenu']) # recursion
                top.add_cascade(label=topItem['Name'], menu=submenu, underline=int(topItem['UnderLine']))
    top = Menu(win)
    make(top, menu)
    win.config(menu=top)        
        

        
def callAndPrintDoc(func):
    '''This function is used as a decorator.'''
    def f(*args, **kwargs):
        ret = func(*args, **kwargs)
        if 'printDoc' in kwargs and kwargs['printDoc']:
            Application.instance.printTip(func.__doc__)
        return ret
    f.__doc__   = func.__doc__
    return f



class WaveSynThread(object):
    class Thread(threading.Thread):
        def __init__(self, func):
            self.func   = func
            threading.Thread.__init__(self)
            
        def run(self):
            self.func()
            
    @staticmethod
    def start(func):
        app = Application.instance
        thread  = WaveSynThread.Thread(func)
        thread.start()
        while thread.isAlive():
            app.root.update()
            for winId in app.windows:
                app.windows[winId].update()



class Application(ModelNode):
    '''This class is the root of the model tree.
In the scripting system, it is named as "wavesyn" (case sensitive).
It also manages the whole application and provide services for other components.
For other nodes on the model tree, the instance of Application can be accessed by Application.instance,
since the instance of Application is the first node created on the model tree.
The model tree of the application is illustrated as follows:
wavesyn
-console
-clipboard
-windows[id]
    -instance of PatternFitting
        -figureBook
    -instance of SingleSyn
        -figureBook
    -instance of MIMOSyn
        -figureBook
'''    
    __metaclass__ = Singleton
    ''' '''
    def __init__(self):
        # The instance of this class is the root of the model tree. Thus isRoot is set to True
        ModelNode.__init__(self, nodeName=Scripting.rootName, isRoot=True)
        Scripting.nameSpace['locals'][Scripting.rootName] = self
        Scripting.nameSpace['globals'] = globals()
        self.homePage = 'https://github.com/xialulee/WaveSyn'
        
        filePath    = getsourcefile(type(self))
        dirPath     = os.path.split(filePath)[0]
        # load config file
        with open(os.path.join(dirPath, 'config.json')) as f:
            config  = json.load(f)
        consoleMenu = config['ConsoleMenu']
        self.editorInfo   = config['EditorInfo']
        self.lockAttribute('editorInfo')
        self.promptSymbols  = config['PromptSymbols']
        tagDefs = config['TagDefs']
        # End load config file

        root = Tix.Tk()
        
        with self.attributeLock:
            setMultiAttr(self,
                # UI elements
                root = root,        
                balloon = Tix.Balloon(root),
                tbicon = TaskbarIcon(root),
                # End UI elements
            
                # Validation Functions
                checkInt = (root.register(partial(checkValue, func=int)),
                    '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'),
                checkFloat = (root.register(partial(checkValue, func=float)),
                    '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'),
                checkPositiveFloat = (root.register(checkPositiveFloat),
                       '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W'),
                # End Validation Functions
                
                filePath    = filePath,
                dirPath     = dirPath
            )
        
                                          
        self.windows = WindowDict() # Instance of ModelNode can be locked automatically.
        
        frm = Frame(root)
        frm.pack(side=TOP, fill=X)
                  
        self.console = ConsoleWindow(menu=consoleMenu, tagDefs=tagDefs)
     
        
        self.clipboard = Clipboard()
        self.scripting = Scripting(self)
        self.noTip = False
        
        

    def newSingleWin(self, printDoc=False):
        print('Not Implemented.', file=sys.stderr)
        
    def newMIMOWin(self, printDoc=False):
        print('Not Implemented.', file=sys.stderr)

    @callAndPrintDoc        
    def newPatternWin(self, printDoc=False):
        '''This method creates a new PatternFitting window.
Its return value is the ID of the new window.
You can access the created window using its ID in the scripting system.
A PatternWindow can synthesize a correlation matrix of which the beam pattern fits the given ideal pattern best.'''        
        return self.windows.add(node=PatternWindow())
                     
        
    def printAndEval(self, expr):
        self.console.write(expr+'\n', 'HISTORY')
        ret = eval(expr, Scripting.nameSpace['globals'], Scripting.nameSpace['locals'])
        if ret != None:
            self.console.write(str(ret)+'\n', 'RETVAL')
        return ret
                              
    def eval(self, expr):
        ret = eval(expr, Scripting.nameSpace['globals'], Scripting.nameSpace['locals'])
        Scripting.nameSpace['locals']['_']  = ret
        return ret
        
    def execute(self, code):
        ret = None
        strippedCode    = code.strip()
        if strippedCode[0] == '!':
            # To do: system(code)
            PIPE    = subprocess.PIPE
            p = subprocess.Popen(strippedCode[1:], shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)  
            (stdout, stderr)    = p.communicate()
            print(stdout)
            print(stderr, file=sys.stderr)
            return
        try:
            ret = self.eval(code)
        except SyntaxError:
            exec code in Scripting.nameSpace['globals'], Scripting.nameSpace['locals']
        return ret
        
            
    def printTip(self, contents):
        if self.noTip:
            return
        console = self.console
        console.write('WaveSyn: ', 'TIP')
        if type(contents)==str:
            console.write(contents+'\n', 'TIP')
            return
        for item in contents:
            if item['type'] == 'text':
                console.write(''.join((item['content'],'\n')), 'TIP')
            elif item['type'] == 'link':
                command = item['command']
                tagName = 'link' + str(id(command))
                console.write(item['content'], tagName)
                text    = console.text
                r, c = text.index(END).split('.')
                text.tag_config(tagName, underline=1, foreground='blue')
                text.tag_bind(tagName, '<Button-1>', command) # href implementation shold be added.
                text.tag_bind(tagName, '<Enter>', lambda dumb: text.config(cursor='hand2'))
                text.tag_bind(tagName, '<Leave>', lambda dumb: text.config(cursor=self.console.defaultCursor))
                console.write('\n')
                
                                            
                
    def printError(self, text):
        self.console.write(text+'\n', 'STDERR')
        
            
    def notifyWinQuit(self, win):
        self.printTip(evalFmt('{win.nodePath} is closed, and its ID becomes defunct for scripting system hereafter'))
        self.windows.pop(id(win))
        
        
    def openHomePage(self):
        webbrowser.open(self.homePage, new=1, autoraise=True)
             
                    
    def mainloop(self):
        return self.root.mainloop()
        
        
def uiImagePath(filename):
    return os.path.join(Application.instance.dirPath, 'images', filename)        
        
        

class Clipboard(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
       
    @Scripting.printable
    def clear(self):
        Application.instance.root.clipboard_clear()
    
    @Scripting.printable
    def append(self, content):
        Application.instance.root.clipboard_append(content)
        
        
        
colorMap = {
    'c': 'cyan',
    'm': 'magenta',
    'y': 'yellow',
    'k': 'black',
    'r': 'red',
    'g': 'forestgreen',
    'b': 'blue'
}






  
class DataFigure(ModelNode):
    def __init__(self, master, topwin, nodeName='', figsize=(5,4), dpi=100, isPolar=False):
        ModelNode.__init__(self, nodeName=nodeName)
        
        figure = Figure(figsize, dpi)
        self.__topwin   = topwin
        
        canvas = FigureCanvasTkAgg(figure, master=master)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=YES)
        self.__canvas = canvas
        toolbar = NavigationToolbar2TkAgg(canvas, master)
        toolbar.update()
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
    def grid(self, *args, **kwargs):
        self.axes.grid(*args, **kwargs)

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
        NodeList.__init__(self, nodeName=nodeName)
        
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
        
        FigureList.__init__(self, nodeName=nodeName)

        figureMeta = kwargs.pop('figureMeta')
        kwargs['orient'] = HORIZONTAL
        
        panedWindow = PanedWindow(*args, **kwargs)

        panedWindow.config(sashwidth=4, sashrelief=GROOVE, bg='forestgreen')        
        
        tabpages    = Notebook(panedWindow)
        self.tabpages   = tabpages
        tabpages.bind('<<NotebookTabChanged>>', self.onTabChange)
        self.lockAttribute('tabpages')
        
        for meta in figureMeta:
            frm = Frame(tabpages)
            fig = DataFigure(frm, topwin, isPolar=meta['polar'])
            tabpages.add(frm, text=meta['name'])
            self.append(fig)
            
        self.lockElements()    
        
        panedWindow.add(tabpages, stretch='always')
        
        self.__list = ScrolledList(panedWindow, relief=GROOVE)
        self.__list.listConfig(width=20)
        self.__list.listClick = self.onListClick
        panedWindow.add(self.__list, stretch='never')
        
        self.panedWindow    = panedWindow
        self.lockAttribute('panedWindow')
        
    @property        
    def currentFigure(self):
        return self[self.tabpages.index(CURRENT)]
        
    @property
    def currentFigureIndex(self):
        return self.tabpages.index(CURRENT)
                
    def plot(self, *args, **kwargs):
        try:
            curveName = kwargs.pop('curveName')
        except KeyError:
            curveName = 'curve'

        for fig in self:
            fig.plotFunction(*args, **kwargs)
        self.__list.insert(END, curveName)
        if 'color' in kwargs:
            self.__list.itemConfig(END, fg=colorMap[kwargs['color']])
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
                
                
        
                

# How to implement a thread safe console?
# see: http://effbot.org/zone/tkinter-threads.htm
class ConsoleText(ScrolledText):
    def __init__(self, *args, **kwargs):
        ScrolledText.__init__(self, *args, **kwargs)
        self.__queue    = Queue.Queue()
        self.text.tag_configure('STDOUT',   foreground='black')
        self.text.tag_configure('STDERR',   foreground='red')
        self.text.tag_configure('TIP', foreground='forestgreen')
        self.text.tag_configure('HISTORY',   foreground='purple')
        self.text.tag_configure('RETVAL',    foreground='orange')
        
        self.text.bind('<KeyPress>', self.onKeyPress)

        
        # Experimenting with idlelib.AutoComplete
        #############################################################
        self.indentwidth    = 4
        self.tabwidth       = 4
        self.context_use_ps1    = '>>> '
        self.__autoComplete = AutoComplete(self)        
        #############################################################
                
        # Syntax highlight is implemented by idlelib
        #############################################################                
        self.percolator = Percolator(self.text)
        self.colorDelegator = ColorDelegator()
        self.percolator.insertfilter(self.colorDelegator)   
        #############################################################
                
        class StdOut:
            def write(obj, content):
                self.write(content, 'STDOUT')

        class StdErr:
            def write(obj, content):
                self.write(content, 'STDERR')
                
        self.__stdout   = StreamChain()
        self.__stdout   += sys.stdout
        self.__stdout   += StdOut()

        self.__stderr   = StreamChain()
        self.__stderr   += sys.stderr
        self.__stderr   += StdErr()

        sys.stdout      = self.__stdout
        sys.stderr      = self.__stderr
        
        self.promptSymbol = '>>> '
        
        self.updateContent()
        
    def write(self, content, tag=''):
        # The write method does not insert text into the console window.
        # The actural "write" operation is carried out by "updateContent".
        self.__queue.put((tag, content))
        self.update()

    def updateContent(self):

        try:
            while True:
                tag, content    = self.__queue.get_nowait()
                r, c    = self.getCursorPos(END)
                start   = 'end-5c'
                stop    = 'end-1c'
                if self.text.get(start, stop) == '>>> ' or self.text.get(start, stop) == '... ':
                    self.text.delete(start, stop)
        
                # Record the position of the END before inserting anything.
                start    = self.text.index(END)
        
                self.text.insert(END, content, tag)
        
                # Remove unnecessary highlighting
                for tag in self.colorDelegator.tagdefs:
                    self.text.tag_remove(tag, start, "end")
                    
        
                self.text.insert(END, self.promptSymbol)
                
                
                # Remove unnecessary highlighting
                self.text.tag_remove("TODO", "1.0", END)
                self.text.tag_add("SYNC", "1.0", END)                                
                self.text.see(END)
                

        except Queue.Empty:
            pass
        finally:
            self.after(100, self.updateContent)
        

    def onKeyPress(self, evt, codeList=[]):   
        #print (evt.keycode)        
        if evt.keycode not in range(16, 19) and evt.keycode not in range(33, 41):
            r, c    = self.getCursorPos()
            prompt  = self.text.get(autoSubs('$r.0'), autoSubs('$r.4'))
            if prompt != '>>> ' and prompt != '... ':
                return 'break'
            if evt.keycode==8 and c <= 4:
                return 'break'
            if c < 4:
                return 'break'
            rend, cend  = self.getCursorPos('end-1c')
            if r < rend:
                return 'break'                
            if evt.keycode == 13:
                app = Application.instance
                code    = self.text.get(autoSubs('$r.4'), autoSubs('$r.end'))
                try:
                    strippedCode     = code.strip()
                    if strippedCode and strippedCode[0] == '!':
                        # Execute a system command
                        app.execute(code)
                        self.promptSymbol   = '>>> '
                        self.write('\n')
                        return 'break'
                    if strippedCode == '':
                        code    = '\n'.join(codeList)
                        del codeList[:]
                    strippedCode    = code.strip()
                    if strippedCode == '':
                        self.promptSymbol   = '>>> '
                        self.write('\n') 
                    elif strippedCode[-1] in (':', '\\') or codeList:
                        codeList.append(code)
                        self.promptSymbol   = '... '
                        self.write('\n')
                    else:
                        self.promptSymbol   = '>>> '
                        self.write('\n')
                        try:
                            ret = app.execute(code)
                        except:
                            traceback.print_exc()
                        if ret != None:
                            self.write(repr(ret)+'\n', 'RETVAL')
    
                finally:
                    return 'break'

            # Experimenting with idlelib's AutoComplete
            #######################################################
            if evt.keycode == 9:
                return self.__autoComplete.autocomplete_event(evt)
            #######################################################

            
    
    def getCursorPos(self, mark=INSERT):
        pos = self.text.index(mark)
        ######################################
        try:        
            r, c    = pos.split('.')
        except ValueError as e:
            print (pos)
            raise e
        ######################################
        return int(r), int(c)        
        
        
class ConsoleWindow(ModelNode):
    strWelcome = '''Good {0}, dear user(s). Welcome to WaveSyn!
WaveSyn is a platform for testing and evaluating waveform synthesis algorithms.
The following modules are imported and all the objects in them can be used directly in the scripting system:
numpy.
Be ware that "print" is a function rather than a statement in the scripting environment.
Have a nice day.
'''
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        app = Application.instance
        root = app.root
        root.title('WaveSyn-Console')
        txtStdOutErr = ConsoleText(root)
        txtStdOutErr.pack(expand=YES, fill=BOTH)
        self.__txtStdOutErr = txtStdOutErr
        tagDefs = kwargs['tagDefs']
        for key in tagDefs:
            self.text.tag_configure(key, **tagDefs[key])        


        nowtime = datetime.now().hour
        if nowtime >= 19:
            greetings = 'evening'
        elif nowtime >= 12:
            greetings = 'afternoon'
        else:
            greetings = 'morning'
        txtStdOutErr.write(self.strWelcome.format(greetings), 'TIP')

        menu    = kwargs['menu']
        makeMenu(root, menu, json=True)
        self.__defaultCursor = self.__txtStdOutErr.text['cursor']
        
    @property
    def promptSymbol(self):
        return self.__txtStdOutErr.promptSymbol
        
    @promptSymbol.setter
    def promptSymbol(self, val):
        self.__txtStdOutErr.promptSymbol    = val
        
    @property
    def defaultCursor(self):
        return self.__defaultCursor
                                                               
    @property
    def text(self):
        return self.__txtStdOutErr.text
                                                        
    def write(self, *args, **kwargs):
        self.__txtStdOutErr.write(*args, **kwargs)
            
    def showPrompt(self):
        'Only used by "clear" method.'
        self.__txtStdOutErr.write('')

    @Scripting.printable    
    def save(self, filename): # for scripting system
        with open(filename, 'w') as f:
            f.write(self.__txtStdOutErr.getText())
            
    def onSaveAs(self):
        printCode   = True
        fileName    = asksaveasfilename(filetypes=[('All types of files', '*.*')])
        if not fileName:
            return
        #self.callMethod('save', filename)
        self.save(fileName)
    
    @Scripting.printable    
    def clear(self):
        self.__txtStdOutErr.clear()
        self.showPrompt()
        
    def onClear(self):
        printCode   = True
        self.clear()

    @Scripting.printable        
    def editScript(self):
        app = Application.instance
            
        fd, filename    = tempfile.mkstemp(suffix='.py', text=True)
        with os.fdopen(fd):
            pass 
            # Close the temp file, consequently the external editor can edit it without limitations.
        try:
            WaveSynThread.start(func=lambda: subprocess.call([app.editorInfo['Path'], filename]))
            with open(filename, 'r') as f:
                code    = f.read()
                self.write(code, 'HISTORY')
                self.write('\n')
                if code:
                    app.execute(code)
        finally:            
            os.remove(filename)
            
    def onEditScript(self):
        printCode   = True
        self.editScript()
        


class WindowDict(NodeDict):
    def __init__(self, nodeName=''):
        NodeDict.__init__(self, nodeName=nodeName)
                
    def __setitem__(self, key, val):
        if not isinstance(val, ModelNode):
            raise TypeError, evalFmt('{self.nodePath} only accepts instance of ToolWindow or of its subclasses.')
        if key != id(val):
            raise ValueError, 'The key should be identical to the ID of the window.'
        NodeDict.__setitem__(self, key, val)
        
    def add(self, node):
        self[id(node)] = node
        return id(node)



class ToolWindow(ModelNode):
    '''Window is build around matplotlib Figure.
'''
    windowName = ''
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
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
    

        
        
class GridGroup(Group):
    def __init__(self, *args, **kwargs):
        self.__topwin   = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
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
        self.__topwin = kwargs['topwin']
        del kwargs['topwin']
        app = Application.instance
       
        Group.__init__(self, *args, **kwargs)
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
        self.__topwin = kwargs['topwin']
        del kwargs['topwin']
        Group.__init__(self, *args, **kwargs)
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


class AlgoSelGroup(Group):
    def __init__(self, *args, **kwargs):
        Group.__init__(self, *args, **kwargs)
        self.__algolist = Combobox(self, value=['ISAA-DIAC'], takefocus=1, stat='readonly', width=12)
        self.__algolist.current(0)
        self.__algolist.pack()
        self.name = 'Algorithms'



class AlgoParamsGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance

        Group.__init__(self, *args, **kwargs)
        self.__algo = None
        self.__MAXROW = 3
        self.__params = {}
        self.balloon = None
        self.name = 'Parameters'

    @property
    def algo(self):
        return self.__algo

    @algo.setter
    def algo(self, algorithm):
        #To do: when algo is reset, the frm should be removed
        frm = Frame(self)
        frm.pack()
        params = algorithm.meta.params
        for idx, name in enumerate(params):
            param = params[name]
            paramitem = ParamItem(frm)
            paramitem.labelText = name
            paramitem.label['width'] = 5
            paramitem.entry['width'] = 8
            if self.balloon:
                self.balloon.bind_widget(paramitem.label, balloonmsg=param.shortdesc)
            if param.type == 'int':
                paramitem.checkFunc = self._app.checkInt
            elif param.type == 'float':
                paramitem.checkFunc = checkFloat
            paramitem.grid(row=idx%self.__MAXROW, column=idx//self.__MAXROW)
            self.__params[param.name] = {'gui':paramitem, 'meta':param}
        self.__algo = algorithm

    def getparams(self):
        params = self.__params
        convert = {'int':int, 'float':float, 'expression':eval, '':lambda x: x}
        return {name: convert[params[name]['meta'].type](params[name]['gui'].entryText) for name in params}

class InitGroup(Group):
    def __init__(self, *args, **kwargs):
        Group.__init__(self, *args, **kwargs)
        self.__initsel = IntVar(0)
        Radiobutton(self, text='Random', value=0, variable=self.__initsel).pack(expand=True, fill=X)
        self.name = 'Initialization'

class GenGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance

        self.__topwin = kwargs['topwin']
        del kwargs['topwin']
        Group.__init__(self, *args, **kwargs)
        self.__num = ParamItem(self)
        self.__num.label.config(text='num')
        self.__num.entryText = '1'
        self.__num.entry.bind('<Return>', lambda event: self.onGenBtnClick())
        self.__num.checkFunc = self._app.checkInt
        self.__num.pack()
        self.__progress = IntVar()
        self.__finishedwav = IntVar()
        progfrm = Frame(self)
        progfrm.pack()
        self.__progbar = Progressbar(progfrm, orient='horizontal', variable=self.__progress, maximum=100)
        self.__progbar.pack(side=LEFT)
        self.__finishedwavbar = Progressbar(progfrm, orient='horizontal', variable=self.__finishedwav, length=70)
        self.__finishedwavbar.pack(side=RIGHT)
        self.__genbtn = Button(self, text='Generate', command=self.onGenBtnClick)
        self.__genbtn.pack(side=LEFT)
        Button(self, text='Stop', command=self.onStopBtnClick).pack(side=RIGHT)
        self.name = 'Generate'
        self.algo = None
        self.getparams = None
        #self.figfrm = None # figfrm: the container of the matplotlib canvas
        self.__stopflag = False

    def onGenBtnClick(self):
        tbicon = self._app.taskbaricon
        self.__stopflag = False
        wavnum = self.__num.getInt()
        progress = [0]
        waveform = [0]
        def exitcheck(k, K, y, y_last):
            progress[0] = int(k / K * 100)
        self.algo.exitcond['func'] = exitcheck
        self.algo.exitcond['interval'] = 1
        params = self.getparams()

        class AlgoThread(threading.Thread):
            def __init__(self, algo, params, waveform, progress):
                self.algo = algo
                self.progress = progress
                threading.Thread.__init__(self)
            def run(self):
                waveform[0] = self.algo(**params)

        self.__finishedwavbar['maximum'] = wavnum
        for cnt in range(wavnum):
            algothread = AlgoThread(self.algo, params, waveform, progress)
            algothread.start()
            while algothread.isAlive():
                self.__progress.set(progress[0])
                tbicon.progress = int((cnt*100+progress[0])/(wavnum*100)*100)
                self.__topwin.update()
                if self.__stopflag:
                    break
## time.sleep(0.1)
            self.__progress.set(0)
            if self.__stopflag:
                break
            self.__topwin.currentFigure.plot_acorr(waveform[0])
            self.__finishedwav.set(cnt+1)
        self.__finishedwav.set(0)
        tbicon.state = guicomponents.TBPF_NOPROGRESS

    def onStopBtnClick(self):
        self.__stopflag = True


def createViewTab(tabpages, topwin):
        # View Tab
    frmView = Frame(tabpages)
    grpGrid = GridGroup(frmView, bd=2, relief=GROOVE, topwin=topwin)
    grpGrid.pack(side=LEFT, fill=Y)
  
    
    grpAxis = AxisGroup(frmView, bd=2, relief=GROOVE, topwin=topwin)
    grpAxis.pack(side=LEFT, fill=Y)
  
    
    grpClear = ClearGroup(frmView, bd=2, relief=GROOVE, topwin=topwin)
    grpClear.pack(side=LEFT, fill=Y)
    
    with topwin.attributeLock:    
        setMultiAttr(topwin,
            grpGrid  = grpGrid,
            grpAxis  = grpAxis,
            grpClear = grpClear  
        )

    
    tabpages.add(frmView, text='View')
        # End View Tab

#import isaa

#class SingleWindow(object):
# def __init__(self, application):
# self.__toplevel = Toplevel()
# self.__toplevel.title(' '.join(('Single-Syn', str(id(self)))))
# self._app = application
# self.__currentFigure = None
# # The toolbar
# tabpages = Notebook(self.__toplevel)
# tabpages.pack(fill=X)
# # Algorithm Tab
# frmAlgo = Frame(tabpages)
# grpAlgoSel = AlgoSelGroup(frmAlgo, bd=2, relief=GROOVE)
# grpAlgoSel.pack(side=LEFT, fill=Y)
# grpParams = AlgoParamsGroup(frmAlgo, bd=2, relief=GROOVE, application=application)
# grpParams.balloon = application.balloon
# grpParams.algo = isaa.diac
# grpParams.pack(side=LEFT, fill=Y)
# grpInit = InitGroup(frmAlgo, bd=2, relief=GROOVE)
# grpInit.pack(side=LEFT, fill=Y)
# grpGen = GenGroup(frmAlgo, bd=2, relief=GROOVE, application=application, topwin=self)
# grpGen.pack(side=LEFT, fill=Y)
# grpGen.getparams = grpParams.getparams
# grpGen.algo = isaa.diac
# tabpages.add(frmAlgo, text='Algorithm')
# # End Algorithm Tab
# create_viewtab(tabpages, application, self)
# # End toolbar
#
# # The Figure
# self.__currentFigure = guitools.FigureFrame(self.__toplevel)
# self.__currentFigure.pack(expand=YES, fill=BOTH)
# # End Figure
#
# @property
# def currentFigure(self):
# return self.__currentFigure
#
# def update(self):
# self.__toplevel.update()
            
            
import pattern2corrmtx

class PatternSolveGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__uiImages = []
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        frm = Frame(self)
        frm.pack(side=TOP)
        
        imageMLbl = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_M_Label.png')
        )
        self.__uiImages.append(imageMLbl)
        Label(frm, image=imageMLbl).pack(side=LEFT)
        
        self.__M = ParamItem(frm)
        self.__M.label.config(text='M')
        self.__M.entryWidth = 6
        self.__M.entryText = 10
        self.__M.entry.bind('<Return>', lambda dumb: self.onSolve())
        self.__M.checkFunc = self._app.checkInt
        self.__M.pack(side=RIGHT)
        
        self._app.balloon.bind_widget(frm, balloonmsg='The number of the array elements.')

        imageSolveBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Solve_Button.png')
        )
        self.__uiImages.append(imageSolveBtn)

        self.__btnSolve = Button(self, image=imageSolveBtn, command=self.onSolve)
        self.__btnSolve.pack(side=TOP)
        self._app.balloon.bind_widget(self.__btnSolve, balloonmsg='Launch the solver to synthesize the correlation matrix.')
        
        frm = Frame(self)
        frm.pack(side=TOP)
        imageDisplayBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Display_Button.png')
        )
        self.__uiImages.append(imageDisplayBtn)
        Label(frm, image=imageDisplayBtn).pack(side=LEFT)
        self.__bDisplay = IntVar(0)
        chkDisplay = Checkbutton(frm, text="Display", variable=self.__bDisplay)
        chkDisplay.pack(side=TOP)
        self._app.balloon.bind_widget(frm, balloonmsg='Display solver output.')
        
        self.name = 'Optimize'
                
    def onSolve(self):
        printCode   = True
        topwin = self.__topwin
        center, width = topwin.grpEdit.beamData
        topwin.figureBook.clear()
        
        topwin.plotIdealPattern(ScriptCode('r_[-90:90.1:0.1]'), center, width)
        topwin.setIdealPattern(ScriptCode('r_[-90:90.1:0.1]'), center, width)
        # Create a new thread for solving the correlation matrix.
        def solveFunc():
            printCode   = True
            topwin.solve(M=self.__M.getInt(), display=self.__bDisplay.get())
        WaveSynThread.start(func=solveFunc)
        # Though method "start" will not return until the solve returns, the GUI will still 
        # responding to user input because Tk.update is called by start repeatedly.
        # While the thread is not alive, the optimization procedure is finished.                        
        topwin.plotCorrMatrixPattern()
        
        
        
        
class PatternEditGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        frm = Frame(self)
        
        self.__center = ParamItem(frm)
        setMultiAttr(self.__center,        
            labelText   = 'center(deg)',        
            entryText   = 0,    
            checkFunc   = self._app.checkInt,
            entryWidth  = 5,    
            labelWidth  = 10
        )                       
        self.__center.pack(side=TOP)        
        self._app.balloon.bind_widget(self.__center, balloonmsg='Specify the beam center here.')
        
        self.__width = ParamItem(frm)
        setMultiAttr(self.__width,
            labelText   = 'width(deg)',
            entryText   = 20,
            checkFunc   = self._app.checkInt,
            entryWidth  = 5,
            labelWidth  = 10
        )
        self.__width.pack(side=TOP)
        self._app.balloon.bind_widget(self.__width, balloonmsg='Specify the beam width here.')
        
        self.__uiImages = []
                
                
        imageAddBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Add_Button.png')
        )
        self.__uiImages.append(imageAddBtn)
        btn = Button(frm, image=imageAddBtn, command=self.onAdd)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Add new beam to the ideal pattern.')
        
        imageDelBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Del_Button.png')
        )
        self.__uiImages.append(imageDelBtn)
        btn = Button(frm, image=imageDelBtn, command=self.onDel)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Remove the selected beam in the listbox.')
        
        imageClrBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Clear_Button.png')
        )
        self.__uiImages.append(imageClrBtn)
        btn = Button(frm, image=imageClrBtn, command=self.onClear)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Clear the listbox of the beam parameters.')
        
        imagePlotBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_Plot_Button.png')
        )
        self.__uiImages.append(imagePlotBtn)
        btn = Button(frm, image=imagePlotBtn, command=self.onPlotIdealPattern)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Plot the ideal pattern.')
        
        frm.pack(side=LEFT, fill=Y)
        
        self.__paramlist = ScrolledList(self)
        self.__paramlist.list.config(height=4, width=10)
        self.__paramlist.pack(side=LEFT)
        self.name = 'Edit Ideal Pattern'
        
        self.optgrp = None
        
    def onAdd(self):
        self.__paramlist.list.insert(END, '{0}, {1}'.format(self.__center.getInt(), self.__width.getInt()))
        
    def onDel(self):
        self.__paramlist.list.delete(ANCHOR)
        
    def onClear(self):
        self.__paramlist.clear()
        
    def onPlotIdealPattern(self):
        printCode   = True
        center, width = self.beamData
        self.__topwin.plotIdealPattern(ScriptCode('r_[-90:90.1:0.1]'), center, width)
        
    @property
    def beamData(self):
        beamParams = self.__paramlist.list.get(0, END)
        if not beamParams:
            # stderr print 'no beam is specified'
            self._app.printError('An error occurred!')
        # msgbox An error has encounted. Please check the Console window for more details.
            self._app.printTip(
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


        
class LoadGroup(Group):
    def __init__(self, *args, **kwargs):
        Group.__init__(self, *args, **kwargs)
        self.name = 'Load Pattern'
        
        
class PatternFileExportGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        
        frm = Frame(self)
        self.__uiImages = []
        imageMatFileBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_SaveMat_Button.png')
        )
        self.__uiImages.append(imageMatFileBtn)
        Button(frm, image=imageMatFileBtn, command=self.onSaveMat).pack(side=TOP)
        Button(frm, text='mat', width=6).pack(side=TOP)
        frm.pack(side=LEFT)
        
        frm = Frame(self)
        imageExcelFileBtn = ImageTk.PhotoImage(
            file=uiImagePath('Pattern_SaveExcel_Button.png')
        )
        self.__uiImages.append(imageExcelFileBtn)
        Button(frm, image=imageExcelFileBtn).pack(side=TOP)
        Button(frm, text='xlsx', width=6).pack(side=TOP)
        frm.pack(side=LEFT)
        
        self.name = 'Corr Matrix'
        
    def onSaveMat(self):
        printCode   = True
        filename = asksaveasfilename(filetypes=[('Matlab mat files', '*.mat')])
        if not filename:
            return
            
        def linkFunc(filename):
            printCode   = True
            clipboard   = Application.instance.clipboard
            clipboard.clear()
            clipboard.append(autoSubs('load $filename'))

        self.__topwin.saveMat(filename)
        tip = [
            {
                'type':'text', 
                'content':autoSubs('''The correlation matrix has been saved in the mat file "$filename" successully.
You can extract the data in Matlab using the following command:''')
            },
            {
                'type':'link', 
                'content':autoSubs('>> load $filename'),
                'command':lambda dumb: linkFunc(filename=filename)
            },
            {
                'type':'text', 
                'content':'''and variable named "R" will appear in your Matlab workspace.
(Click the underlined Matlab command and copy it to the clipboard)'''
            }
        ]
        self._app.printTip(tip)

        
        
        
class PatternFigureExportGroup(Group):
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
'''A Matlab script file has been saved as {filename}.
By running this script, Matlab will literally "re-plot" the curves shown here.'''.format(filename=filename)
        )


        

class PatternWindow(ToolWindow):
    windowName = 'WaveSyn-PatternFitting'
    def __init__(self, *args, **kwargs):
        ToolWindow.__init__(self, *args, **kwargs)
        # The toolbar
        tabpages = Notebook(self._toplevel)
        tabpages.pack(fill=X)
            # Algorithm tab
        frmAlgo = Frame(tabpages)
        grpSolve = PatternSolveGroup(frmAlgo, topwin=self)
        grpSolve.pack(side=LEFT, fill=Y)
        grpEdit = PatternEditGroup(frmAlgo, topwin=self)
        grpEdit.pack(side=LEFT, fill=Y)
        self.__grpEdit = grpEdit
        
        tabpages.add(frmAlgo, text='Algorithm')
            # End Algorithm tab
            
            # View Tab
        createViewTab(tabpages, self)
            # End View tab
        
            # Export tab
        frmExport = Frame(tabpages)
        grpExport = PatternFileExportGroup(frmExport, topwin=self)
        grpExport.pack(side=LEFT, fill=Y)
        grpFigureExport = PatternFigureExportGroup(frmExport, topwin=self)
        grpFigureExport.pack(side=LEFT, fill=Y)
        tabpages.add(frmExport, text='Export')
            # End Export tab
        # End toolbar
        
        self.idealPattern = None
        self.angles = None

        figureBook = FigureBook(self._toplevel, 
            figureMeta=[
                {'name':'Cartesian', 'polar':False},
                {'name':'Polar', 'polar':True}
            ],
            topwin   = self
        )

        figureBook.panedWindow.pack(expand=YES, fill=BOTH)
        figCart = figureBook[0]
        figCart.plotFunction = lambda *args, **kwargs: figCart.plot(*args, **kwargs)
        figPolar    = figureBook[1]
        figPolar.plotFunction = lambda angles, pattern, **kwargs: figPolar.plot(angles/180.*pi, pattern, **kwargs)
        
        self.figureBook = figureBook        
        self.__problem = pattern2corrmtx.Problem()
        self.R = None
        
                
    @property
    def grpEdit(self):
        return self.__grpEdit
    
    @Scripting.printable    
    def setIdealPattern(self, angles, center, width):
        self.angles = angles = r_[-90:90.1:0.1]
        self.idealPattern = pattern2corrmtx.ideal_pattern(angles, center, width)

    @Scripting.printable    
    def plotIdealPattern(self, angles, center, width):
        self.figureBook.plot(angles, pattern2corrmtx.ideal_pattern(angles, center, width),
            curveName='Ideal Pattern', color='b')
    
    @Scripting.printable        
    def plotCorrMatrixPattern(self, R=None):
        if R == None:
            R = self.R
        if R == None:
            pass # To do: raise a error
        self.figureBook.plot(self.angles, pattern2corrmtx.corrmtx2pattern(R, self.angles),
            curveName='Synthesized Pattern', color='g')
            
    @Scripting.printable    
    def solve(self, M, display=False):
        self.__problem.M = M
        self.__problem.angles = self.angles
        self.__problem.idealpattern = self.idealPattern
        self.R = self.__problem.solve(verbose=display)
        
    @Scripting.printable    
    def saveMat(self, filename, varname='R', format='5'):
        savemat(filename, {varname:self.R}, format=format)
                
        
        
if __name__ == '__main__':
    application = Application()
    application.mainloop()
