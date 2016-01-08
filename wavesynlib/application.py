# -*- coding: utf-8 -*-
"""
Created on Fri May 02 15:48:27 2014

@author: Feng-cong Li. xialulee@sina.com
"""
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


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
from Tkinter      import Frame
from tkFileDialog import asksaveasfilename


import matplotlib
matplotlib.use('TkAgg')

from numpy import *


from datetime   import datetime
from inspect    import getsourcefile
import webbrowser
import subprocess
import json
import traceback

# Some console functionalities are implemented by idlelib
##########################
from idlelib.AutoComplete import AutoComplete
import idlelib.AutoCompleteWindow
idlelib.AutoCompleteWindow.KEYPRESS_SEQUENCES = ()
from idlelib.Percolator import Percolator
from idlelib.ColorDelegator import ColorDelegator
##########################

from wavesynlib.guicomponents.tk                 import DirIndicator, TaskbarIcon, ScrolledText, ValueChecker, PilImageFrame
from wavesynlib.interfaces.clipboard.modelnode   import Clipboard
from wavesynlib.interfaces.timer.tk              import TkTimer
from wavesynlib.interfaces.editor.externaleditor import EditorDict, EditorNode
from wavesynlib.stdstream                        import StreamManager
#from wavesynlib.cuda                             import Worker as CUDAWorker
from wavesynlib.languagecenter.utils             import autoSubs, evalFmt, setMultiAttr
from wavesynlib.languagecenter.designpatterns    import Singleton        
from wavesynlib.languagecenter.wavesynscript     import Scripting, ModelNode
from wavesynlib.languagecenter.modelnode         import LangCenterNode
from wavesynlib.languagecenter                   import templates


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



