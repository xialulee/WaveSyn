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

import os
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

from functools import partial
from datetime import datetime
import webbrowser
import subprocess
import tempfile
import json
import traceback

##########################
from idlelib import AutoComplete
##########################

from guicomponents import Group, StreamChain, TaskbarIcon, ParamItem, ScrolledList, ScrolledText
import guicomponents



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


class ObjectWithLock(object):    
    '''This is a mixin class.'''
    @property
    def lock(self):
        if not hasattr(self, '_lock'):
            self._lock  = threading.Lock()
        return self._lock
    
    
# Object Model Sub-System
# In fact, the functionality of this sub-system is serving the scripting system.
class ModelNode(object):
    '''This class defines the node of the model tree of this application.
The model tree is illustrated as follows:
wavesyn
-console
-clipboard
-window[id]
    -instance of PatternFitting
        -figureBook
    -instance of SingleSyn
        -figureBook
    -instance of MIMOSyn
        -figureBook
'''
    def __init__(self, nodeName='', isRoot=False, **kwargs):
        if '_attributeLock' not in self.__dict__:
            object.__setattr__(self, '_attributeLock', set())
        self.parentNode = None
        self.__isRoot = isRoot
        self.nodeName = nodeName
        
    def lockAttribute(self, attrName):
        self._attributeLock.add(attrName)
        
    @property
    def isRoot(self):
        return self.__isRoot
        
    def __setattr__(self, key, val):
        if '_attributeLock' not in self.__dict__:
            # This circumstance happens when __setattr__ called before __init__ being called.
            object.__setattr__(self, '_attributeLock', set())
        if key in self._attributeLock:
            raise AttributeError, 'Attribute "{0}" is not changable.'.format(key)
        if isinstance(val, ModelNode) and not val.isRoot and val.parentNode==None:
            val.nodeName = val.nodeName if val.nodeName else key
            object.__setattr__(val, 'parentNode', self)
            val.lockAttribute('parentNode')
        object.__setattr__(self, key, val)
        
    @property
    def nodePath(self):
        if self.isRoot:
            return self.nodeName
        if isinstance(self.parentNode, NodeHub):
            return '{parentPath}[{id}]'.format(parentPath=self.parentNode.nodePath, id=id(self))
        else:
            return '.'.join((self.parentNode.nodePath, self.nodeName))
        
    '''This class is a mixin class, which helps the system to evaluate and print command on the console.
A mixin class does not have a __init__ method.'''
    def callMethod(self, name, *args, **kwargs):
        strParams = Scripting.paramsToStr(*args, **kwargs)
        Application.instance.printAndEval(self.nodePath+'.{0}({1})'.format(name, strParams))
        
    def callMethodAndPrintDoc(self, name, *args, **kwargs):
        self.callMethod(name, *args, **kwargs)
        doc = Application.instance.eval(self.nodePath+'.{0}.__doc__'.format(name))
        Application.instance.printTip(doc)
# End Object Model
        
        
        
class NodeHub(ModelNode, dict):
    def __init__(self, nodeName=''):
        dict.__init__(self)
        ModelNode.__init__(self, nodeName=nodeName)
                
    def __setitem__(self, key, val):
        if not isinstance(val, ModelNode):
            raise TypeError, '{nodePath} only accepts instance of ToolWindow and its subclass.'.format(nodePath=self.nodePath)
        if key != id(val):
            raise ValueError, 'The key should be identical to the ID of the window.'
        object.__setattr__(val, 'parentNode', self)
        val.lockAttribute('parentNode')
        dict.__setitem__(self, key, val)
        
    def add(self, node):
        self[id(node)] = node
        return id(node)
        
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
            #print (type(param))
            if isinstance(param, str) or isinstance(param, unicode):
                #print ('"{0}"'.format(param))
                return '"{0}"'.format(param)
            elif isinstance(param, ScriptCode):
                return param.code
            else:
                return str(param)
                
        strArgs = ', '.join([paramToStr(arg) for arg in args]) if args else ''
        strKwargs = ', '.join(['{0}={1}'.format(key, paramToStr(kwargs[key])) for key in kwargs]) \
            if kwargs else ''
            
        if strArgs and strKwargs:
            params = ', '.join((strArgs, strKwargs))
        else:
            params = strArgs if strArgs else strKwargs
        return params
        
    def __init__(self, rootNode):
        ModelNode.__init__(self)
        self.__rootNode = rootNode

        # self.__codeList = []
        
