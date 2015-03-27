# -*- coding: utf-8 -*-
"""
Created on Fri May 02 15:48:27 2014

@author: Feng-cong Li. xialulee@sina.com
"""
from __future__ import division
from __future__ import print_function


def dependenciesForMyprogram():
    '''This function is used to solve the bugs of py2exe'''
    from scipy.sparse.csgraph   import _validation
    from scipy.special          import _ufuncs_cxx

import thread
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
from Tkinter import Frame
from tkFileDialog import asksaveasfilename


import matplotlib
matplotlib.use('TkAgg')

from numpy import *


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

from objectmodel import ModelNode
from guicomponents import StreamChain, TaskbarIcon, ScrolledText, ValueChecker, TkTimer
from common import setMultiAttr, autoSubs, evalFmt, Singleton
from interfaces.editor.externaleditor  import EditorDict, EditorNode

from stdstream  import StreamManager
##########################Experimenting with multiprocessing###############################
#import multiprocessing as mp
###########################################################################################

        
# Scripting Sub-System
class ScriptCode(object):
    def __init__(self, code):
        self.code = code
        
class Scripting(ModelNode):
    _xmlrpcexport_  = []    
    
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
        theThread  = WaveSynThread.Thread(func)
        theThread.start()
        while theThread.isAlive():
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
    
    _xmlrpcexport_  = [
        'createWindow',
        'openHomePage'
    ]
    ''' '''
    def __init__(self):
        # The instance of this class is the root of the model tree. Thus isRoot is set to True
        ModelNode.__init__(self, nodeName=Scripting.rootName, isRoot=True)
        Scripting.nameSpace['locals'][Scripting.rootName] = self
        Scripting.nameSpace['globals'] = globals()
        self.homePage = 'https://github.com/xialulee/WaveSyn'
        
        filePath    = getsourcefile(type(self))
        dirPath     = os.path.split(filePath)[0]
        sys.path.append(dirPath)
        #sys.path.append(os.path.join(dirPath, '..'))        
        
        # load config file
        configFileName  = os.path.join(dirPath, 'config.json')
        with open(configFileName) as f:
            config  = json.load(f)
        consoleMenu = config['ConsoleMenu']
        self.editorInfo   = config['EditorInfo']
        self.lockAttribute('editorInfo')
        self.promptSymbols  = config['PromptSymbols']

        tagDefs = config['TagDefs']
        # End load config file

        root = Tix.Tk()
        mainThreadId    = thread.get_ident()
        
        from interfaces.xmlrpc.server import CommandSlot
        

        valueChecker    = ValueChecker(root)        
        
        with self.attributeLock:
            setMultiAttr(self,
                # UI elements
                root = root,        
                balloon = Tix.Balloon(root),
                tbicon = TaskbarIcon(root),
                # End UI elements
                
                mainThreadId        = mainThreadId,
                execThreadLock      = threading.RLock(),
                xmlrpcCommandSlot   = CommandSlot(),
            
                # Validation Functions
                valueChecker        = valueChecker,
                checkInt            = valueChecker.checkInt,
                checkFloat          = valueChecker.checkFloat,
                checkPositiveFloat  = valueChecker.checkPositiveFloat,
                # End Validation Functions
                
                filePath    = filePath,
                dirPath     = dirPath,
                
                monitorTimer    = TkTimer(widget=root, interval=100, active=False),
                streamManager   =StreamManager(),                
                
                configFileName  = configFileName
            )        
        
        #self.monitorTimer.addObserver(self.streamManager)

        
        from basewindow import WindowDict                                  
        self.windows    = WindowDict() # Instance of ModelNode can be locked automatically.
        self.editors    = EditorDict()

        class EditorObserver(object):
            def __init__(self, wavesyn):
                self.wavesyn    = wavesyn

            def update(self, editor):
                wavesyn = self.wavesyn                
                code    = editor.code
                if not code:
                    return
                wavesyn.console.write('WaveSyn: executing code from editor {0} listed as follows:\n'.format(id(editor)), tag='TIP')
                wavesyn.console.write(code, tag='HISTORY')
                wavesyn.console.write('\n')
                wavesyn.execute(code)

        self.editors.manager.addObserver(EditorObserver(self))

        # Make wavesyn.editors.manager check wavesyn.editors every 100ms
        self.monitorTimer.addObserver(self.editors.manager) 
        
        frm = Frame(root)
        frm.pack(side=TOP, fill=X)                

        self.console = ConsoleWindow(menu=consoleMenu, tagDefs=tagDefs)
        self.streamManager.addObserver(self.console.streamObserver)
             
        self.clipboard = Clipboard()
        self.scripting = Scripting(self)
        self.noTip = False

        self.monitorTimer.active    = True
        
    def createWindow(self, moduleName, className):
        '''Create a tool window.'''
        mod = __import__(autoSubs('toolwindows.$moduleName'), globals(), locals(), [className], -1)
        return self.windows.add(node=getattr(mod, className)())

    def launchEditor(self, editorPath=None):
        if editorPath is None:
            editorPath  = self.editorInfo['Path']
        editorID    = self.editors.add(EditorNode(editorPath=editorPath))
        self.editors[editorID].launch()
        return editorID