class Application(ModelNode): # Create an ABC for root node to help wavesynscript.Scripting determine whether the node is root. 
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
        super(Application, self).__init__(nodeName=Scripting.rootName, isRoot=True)
        Scripting.nameSpace['locals'][Scripting.rootName] = self
        Scripting.nameSpace['globals'] = globals()
        Scripting.rootNode = self
        self.homePage = 'https://github.com/xialulee/WaveSyn'
        
        filePath    = getsourcefile(type(self))
        dirPath     = os.path.split(filePath)[0]
        
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
        
        from wavesynlib.interfaces.xmlrpc.server import CommandSlot
        

        valueChecker    = ValueChecker(root)        
        
        with self.attributeLock:
            setMultiAttr(self,
                # UI elements
                root                = root,        
                balloon             = Tix.Balloon(root),
                tbicon              = TaskbarIcon(root),
                # End UI elements
                
                mainThreadId        = mainThreadId,
                execThreadLock      = threading.RLock(),
                xmlrpcCommandSlot   = CommandSlot(),

                langCenter          = LangCenterNode(),
            
                # Validation Functions
                valueChecker        = valueChecker,
                checkInt            = valueChecker.checkInt,
                checkFloat          = valueChecker.checkFloat,
                checkPositiveFloat  = valueChecker.checkPositiveFloat,
                # End Validation Functions
                
                filePath    = filePath,
                dirPath     = dirPath,
                                
                streamManager   =StreamManager(),                
                
                configFileName  = configFileName
                
#                cudaWorker      = CUDAWorker()
            )        
        
        

        
        from wavesynlib.basewindow import WindowDict                                  
        self.windows    = WindowDict() # Instance of ModelNode can be locked automatically.
        self.editors    = EditorDict()

        class EditorObserver(object): # use SimpleObserver instead
            def __init__(self, wavesyn):
                self.wavesyn    = wavesyn

            def update(self, editor):
                wavesyn = self.wavesyn                
                code    = editor.code
                if not code:
                    return
                wavesyn.streamManager.write('WaveSyn: executing code from editor {0} listed as follows:\n'.format(id(editor)), 'TIP')
                wavesyn.streamManager.write(code, 'HISTORY')
                wavesyn.streamManager.write('\n')
                wavesyn.execute(code)

        self.editors.manager.addObserver(EditorObserver(self))

        with self.attributeLock:
            self.monitorTimer    = self.createTimer(interval=100, active=False)
        # Make wavesyn.editors.manager check wavesyn.editors every 100ms
        self.monitorTimer.addObserver(self.editors.manager) 
        self.monitorTimer.addObserver(self.streamManager)
        
        frm = Frame(root)
        frm.pack(side=TOP, fill=X)                

        self.console = ConsoleWindow(menu=consoleMenu, tagDefs=tagDefs)
        self.streamManager.addObserver(self.console.streamObserver) #!
             
        self.clipboard = Clipboard()
        self.scripting = Scripting(self)
        self.noTip = False

        self.monitorTimer.active    = True
        
    def createWindow(self, moduleName, className):
        '''Create a tool window.'''
        mod = __import__(autoSubs('wavesynlib.toolwindows.$moduleName'), globals(), locals(), [className], -1)
        return self.windows.add(node=getattr(mod, className)())

    def launchEditor(self, editorPath=None):
        if editorPath is None:
            editorPath  = self.editorInfo['Path']
        editorID    = self.editors.add(EditorNode(editorPath=editorPath))
        self.editors[editorID].launch()
        return editorID
        
    def createTimer(self, interval=100, active=False):
        return TkTimer(self.root, interval, active)
                     
        
    def printAndEval(self, expr):
        with self.execThreadLock:
            self.streamManager.write(expr+'\n', 'HISTORY')
            ret = eval(expr, Scripting.nameSpace['globals'], Scripting.nameSpace['locals'])
            if ret is not None:
                self.streamManager.write(str(ret)+'\n', 'RETVAL')
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
                encoding            = sys.getfilesystemencoding()
                print(stdout.decode(encoding, 'ignore'))
                print(stderr.decode(encoding, 'ignore'), file=sys.stderr)                
                return
            try:
                ret = self.eval(code)
            except SyntaxError:
                exec code in Scripting.nameSpace['globals'], Scripting.nameSpace['locals']
            return ret
            
                    
            
    def printTip(self, contents):
        if self.noTip:
            return
        streamManager = self.streamManager
        streamManager.write('WaveSyn: ', 'TIP')
        if type(contents) in (str, unicode):
            streamManager.write(contents+'\n', 'TIP')
            return
        for item in contents:
            if item['type'] == 'text':
                streamManager.write(''.join((item['content'],'\n')), 'TIP')
            elif item['type'] == 'link':
                command = item['command']
                tagName = 'link' + str(id(command))
                streamManager.write(item['content'], tagName)
                text    = self.console.text
                r, c = text.index(END).split('.')
                text.tag_config(tagName, underline=1, foreground='blue')
                text.tag_bind(tagName, '<Button-1>', command) # href implementation shold be added.
                text.tag_bind(tagName, '<Enter>', lambda dumb: text.config(cursor='hand2'))
                text.tag_bind(tagName, '<Leave>', lambda dumb: text.config(cursor=self.console.defaultCursor))
                streamManager.write('\n')
            elif item['type'] == 'pil_image':
                streamManager.write('The QR code of the text stored by clipboard is shown above.', 'TIP')
                text    = self.console.text                
                text.insert(END, '\n')
                pilFrame    = PilImageFrame(text, pilImage=item['image'])
                text.window_create(END, window=pilFrame)
                text.insert(END, '\n')
                streamManager.write('\n')
                
                                            
                
    def printError(self, text):
        self.streamManager.write(text+'\n', 'STDERR')
        
            
    def notifyWinQuit(self, win):
        self.printTip(evalFmt('{win.nodePath} is closed, and its ID becomes defunct for scripting system hereafter'))
        self.windows.pop(id(win))
        
        
    def openHomePage(self):
        '''Open the home page of wavesyn.'''
        webbrowser.open(self.homePage, new=1, autoraise=True)
             
                    
    def mainloop(self):
        return self.root.mainloop()
        
    @classmethod
    def doEvents(cls):
        cls.instance.root.update()
        
    def startXMLRPCServer(self, addr='localhost', port=8000):
        from wavesynlib.interfaces.xmlrpc.server    import startXMLRPCServer
        startXMLRPCServer(addr, port)        
        def checkCommand():
            command = self.xmlrpcCommandSlot.command
            paramsToStr  = Scripting.paramsToStr # used by evalFmt
            try:
                if command is not None:
                    nodePath, methodName, args, kwargs  = command
                    ret, err    = None, None
                    try:
                        ret = self.printAndEval(evalFmt('{nodePath}.{methodName}({paramsToStr(*args, **kwargs)})')) # paramToStr used here
                    except Exception as error:
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
                

        
# How to implement a thread safe console?
# see: http://effbot.org/zone/tkinter-threads.htm              
class ConsoleText(ScrolledText):
    class StreamObserver(object):
        def __init__(self, consoleText):
            self.__consoleText  = consoleText
        def update(self, streamType, content):
            self.__consoleText.write(streamType, content)
    
    def __init__(self, *args, **kwargs):
        super(ConsoleText, self).__init__(*args, **kwargs)
        # The shared queue of the PRODUCER-CONSUMER model.
        self.__queue    = Queue.Queue()
        self.text['wrap']   = 'word'
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
        self.promptSymbol = '>>> '    
        
        
    def updateContent(self, tag, content):
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

    def onKeyPress(self, evt, codeList=[]):       
        # Experimenting with idlelib's AutoComplete
        ##############################################################
        keysym = evt.keysym        
        if self.__autoComplete.autocompletewindow and \
                self.__autoComplete.autocompletewindow.is_active():
            if self.__autoComplete.autocompletewindow.keypress_event(evt) == 'break':
                return 'break'
            else:
                if keysym == 'Tab':
                    return 'break'
            
        if evt.keysym == 'Tab':
            return self.__autoComplete.autocomplete_event(evt)
        ##############################################################
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
                        self.updateContent(tag='', content='\n')
                        return 'break'
                    if strippedCode == '':
                        code    = '\n'.join(codeList)
                        del codeList[:]
                    strippedCode    = code.strip()
                    if strippedCode == '':
                        self.promptSymbol   = '>>> '
                        self.updateContent(tag='', content='\n') 
                    elif strippedCode[-1] in (':', '\\') or codeList:
                        codeList.append(code)
                        self.promptSymbol   = '... '
                        self.updateContent(tag='', content='\n')
                    else:
                        self.promptSymbol   = '>>> '
                        self.updateContent(tag='', content='\n')
                        try:
                            ret = app.execute(code)
                        except:
                            traceback.print_exc()
                        if ret is not None:
                            self.updateContent(tag='RETVAL', content=repr(ret)+'\n')
    
                finally:
                    self.text.mark_set(INSERT, END)
                    self.text.see(END)
                    return 'break'            
                
    def getCursorPos(self, mark=INSERT): 
        return (int(i) for i in self.text.index(mark).split('.'))               
        
        