#    def execute(self, code):
#        app = Application.instance
#        if isinstance(code, ScriptCode):
#            code = code.code
#        if not code.strip():
#            code = '\n'.join(self.__codeList)
#            self.__codeList = []
#        strippedCode    = code.strip()
#        if strippedCode == '':
#            app.console.promptSymbol    = '>>> '
#            app.console.write('\n')
#            return True
#        if strippedCode[-1] == ':' or self.__codeList:
#            self.__codeList.append(code)
#            app.console.promptSymbol    = '... '
#            app.console.write('\n')
#            return False
#        app.console.promptSymbol    = '>>> '
#        app.console.write('\n')
#        try:
#            ret = eval(code, self.nameSpace['globals'], self.nameSpace['locals'])
#            if ret!=None: 
#                Application.instance.console.write(repr(ret), 'RETVAL')
#                print()
#        except SyntaxError:
#            #exec code in self.nameSpace['globals'], self.nameSpace['locals']
#            exec code in self.nameSpace['globals'], self.nameSpace['locals']
#
#
#        return True
            

    def executeFile(self, filename):
        execfile(filename, **self.nameSpace) #?
        
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
                    cmd = topItem['Command'] # topItem['Command'] is a callable object
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


class Singleton(type):
    '''This class is a meta class, which helps to create singleton class.'''
    def __call__(self, *args, **kwargs):
        if hasattr(self, 'instance'):
            return self.instance
        else:
            self.instance = object.__new__(self)
            # In this circumstance, the __init__ should be called explicitly.
            self.__init__(self.instance, *args, **kwargs)
            return self.instance