#
#    @callAndPrintDoc        
#    def newPatternWin(self, printDoc=False):
#        '''This method creates a new PatternFitting window.
#Its return value is the ID of the new window.
#You can access the created window using its ID in the scripting system.
#A PatternWindow can synthesize a correlation matrix of which the beam pattern fits the given ideal pattern best.'''        
#        return self.windows.add(node=PatternWindow())
        
    def createTimer(self, interval=100, active=False):
        return TkTimer(interval, active)
                     
        
    def printAndEval(self, expr):
        with self.execThreadLock:
            self.console.write(expr+'\n', 'HISTORY')
            ret = eval(expr, Scripting.nameSpace['globals'], Scripting.nameSpace['locals'])
            if ret != None:
                self.console.write(str(ret)+'\n', 'RETVAL')
            return ret
                              
    def eval(self, expr):
        with self.execThreadLock:
            ret = eval(expr, Scripting.nameSpace['globals'], Scripting.nameSpace['locals'])
            Scripting.nameSpace['locals']['_']  = ret
            return ret
        
    def execute(self, code):
        with self.execThreadLock:
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
        if type(contents) in (str, unicode):
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
        '''Open the home page of wavesyn.'''
        webbrowser.open(self.homePage, new=1, autoraise=True)
             
                    
    def mainloop(self):
        return self.root.mainloop()
        
    def startXMLRPCServer(self, addr='localhost', port=8000):
        from interfaces.xmlrpc.server    import startXMLRPCServer
        startXMLRPCServer(addr, port)        
        def checkCommand():
            command = self.xmlrpcCommandSlot.command
            paramsToStr  = Scripting.paramsToStr
            try:
                if command is not None:
                    nodePath, methodName, args, kwargs  = command
                    ret, err    = None, None
                    try:
                        ret = self.printAndEval(evalFmt('{nodePath}.{methodName}({paramsToStr(*args, **kwargs)})'))
                    except Exception, error:
                        err = error
                    ret = 0 if ret is None else ret
                    self.xmlrpcCommandSlot.returnVal    = (ret, err)
            finally:
                # Make sure that at any circumstance the checkCommand will be called repeatedly.
                self.root.after(100, self.xmlrpcCheckCommand)
        self.xmlrpcCheckCommand = checkCommand
        self.root.after(100, checkCommand)

        
        
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
        