class ConsoleWindow(ModelNode):
    
    class StreamObserver(object):
        def __init__(self, console):
            self.__console  = console
            
        def update(self, streamType, content):
            self.__console.consoleText.updateContent(tag=streamType, content=content)

    def __init__(self, *args, **kwargs):
        super(ConsoleWindow, self).__init__(*args, **kwargs)
        app = Application.instance
        root = app.root
        root.title('WaveSyn-Console')

        dirIndicator = DirIndicator()
        dirIndicator.pack(fill=X)
        
        txtStdOutErr = ConsoleText(root)
        txtStdOutErr.pack(expand=YES, fill=BOTH)
        self.__txtStdOutErr = txtStdOutErr
        tagDefs = kwargs['tagDefs']
        for key in tagDefs:
            self.text.tag_configure(key, **tagDefs[key])        

        nowtime = datetime.now().hour
        if nowtime >= 19:
            time    = 'evening'
        elif nowtime >= 12:
            time    = 'afternoon'
        else:
            time    = 'morning'
        app.streamManager.write(templates.greeting.format(time), 'TIP')
        menu    = kwargs['menu']
        makeMenu(root, menu, json=True)
        self.__defaultCursor = self.__txtStdOutErr.text['cursor']
        self.streamObserver = self.StreamObserver(self)
        
        
    @property
    def consoleText(self):
        return self.__txtStdOutErr        
        
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
                                                                    
    @Scripting.printable    
    def save(self, filename): # for scripting system
        with open(filename, 'w') as f:
            f.write(self.__txtStdOutErr.getText())
            
    def onSaveAs(self):
        printCode   = True # For macro recording
        fileName    = asksaveasfilename(filetypes=[('All types of files', '*.*')])
        if not fileName:
            return
        self.save(fileName)
    
    @Scripting.printable    
    def clear(self):
        self.__txtStdOutErr.clear()
        print('', sep='', end='')
        
    def onClear(self):
        printCode   = True # For macro recording
        self.clear()

    def windowAttributes(self, *args, **kwargs):
        return Application.instance.root.wm_attributes(*args, **kwargs)        
        
        
        
     
    

def mainloop():
    Application().mainloop()
        
        