class Application(ModelNode):
    '''This class is the root of the model tree.
In the scripting system, it is named as "wavesyn" (case sensitive).
It also manages the whole application and provide services for other components.
For other nodes on the model tree, the instance of Application can be accessed by Application.instance,
since the instance of Application is the first node created on the model tree.'''
    __metaclass__ = Singleton
    ''' '''
    def __init__(self):
        # The instance of this class is the root of the model tree. Thus isRoot is set to True
        ModelNode.__init__(self, nodeName=Scripting.rootName, isRoot=True)
        Scripting.nameSpace['locals'][Scripting.rootName] = self
        Scripting.nameSpace['globals'] = globals()
        self.homePage = 'https://github.com/xialulee/WaveSyn'
        
        # load config file
        with open('config.json') as f:
            config  = json.load(f)
        consoleMenu = config['ConsoleMenu']
        self.__editorInfo   = config['EditorInfo']
        self.promptSymbols  = config['PromptSymbols']
        # End load config file

        root = Tix.Tk()
        self.__root = root
        
        self.__balloon = Tix.Balloon(root)
        self.__tbicon = TaskbarIcon(root)
        
        # Validation Functions
        self.__checkInt = (root.register(partial(checkValue, func=int)),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.__checkFloat = (root.register(partial(checkValue, func=float)),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.__checkPositiveFloat = (root.register(checkPositiveFloat),
                   '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        # End Validation Functions
               
        self.window = NodeHub()
        
        frm = Frame(root)
        frm.pack(side=TOP, fill=X)
                  
        self.console = ConsoleWindow(menu=consoleMenu)
        self.clipboard = Clipboard()
        self.scripting = Scripting(self)
        self.noTip = False

    def newSingleWin(self, printDoc=False):
# newwin = SingleWindow(self)
# self.window[id(newwin)] = newwin
# return id(newwin)
        print('Not Implemented.', file=sys.stderr)
        
    def newMIMOWin(self, printDoc=False):
        print('Not Implemented.', file=sys.stderr)

    @callAndPrintDoc        
    def newPatternWin(self, printDoc=False):
        '''This method creates a new PatternFitting window.
Its return value is the ID of the new window.
You can access the created window using its ID in the scripting system.
A PatternWindow can synthesize a correlation matrix of which the beam pattern fits the given ideal pattern best.'''        
        return self.window.add(node=PatternWindow())

             
    @property
    def root(self):
        return self.__root
                
    @property
    def taskbaricon(self):
        return self.__tbicon
        
    @property
    def balloon(self):
        return self.__balloon
        
    @property
    def editorInfo(self):
        return self.__editorInfo
        
    # The validation functions for entry widgets
    @property
    def checkInt(self):
        return self.__checkInt
    
    @property
    def checkFloat(self):
        return self.__checkFloat
        
    @property
    def checkPositiveFloat(self):
        return self.__checkPositiveFloat
    # End
        
        
    def printAndEval(self, expr):
        self.console.write(expr+'\n', 'HISTORY')
        ret = eval(expr, Scripting.nameSpace['globals'], Scripting.nameSpace['locals'])
        if ret != None:
            self.console.write(str(ret)+'\n', 'RETVAL')
                              
    def eval(self, expr):
        return eval(expr, Scripting.nameSpace['globals'], Scripting.nameSpace['locals'])
        
    def execute(self, code):
        ret = None
        try:
            ret = self.eval(code)
        except SyntaxError:
            exec code in Scripting.nameSpace['globals'], Scripting.nameSpace['locals']
        return ret
        
            
    def printTip(self, contents):
        if self.noTip:
            return
        self.console.write('WaveSyn: ', 'TIP')
        if type(contents)==str:
            self.console.write(contents+'\n', 'TIP')
            return
        for item in contents:
            if item['type'] == 'text':
                self.console.write(''.join((item['content'],'\n')), 'TIP')
            elif item['type'] == 'link':
                command = item['command']
                tagName = 'link' + str(id(command))
                self.console.write(item['content'], tagName)
                r, c = self.console.text.index(END).split('.')
                self.console.text.tag_config(tagName, underline=1, foreground='blue')
                self.console.text.tag_bind(tagName, '<Button-1>', command) # href implementation
                self.console.text.tag_bind(tagName, '<Enter>', lambda dumb: self.console.text.config(cursor='hand2'))
                self.console.text.tag_bind(tagName, '<Leave>', lambda dumb: self.console.text.config(cursor=self.console.defaultCursor))
                self.console.write('\n')
                
                                            
                
    def printError(self, text):
        self.console.write(text+'\n', 'STDERR')
        
            
    def notifyWinQuit(self, win):
        self.printTip('{0} is closed, and its ID becomes defunct for scripting system hereafter.'\
            .format(win.nodePath))
        self.window.pop(id(win))
        
        
    def openHomePage(self):
        webbrowser.open(self.homePage, new=1, autoraise=True)
             
                    
    def mainloop(self):
        return self.__root.mainloop()
        
        

class Clipboard(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
       
    def clear(self):
        Application.instance.root.clipboard_clear()
    
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


  

  
  

class DataFigure(object):
    def __init__(self, master, figsize=(5,4), dpi=100, polar=False):
        self.__fig = Figure(figsize, dpi)
        canvas = FigureCanvasTkAgg(self.__fig, master=master)
        canvas.show()
        canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=YES)
        self.__canvas = canvas
        toolbar = NavigationToolbar2TkAgg(canvas, master)
        toolbar.update()
        toolbar.pack()
        self.__lineObjects = []
        self.__axes = self.__fig.add_subplot(111, polar=polar)
        self.__polar = polar
        self.plotFunction = None
        
    @property
    def figure(self):
        return self.__fig
        
    @property
    def axes(self):
        return self.__axes
        
    @property
    def polar(self):
        return self.__polar
        
    @property
    def lineObjects(self):
        return self.__lineObjects
        
    def plot(self, *args, **kwargs):
        lineObject = self.__axes.plot(*args, **kwargs)
        self.__lineObjects.append(lineObject)
        self.update()
        self.update_axispanel()
        

        
    def update(self):
        self.__canvas.show()

    def update_axispanel(self):
        pass
        #Temprorily disabled
# if self.axispanel:
# ap = self.axispanel
# ap.xlim = self.__axes.get_xlim()
# ap.ylim = self.__axes.get_ylim()
#
# attr_func = {
# 'major_xtick': self.__axes.xaxis.get_major_locator,
# 'major_ytick': self.__axes.yaxis.get_major_locator,
# 'minor_xtick': self.__axes.xaxis.get_minor_locator,
# 'minor_ytick': self.__axes.yaxis.get_minor_locator
# }
# for attr in attr_func:
# tick = attr_func[attr]()()
# if len(tick) >= 2:
# tick = tick[1] - tick[0]
# setattr(ap, attr, tick)
# def plot_acorr(self, s, db=True, unif=True):
# color_map = {
# 'c': 'cyan',
# 'm': 'magenta',
# 'y': 'yellow',
# 'k': 'black',
# 'r': 'red',
# 'g': 'green',
# 'b': 'blue'
# }
# ac = abs(convolve(s, conj(s[::-1])))
# if unif:
# ac /= max(ac)
# if db:
# ac = 20*log10(ac)
# N = len(s)
# lineobj = self.__axes.plot(r_[(-N+1):N], ac)[0]
# ######################################################
# #print pyplot.getp(lineobj, 'color')
# ######################################################
# self.__meta_of_lines.append(LineMeta(s, 'acorr', ac, lineobj))
# pos = len(self.__meta_of_lines) - 1
# self.__slist.list.insert(pos, 'acorr of s{0}'.format(pos))
# line_color = pyplot.getp(lineobj, 'color')
# self.__slist.list.itemconfig(pos, fg=color_map[line_color], bg='gray')
# self.update()
# self.update_axispanel()


    def clear(self):
        self.__axes.clear()
        self.__lineObjects = []
        #self.__list.clear()
        self.update()
# if self.gridpanel:
# self.gridpanel.major = 0
# self.gridpanel.minor = 0

# def remove_sel_line(self):
# sel = self.__slist.list.curselection()
# if len(sel) > 0:
# sel = int(sel[0])
# linemeta = self.__meta_of_lines[sel]
# linemeta.lineobj.remove()
# self.__slist.list.delete(ANCHOR)
# del self.__meta_of_lines[sel]
# self.update()
            
    def deleteLine(self, idx):
        lineObject = self.__lineObjects[idx]
        lineObject.remove()
        del self.__lineObjects[idx]

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
        


class FigureBook(PanedWindow, ModelNode): 
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self)
        figureMeta = kwargs.pop('figureMeta')
        kwargs['orient'] = HORIZONTAL
        PanedWindow.__init__(self, *args, **kwargs)

        self['sashwidth'] = 4
        self['sashrelief'] = GROOVE
        self['bg'] = 'forestgreen'
        
        self.__figures = []
        
        tabpages = Notebook(self)
        for meta in figureMeta:
            frm = Frame(tabpages)
            fig = DataFigure(frm, polar=meta['polar'])
            tabpages.add(frm, text=meta['name'])
            self.__figures.append(fig)
            
        self.add(tabpages, stretch='always')
        
        self.__list = ScrolledList(self, relief=GROOVE)
        self.__list.listConfig(width=20)
        self.__list.listClick = self.onListClick
        self.add(self.__list, stretch='never')
        
    @property
    def figures(self):
        return self.__figures
        
    def plot(self, *args, **kwargs):
        try:
            curveName = kwargs.pop('curveName')
        except KeyError:
            curveName = 'curve'
        for fig in self.__figures:
            fig.plotFunction(*args, **kwargs)
        self.__list.insert(END, curveName)
        if 'color' in kwargs:
            self.__list.itemConfig(END, fg=colorMap[kwargs['color']])
            
    def clear(self):
        for fig in self.__figures:
            fig.clear()
        self.__list.clear()
        
        
    def onListClick(self, index, label):
        index = int(index)

        for figure in self.__figures:
            for line in figure.lineObjects:
                pyplot.setp(line, linewidth=1)
            pyplot.setp(figure.lineObjects[index], linewidth=2)
            figure.update()
            
    def exportMatlabScript(self, filename):
        with open(filename, 'w') as file:
            pass
            for figure in self.__figures:
                print('%Generated by WaveSyn.',
                      'figure;', sep = '\n',
                      file=file)
                for line in figure.lineObjects:
                    params = {}
                    for name in ('xdata', 'ydata', 'color'):
                        params[name] = pyplot.getp(line[0], name)
                    params['func'] = 'polar' if figure.polar else 'plot'
                    params['xdata'] = ','.join((str(i) for i in params['xdata']))
                    params['ydata'] = ','.join((str(i) for i in params['ydata']))
                    print("{func}([{xdata}], [{ydata}], '{color}');hold on".format(**params), file=file)
                
        
                


class ConsoleText(ScrolledText):
    '''see http://effbot.org/zone/tkinter-threads.htm'''
    def __init__(self, *args, **kwargs):
        ScrolledText.__init__(self, *args, **kwargs)
        self.text.tag_configure('STDOUT',   foreground='black')
        self.text.tag_configure('STDERR',   foreground='red')
        self.text.tag_configure('TIP', foreground='forestgreen')
        self.text.tag_configure('HISTORY',   foreground='purple')
        self.text.tag_configure('RETVAL',    foreground='orange')
        
        self.text.bind('<KeyPress>', self.onKeyPress)

        
        #############################################################
        self.indentwidth    = 4
        self.tabwidth       = 4
        self.context_use_ps1    = '>>> '
        self.__autoComplete = AutoComplete.AutoComplete(self)        
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
        

    def write(self, content, tag=None):
        r, c    = self.getCursorPos(END)
        start   = 'end-5c'
        stop    = 'end-1c'
        if self.text.get(start, stop) == '>>> ' or self.text.get(start, stop) == '... ':
            self.text.delete(start, stop)
        self.text.insert(END, content, tag)
        self.text.insert(END, self.promptSymbol)
        self.text.see(END)
        self.text.update()
        

    def onKeyPress(self, evt, codeList=[]):   
        #print (evt.keycode)        
        if evt.keycode not in range(16, 19) and evt.keycode not in range(33, 41):
            r, c    = self.getCursorPos()
            prompt  = self.text.get('{r}.0'.format(r=r), '{r}.4'.format(r=r))
            if prompt != '>>> ' and prompt != '... ':
                return 'break'
            if evt.keycode==8 and c <= 4:
                return 'break'
            if c < 4:
                return 'break'
            if evt.keycode == 13:
                rend, cend  = self.getCursorPos('end-1c')
                if r < rend:
                    return 'break'
                app = Application.instance
                code    = self.text.get('{r}.4'.format(r=r), '{r}.end'.format(r=r))
                try:
                    strippedCode     = code.strip()
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

            #######################################################
            if evt.keycode == 9:
                return self.__autoComplete.autocomplete_event(evt)
            #######################################################

            
    
    def getCursorPos(self, mark=INSERT):
        pos = self.text.index(mark)
        r, c    = pos.split('.')
        return int(r), int(c)        
        
        
class ConsoleWindow(ObjectWithLock, ModelNode):
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

        nowtime = datetime.now().hour
        if nowtime >= 19:
            greetings = 'evening'
        elif nowtime >= 12:
            greetings = 'afternoon'
        else:
            greetings = 'morning'
        txtStdOutErr.write(self.strWelcome.format(greetings), 'TIP')
        self.__txtStdOutErr = txtStdOutErr
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
        with self.lock:
            self.__txtStdOutErr.write(*args, **kwargs)
        
    def save(self, filename): # for scripting system
        with open(filename, 'w') as f:
            f.write(self.__txtStdOutErr.getText())
            
    def onSaveAs(self):
        filename    = asksaveasfilename(filetypes=[('All types of files', '*.*')])
        if not filename:
            return
        self.callMethod('save', filename)
        
    def clear(self):
        self.__txtStdOutErr.clear()
        self.__txtStdOutErr.write('') # By calling write('') the prompt symbol will be printed.
        
    def onClear(self):
        self.callMethod('clear')
        
    def editScript(self):
        app = Application.instance
        class EditorThread(threading.Thread):
            def __init__(self, filename):
                self.__filename = filename
                threading.Thread.__init__(self)
            def run(self):
                subprocess.call([app.editorInfo['Path'], self.__filename]) 
            
        fd, filename    = tempfile.mkstemp(suffix='.py', text=True)
        with os.fdopen(fd):
            pass # Close the temp file, and the external editor can edit it freely.
        try:
            editorThread    = EditorThread(filename)
            editorThread.start()
            while editorThread.isAlive():
                app.root.update()
            with open(filename, 'r') as f:
                code    = f.read()
                self.write(code, 'HISTORY')
                self.write('\n')
                if code:
                    app.scripting.execute(code)
        finally:            
            os.remove(filename)
            
    def onEditScript(self):
        self.callMethod('editScript')
        

class ToolWindow(ModelNode):
    '''Window is build around matplotlib Figure.
'''
    windowName = ''
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        self._toplevel = Toplevel()
        self._toplevel.title('{0} id={1}'.format(self.windowName, id(self)))
        self._toplevel.protocol('WM_DELETE_WINDOW', lambda: self.callMethod('close'))
        
    def close(self):
        Application.instance.notifyWinQuit(self)
        self._toplevel.destroy() # For Toplevel objects, use destroy rather than quit.
    

        
        
class GridGroup(Group):
    def __init__(self, *args, **kwargs):
        self.__topwin = kwargs['topwin']
        del kwargs['topwin']
        Group.__init__(self, *args, **kwargs)
        major = IntVar(0)
        minor = IntVar(0)
        self.__major = major
        self.__minor = minor
        

        def setgrid():
            currentFigure = self.__topwin.currentFigure
            currentFigure.axes.grid(major.get(), 'major')
            currentFigure.axes.grid(minor.get(), 'minor')
            currentFigure.update()


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

            for idx, name in enumerate(('major', 'minor')):
                for key in ret[idx]:
                    value = ret[idx][key][1].get()
                    if value:
                        self.__topwin.currentFigure.axes.grid(None, name, **{key: value})
            major.set(1)
            minor.set(1)
            self.__topwin.currentFigure.update()
                                    
        Checkbutton(self, text='Grid Major', variable=major, command=setgrid).pack(fill=X)
        Checkbutton(self, text='Grid Minor', variable=minor, command=setgrid).pack(fill=X)
        Button(self, text='Property', command=onPropertyClick).pack()
        self.name = 'Grid'



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
        application = Application.instance
       
        Group.__init__(self, *args, **kwargs)
        self.__params = [StringVar() for i in range(8)]
        paramfrm =Frame(self)
        paramfrm.pack()
        names = ['xmin', 'xmax', 'ymin', 'ymax', 'major xtick', 'major ytick', 'minor xtick', 'minor ytick']
        for c in range(4):
            for r in range(2):
                temp = ParamItem(paramfrm)
                temp.checkFunc = application.checkFloat
                temp.labelText = names[c*2+r]
                temp.labelWidth = 5 if c*2+r < 4 else 10
                temp.entryWidth = 5
                temp.entry.config(textvariable=self.__params[c*2+r])
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

    @property
    def major_xtick(self):
        return float(self.__params[4].get())

    @major_xtick.setter
    def major_xtick(self, value):
        self.__params[4].set(str(value))

    @property
    def major_ytick(self):
        return float(self.__params[5].get())

    @major_ytick.setter
    def major_ytick(self, value):
        self.__params[5].set(str(value))

    @property
    def minor_xtick(self):
        return float(self.__params[6].get())

    @minor_xtick.setter
    def minor_xtick(self, value):
        self.__params[6].set(str(value))

    @property
    def minor_ytick(self):
        return float(self.__params[7].get())

    @minor_ytick.setter
    def minor_ytick(self, value):
        self.__params[7].set(str(value))

    def onConfirmClick(self):
        aparams = map(lambda v: float(v.get()), self.__params)
        self.__topwin.currentFigure.axis(aparams[:4])
        self.__topwin.currentFigure.axes.xaxis.set_major_locator(MultipleLocator(int(aparams[4])))
        self.__topwin.currentFigure.axes.yaxis.set_major_locator(MultipleLocator(int(aparams[5])))
        self.__topwin.currentFigure.axes.xaxis.set_minor_locator(MultipleLocator(int(aparams[6])))
        self.__topwin.currentFigure.axes.yaxis.set_minor_locator(MultipleLocator(int(aparams[7])))
        self.__topwin.currentFigure.update()

    def onAutoClick(self):
        self.__topwin.currentFigure.axes.autoscale()
        self.__topwin.currentFigure.update()
        self.__topwin.currentFigure.update_axispanel()


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
        self.__topwin.figureBook.clear()

    def onDelSel(self):
        self.__topwin.figureBook.remove_sel_line()

    def onDelUnSel(self):
        self.__topwin.figureBook.remove_unsel_lines()


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


def create_viewtab(tabpages, application, topwin):
        # View Tab
    frmView = Frame(tabpages)
    grpGrid = GridGroup(frmView, bd=2, relief=GROOVE, topwin=topwin)
    grpGrid.pack(side=LEFT, fill=Y)
    grpAxis = AxisGroup(frmView, bd=2, relief=GROOVE, topwin=topwin)
    grpAxis.pack(side=LEFT, fill=Y)
    grpClear = ClearGroup(frmView, bd=2, relief=GROOVE, topwin=topwin)
    grpClear.pack(side=LEFT, fill=Y)
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
        
        imageMLbl = ImageTk.PhotoImage(file='Pattern_M_Label.png', master=frm)
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

        imageSolveBtn = ImageTk.PhotoImage(file='Pattern_Solve_Button.png', master=self)
        self.__uiImages.append(imageSolveBtn)

        self.__btnSolve = Button(self, image=imageSolveBtn, command=self.onSolve)
        self.__btnSolve.pack(side=TOP)
        self._app.balloon.bind_widget(self.__btnSolve, balloonmsg='Launch the solver to synthesize the correlation matrix.')
        
        frm = Frame(self)
        frm.pack(side=TOP)
        imageDisplayBtn = ImageTk.PhotoImage(file='Pattern_Display_Button.png')
        self.__uiImages.append(imageDisplayBtn)
        Label(frm, image=imageDisplayBtn).pack(side=LEFT)
        self.__bDisplay = IntVar(0)
        chkDisplay = Checkbutton(frm, text="Display", variable=self.__bDisplay)
        chkDisplay.pack(side=TOP)
        self._app.balloon.bind_widget(frm, balloonmsg='Display solver output.')
        
        self.name = 'Optimize'
                
    def onSolve(self):
        topwin = self.__topwin
        center, width = topwin.grpEdit.beamData
        topwin.figureBook.callMethod('clear')
        callMethod = topwin.callMethod

        callMethod('plotIdealPattern', ScriptCode('r_[-90:90.1:0.1]'), center, width)
        callMethod('setIdealPattern', ScriptCode('r_[-90:90.1:0.1]'), center, width)
        callMethod('solve', M=self.__M.getInt(), display=self.__bDisplay.get())
        callMethod('plotCorrMatrixPattern')
        
        
        
        
class PatternEditGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        frm = Frame(self)
        self.__center = ParamItem(frm)
        self.__center.label.config(text='center(deg)')
        self.__center.entryText = 0
        self.__center.checkFunc = self._app.checkInt
        self.__center.entryWidth = 5
        self.__center.labelWidth = 10
        self.__center.pack(side=TOP)
        self._app.balloon.bind_widget(self.__center, balloonmsg='Specify the beam center here.')
        
        self.__width = ParamItem(frm)
        self.__width.label.config(text='width(deg)')
        self.__width.entryText = 20
        self.__width.checkFunc = self._app.checkInt
        self.__width.entryWidth = 5
        self.__width.labelWidth = 10
        self.__width.pack(side=TOP)
        self._app.balloon.bind_widget(self.__width, balloonmsg='Specify the beam width here.')
        
        self.__uiImages = []
                
                
        imageAddBtn = ImageTk.PhotoImage(file='Pattern_Add_Button.png', master=frm)
        self.__uiImages.append(imageAddBtn)
        btn = Button(frm, image=imageAddBtn, command=self.onAdd)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Add new beam to the ideal pattern.')
        
        imageDelBtn = ImageTk.PhotoImage(file='Pattern_Del_Button.png', master=frm)
        self.__uiImages.append(imageDelBtn)
        btn = Button(frm, image=imageDelBtn, command=self.onDel)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Remove the selected beam in the listbox.')
        
        imageClrBtn = ImageTk.PhotoImage(file='Pattern_Clear_Button.png', master=frm)
        self.__uiImages.append(imageClrBtn)
        btn = Button(frm, image=imageClrBtn, command=self.onClear)
        btn.pack(side=LEFT)
        self._app.balloon.bind_widget(btn, balloonmsg='Clear the listbox of the beam parameters.')
        
        imagePlotBtn = ImageTk.PhotoImage(file='Pattern_Plot_Button.png', master=frm)
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
        center, width = self.beamData
        self.__topwin.callMethod('plotIdealPattern', ScriptCode('r_[-90:90.1:0.1]'), center, width)
        
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
        imageMatFileBtn = ImageTk.PhotoImage(file='Pattern_SaveMat_Button.png', master=frm)
        self.__uiImages.append(imageMatFileBtn)
        Button(frm, image=imageMatFileBtn, command=self.onSaveMat).pack(side=TOP)
        Button(frm, text='mat', width=6).pack(side=TOP)
        frm.pack(side=LEFT)
        
        frm = Frame(self)
        imageExcelFileBtn = ImageTk.PhotoImage(file='Pattern_SaveExcel_Button.png', master=frm)
        self.__uiImages.append(imageExcelFileBtn)
        Button(frm, image=imageExcelFileBtn).pack(side=TOP)
        Button(frm, text='xlsx', width=6).pack(side=TOP)
        frm.pack(side=LEFT)
        
        self.name = 'Corr Matrix'
        
    def onSaveMat(self):
        filename = asksaveasfilename(filetypes=[('Matlab mat files', '*.mat')])
        if not filename:
            return

        self.__topwin.callMethod('saveMat', filename)
        tip = [
            {'type':'text', 'content':'''The correlation matrix has been saved in the mat file "{filename}" successully.
You can extract the data in Matlab using the following command:'''.format(filename=filename)},
            {'type':'link', 'content':'>> load {filename}'.format(filename=filename),
                 'command':lambda dumb: (
                     Application.instance.clipboard.callMethod('clear'),
                     Application.instance.clipboard.callMethod(
                         'append',
                         'load {filename}'.format(filename=filename)
                     )
                  )
            },
            {'type':'text', 'content':'''and variable named "R" will appear in your Matlab workspace.
(Click the underlined Matlab command and copy it to the clipboard)'''}
        ]
        self._app.printTip(tip)

        
        
        
class PatternFigureExportGroup(Group):
    def __init__(self, *args, **kwargs):
        self._app = Application.instance
        self.__topwin = kwargs.pop('topwin')
        Group.__init__(self, *args, **kwargs)
        self.__uiImages = []
        imageFigureExportBtn = ImageTk.PhotoImage(file='Pattern_ExportFigure_Button.png')
        self.__uiImages.append(imageFigureExportBtn)
        frm = Frame(self); frm.pack(side=LEFT)
        Button(frm, image=imageFigureExportBtn, command=self.onExportMatlabScript).pack(side=TOP)
        Button(frm, text='Script', command=self.onExportMatlabScript, width=6).pack(side=TOP)
        
        self.name = 'Figure'
        

    def onExportMatlabScript(self):
        filename = asksaveasfilename(filetypes=[('Matlab script files', '*.m')])
        if not filename:
            return
        self.__topwin.figureBook.callMethod('exportMatlabScript', filename)
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
        #grpEdit.optgrp = grpGen
        grpEdit.pack(side=LEFT, fill=Y)
        self.__grpEdit = grpEdit
        
        tabpages.add(frmAlgo, text='Algorithm')
            # End Algorithm tab
            
            # View Tab
        create_viewtab(tabpages, application, self)
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

        figureBook = FigureBook(self._toplevel, \
            figureMeta=[
                {'name':'Cartesian', 'polar':False},
                {'name':'Polar', 'polar':True}
            ]
        )
        figureBook.pack(expand=YES, fill=BOTH)
        figCart = figureBook.figures[0]
        figCart.plotFunction = lambda *args, **kwargs: figCart.plot(*args, **kwargs)
        figPolar = figureBook.figures[1]
        figPolar.plotFunction = lambda angles, pattern, **kwargs: figPolar.plot(angles/180.*pi, pattern, **kwargs)
        
        self.figureBook = figureBook        
        self.__problem = pattern2corrmtx.Problem()
        self.R = None
        
        
    @property
    def grpEdit(self):
        return self.__grpEdit
        
    def setIdealPattern(self, angles, center, width):
        self.angles = angles = r_[-90:90.1:0.1]
        self.idealPattern = pattern2corrmtx.ideal_pattern(angles, center, width)

        
    def plotIdealPattern(self, angles, center, width):
        self.figureBook.plot(angles, pattern2corrmtx.ideal_pattern(angles, center, width),
            curveName='Ideal Pattern', color='b')
            
    def plotCorrMatrixPattern(self, R=None):
        if R == None:
            R = self.R
        if R == None:
            pass # To do: raise a error
        self.figureBook.plot(self.angles, pattern2corrmtx.corrmtx2pattern(R, self.angles),
            curveName='Synthesized Pattern', color='g')
            
        
    def solve(self, M, display=False):
        self.__problem.M = M
        self.__problem.angles = self.angles
        self.__problem.idealpattern = self.idealPattern
        self.R = self.__problem.solve(verbose=display)
        
        
    def saveMat(self, filename, varname='R', format='5'):
        savemat(filename, {varname:self.R}, format=format)
                
        
        
if __name__ == '__main__':
    application = Application()
    application.mainloop()