# How to implement a thread safe console?
# see: http://effbot.org/zone/tkinter-threads.htm
#class ConsoleText(ScrolledText):
#    def __init__(self, *args, **kwargs):
#        ScrolledText.__init__(self, *args, **kwargs)
#        # The shared queue of the PRODUCER-CONSUMER model.
#        self.__queue    = Queue.Queue()
#        self.text.tag_configure('STDOUT',   foreground='black')
#        self.text.tag_configure('STDERR',   foreground='red')
#        self.text.tag_configure('TIP', foreground='forestgreen')
#        self.text.tag_configure('HISTORY',   foreground='purple')
#        self.text.tag_configure('RETVAL',    foreground='orange')
#        
#        self.text.bind('<KeyPress>', self.onKeyPress)
#
#        
#        # Experimenting with idlelib.AutoComplete
#        #############################################################
#        self.indentwidth    = 4
#        self.tabwidth       = 4
#        self.context_use_ps1    = '>>> '
#        self.__autoComplete = AutoComplete(self)        
#        #############################################################
#                
#        # Syntax highlight is implemented by idlelib
#        #############################################################                
#        self.percolator = Percolator(self.text)
#        self.colorDelegator = ColorDelegator()
#        self.percolator.insertfilter(self.colorDelegator)   
#        #############################################################
#                
#        class StdOut:
#            def write(obj, content):
#                self.write(content, 'STDOUT')
#
#        class StdErr:
#            def write(obj, content):
#                self.write(content, 'STDERR')
#                
#        self.__stdout   = StreamChain()
#        self.__stdout   += sys.stdout
#        self.__stdout   += StdOut()
#
#        self.__stderr   = StreamChain()
#        self.__stderr   += sys.stderr
#        self.__stderr   += StdErr()
#
#        sys.stdout      = self.__stdout
#        sys.stderr      = self.__stderr
#        
#        self.promptSymbol = '>>> '
#        
#        self.updateContent()
#        
#    def write(self, content, tag=''):
#        # The write method does not insert text into the console window.
#        # The actural "write" operation is carried out by "updateContent".
#        # "write" is called by PRODUCER.
#        self.__queue.put((tag, content))
#        if thread.get_ident() == Application.instance.mainThreadId:
#            # If the current thread is not the main thread, the Tk update() should not be called,
#            # or the vital objects of the application may be modified by more than one threads simultaneously.
#            try:            
#                self.update()
#            except TclError:
#                pass
#
#    def updateContent(self):
#        # updateContent is called by CONSUMER.
#        try:
#            while True:
#                tag, content    = self.__queue.get_nowait()
#                r, c    = self.getCursorPos(END)
#                start   = 'end-5c'
#                stop    = 'end-1c'
#                if self.text.get(start, stop) == '>>> ' or self.text.get(start, stop) == '... ':
#                    self.text.delete(start, stop)
#        
#                # Record the position of the END before inserting anything.
#                start    = self.text.index(END)
#        
#                self.text.insert(END, content, tag)
#        
#                # Remove unnecessary highlighting
#                for tag in self.colorDelegator.tagdefs:
#                    self.text.tag_remove(tag, start, "end")
#                    
#        
#                self.text.insert(END, self.promptSymbol)
#                
#                
#                # Remove unnecessary highlighting
#                self.text.tag_remove("TODO", "1.0", END)
#                self.text.tag_add("SYNC", "1.0", END)                                
#                self.text.see(END)
#                
#
#        except Queue.Empty:
#            pass
#        finally:
#            self.after(100, self.updateContent)
#        
#
#    def onKeyPress(self, evt, codeList=[]):   
#        #print (evt.keycode)        
#        if evt.keycode not in range(16, 19) and evt.keycode not in range(33, 41):
#            r, c    = self.getCursorPos()
#            prompt  = self.text.get(autoSubs('$r.0'), autoSubs('$r.4'))
#            if prompt != '>>> ' and prompt != '... ':
#                return 'break'
#            if evt.keycode==8 and c <= 4:
#                return 'break'
#            if c < 4:
#                return 'break'
#            rend, cend  = self.getCursorPos('end-1c')
#            if r < rend:
#                return 'break'                
#            if evt.keycode == 13:
#                app = Application.instance
#                code    = self.text.get(autoSubs('$r.4'), autoSubs('$r.end'))
#                try:
#                    strippedCode     = code.strip()
#                    if strippedCode and strippedCode[0] == '!':
#                        # Execute a system command
#                        app.execute(code)
#                        self.promptSymbol   = '>>> '
#                        self.write('\n')
#                        return 'break'
#                    if strippedCode == '':
#                        code    = '\n'.join(codeList)
#                        del codeList[:]
#                    strippedCode    = code.strip()
#                    if strippedCode == '':
#                        self.promptSymbol   = '>>> '
#                        self.write('\n') 
#                    elif strippedCode[-1] in (':', '\\') or codeList:
#                        codeList.append(code)
#                        self.promptSymbol   = '... '
#                        self.write('\n')
#                    else:
#                        self.promptSymbol   = '>>> '
#                        self.write('\n')
#                        try:
#                            ret = app.execute(code)
#                        except:
#                            traceback.print_exc()
#                        if ret != None:
#                            self.write(repr(ret)+'\n', 'RETVAL')
#    
#                finally:
#                    self.text.mark_set(INSERT, END)
#                    self.text.see(END)
#                    return 'break'
#
#            # Experimenting with idlelib's AutoComplete
#            #######################################################
#            if evt.keycode == 9:
#                return self.__autoComplete.autocomplete_event(evt)
#            #######################################################
#                
#    def getCursorPos(self, mark=INSERT): 
#        return (int(i) for i in self.text.index(mark).split('.'))       
        
