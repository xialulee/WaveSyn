#-*- coding:utf-8 -*

from Tkinter import *
import sys
##import threading
##import Queue

##root    = None


TBPF_NOPROGRESS     = 0
TBPF_INDETERMINATE  = 1
TBPF_NORMAL         = 2
TBPF_ERROR          = 4
TBPF_PAUSED         = 8
import platform
win7plus    = False
if platform.system() == 'Windows':
    winver  = platform.version().split('.')    
    if int(winver[0])>=6 and int(winver[1])>=1:
        win7plus    = True

if win7plus:
    from taskbarmanager import ITaskbarList4, GUID_CTaskbarList, TBPFLAG
    from comtypes import CoCreateInstance
    import ctypes as ct
    GetParent   = ct.windll.user32.GetParent

    class TaskbarIcon(object):
        def __init__(self, root):
            self.__tbm  = CoCreateInstance(GUID_CTaskbarList, interface=ITaskbarList4)
            self.__root = root

        @property
        def progress(self):
            '''Not implemented'''
            pass

        @progress.setter
        def progress(self, value):
            self.__tbm.SetProgressValue(GetParent(self.__root.winfo_id()), int(value), 100)

        @property
        def state(self):
            '''Not Implemented'''
            pass

        @state.setter
        def state(self, state):
            self.__tbm.SetProgressState(GetParent(self.__root.winfo_id()), state)
else:
    class TaskbarIcon(object):
        def __init__(self, root):
            pass



class LabeledEntry(Frame, object):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.__entry    = Entry(self)
        self.__label    = Label(self)
        if 'labelfirst' in kwargs and kwargs['labelfirst']:
            self.__label.pack(side=LEFT)
            self.__entry.pack(side=LEFT)
        else:
            self.__entry.pack(side=LEFT)
            self.__label.pack(side=LEFT)
        if 'labeltext' in kwargs:
            self.__label['text']    =kwargs['labeltext']

    @property
    def entry(self):
        return self.__entry

    @property
    def label(self):
        return self.__label
        
        
        
        
class ParamItem(Frame, object):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.__label    = Label(self)
        self.__label.pack(side=LEFT)
        self.__entry    = Entry(self)
        self.__entry.pack(fill=X, expand=YES)
        self.__checkFunc    = None

    @property
    def label(self):
        return self.__label

    @property
    def entry(self):
        return self.__entry

    @property
    def labelText(self):
        return self.__label['text']

    @labelText.setter
    def labelText(self, text):
        self.__label['text']    = text

    @property
    def entryText(self):
        return self.__entry.get()

    @entryText.setter
    def entryText(self, text):
        self.__entry.delete(0, END)
        self.__entry.insert(0, text)

    def getInt(self):
        return int(self.__entry.get())

    def getFloat(self):
        return float(self.__entry.get())

    @property
    def labelWidth(self):
        return self.__label['width']

    @labelWidth.setter
    def labelWidth(self, width):
        self.__label['width']   = width

    @property
    def entryWidth(self):
        return self.__entry['width']

    @entryWidth.setter
    def entryWidth(self, width):
        self.__entry['width']   = width

    @property
    def checkFunc(self):
        return self.__checkFunc

    @checkFunc.setter
    def checkFunc(self, func):
        self.__checkFunc    = func
        self.__entry.config(validate='key', validatecommand=func)
                



class TextWinHotkey(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.bind('<Control-Key-a>', lambda event: self.selectAll())

    def selectAll(self):
        self.tag_add(SEL, '1.0', 'end-1c')
        self.see(INSERT)
        self.focus()
        return 'break'


class ScrolledText(Frame):
    '''This class is based on Programming Python 3rd Edition P517'''
    def __init__(self, parent=None, text='', file=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.makeWidgets()
        self.setText(text, file)
        


    def makeWidgets(self):
        sbar    = Scrollbar(self)
        text    = TextWinHotkey(self, relief=SUNKEN)
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        text.pack(side=LEFT, expand=YES, fill=BOTH)
        self.text   = text

    def setText(self, text='', file=None):
        if file:
            with open(file, 'r') as f:
                text    = f.read().decode('gbk')
        self.text.delete('1.0', END)
        self.text.insert('1.0', text)
        self.text.mark_set(INSERT, '1.0')
        self.text.focus()
        
    def clear(self):
        self.setText()

    def appendText(self, text=''):
        self.text.insert(END, text)

    def getText(self):
        return self.text.get('1.0', END+'-1c')

    def selectAll(self):
        return self.text.selectAll()

    def findText(self, target):
        if target:
            where   = self.text.search(target, INSERT, END)
            if where:
                if __DEBUG__:
                    print 'Ctrl+F: searching for {0}'.format(target)
                    print 'position', where
                pastit  = where + ('+%dc' % len(target))
                self.text.tag_remove(SEL, '1.0', END)
                self.text.tag_add(SEL, where, pastit)
                self.text.mark_set(INSERT, pastit)
                self.text.see(INSERT)
                self.text.focus()
                return True
            else:
                return False
        else:
            return False




class StreamChain(object):
    def __init__(self):
        self.__streamlist   = []

    def __iadd__(self, stream):
        self.__streamlist.append(stream)
        return self

    def remove(self, stream):
        while True:
            try:
                del self.__streamlist[self.__streamlist.index(stream)]
            except ValueError:
                break

    def write(self, content):
        for stream in self.__streamlist:
            stream.write(content)

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

    def write(self, content, tag=None):
        self.text.insert(END, content, tag)
        self.text.see(END)
        self.text.update()
        
    def onKeyPress(self, evt):        
        if evt.keycode not in range(16, 19) and evt.keycode not in range(33, 41):
            r, c    = self.getCursorPos()
            start3  = self.text.get('{r}.0'.format(r=r), '{r}.3'.format(r=r))
            if start3 != '>>>':
                return 'break'
            if c < 4:
                return 'break'
            
    
    def getCursorPos(self):
        pos = self.text.index(INSERT)
        r, c    = pos.split('.')
        return int(r), int(c)

class ScrolledList(Frame, object):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        sbar = Scrollbar(self)
        list = Listbox(self)
        sbar.config(command=list.yview)
        list.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        list.pack(side=LEFT, expand=YES, fill=BOTH)
        list.bind('<<ListboxSelect>>', self.onListboxClick)
        
        self.__listClick = None
        self.__list = list
        self.__sbar = sbar
        

    @property
    def list(self):
        return self.__list

    @property
    def sbar(self):
        return self.__sbar

    def insert(self, *args, **kwargs):
        return self.__list.insert(*args, **kwargs)
        
    def itemConfig(self, *args, **kwargs):
        return self.__list.itemconfig(*args, **kwargs)

    def clear(self):
        self.__list.delete(0, END)
        
    def listConfig(self, **kwargs):
        self.__list.config(**kwargs)
        
    @property
    def listClick(self):
        return self.__listClick

    @listClick.setter
    def listClick(self, val):
        if not callable(val):
            raise TypeError
        self.__listClick = val

    def onListboxClick(self, event):
        index = self.__list.curselection()
        if len(index) > 0:
            index = index[0]
            label = self.__list.get(index)
            if self.listClick:
                self.listClick(index, label)

class Group(Frame, object):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        if 'relief' not in kwargs:
            self['relief']  = GROOVE
        if 'bd' not in kwargs:
            self['bd']      = 2
        self.__lblName  = Label(self)
        self.__lblName.pack(side=BOTTOM)        

    @property
    def name(self):
        return self.__lblName['text']

    @name.setter
    def name(self, name):
        self.__lblName['text']  = name
        
        
        