class ConsoleText(ScrolledText):
    class StreamObserver(object):
        def __init__(self, consoleText):
            self.__consoleText  = consoleText
        def update(self, streamType, content):
            self.__consoleText.write(streamType, content)
    
    def __init__(self, *args, **kwargs):
        ScrolledText.__init__(self, *args, **kwargs)
        # The shared queue of the PRODUCER-CONSUMER model.
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
        # "write" is called by PRODUCER.
        self.__queue.put((tag, content))
        if thread.get_ident() == Application.instance.mainThreadId:
            # If the current thread is not the main thread, the Tk update() should not be called,
            # or the vital objects of the application may be modified by more than one threads simultaneously.
            try:            
                self.update()
            except TclError:
                pass

    def updateContent(self):
        # updateContent is called by CONSUMER.
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
                    self.text.mark_set(INSERT, END)
                    self.text.see(END)
                    return 'break'

            # Experimenting with idlelib's AutoComplete
            #######################################################
            if evt.keycode == 9:
                return self.__autoComplete.autocomplete_event(evt)
            #######################################################
                
    def getCursorPos(self, mark=INSERT): 
        return (int(i) for i in self.text.index(mark).split('.'))               
        
        
class ConsoleWindow(ModelNode):
    strWelcome = '''Good {0}, dear user(s). Welcome to WaveSyn!
WaveSyn is a platform for testing and evaluating waveform synthesis algorithms.
The following modules are imported and all the objects in them can be used directly in the scripting system:
numpy.
Be ware that "print" is a function rather than a statement in the scripting environment.
Have a nice day.
'''
    class StreamObserver(object):
        def __init__(self, console):
            self.__console  = console
            
        def update(self, streamType, content):
            self.__console.write(tag=streamType, content=content)

    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        app = Application.instance
        ####################################
        timer   = app.createTimer(100, False)
        self.__timer    = timer        
        ####################################
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
        self.streamObserver = self.StreamObserver(self)
        
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

    def windowAttributes(self, *args, **kwargs):
        return Application.instance.root.wm_attributes(*args, **kwargs)        
        
        
        
     
    

def mainloop():
    Application().mainloop()
        
        
#if __name__ == '__main__':
#    mainloop()

