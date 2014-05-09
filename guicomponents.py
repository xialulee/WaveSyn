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
        self.__checkfunc    = None

    @property
    def label(self):
        return self.__label

    @property
    def entry(self):
        return self.__entry

    @property
    def labeltext(self):
        return self.__label['text']

    @labeltext.setter
    def labeltext(self, text):
        self.__label['text']    = text

    @property
    def entrytext(self):
        return self.__entry.get()

    @entrytext.setter
    def entrytext(self, text):
        self.__entry.delete(0, END)
        self.__entry.insert(0, text)

    def getint(self):
        return int(self.__entry.get())

    def getfloat(self):
        return float(self.__entry.get())

    @property
    def labelwidth(self):
        return self.__label['width']

    @labelwidth.setter
    def labelwidth(self, width):
        self.__label['width']   = width

    @property
    def entrywidth(self):
        return self.__entry['width']

    @entrywidth.setter
    def entrywidth(self, width):
        self.__entry['width']   = width

    @property
    def checkfunc(self):
        return self.__checkfunc

    @checkfunc.setter
    def checkfunc(self, func):
        self.__checkfunc    = func
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
        self.makewidgets()
        self.settext(text, file)
        


    def makewidgets(self):
        sbar    = Scrollbar(self)
        text    = TextWinHotkey(self, relief=SUNKEN)
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        text.pack(side=LEFT, expand=YES, fill=BOTH)
        self.text   = text

    def settext(self, text='', file=None):
        if file:
            with open(file, 'r') as f:
                text    = f.read().decode('gbk')
        self.text.delete('1.0', END)
        self.text.insert('1.0', text)
        self.text.mark_set(INSERT, '1.0')
        self.text.focus()
        
    def clear(self):
        self.settext()

    def appendtext(self, text=''):
        self.text.insert(END, text)

    def gettext(self):
        return self.text.get('1.0', END+'-1c')

    def selectAll(self):
        return self.text.selectAll()

    def findtext(self, target):
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
        #self.__app  = kwargs.pop('application')
        ScrolledText.__init__(self, *args, **kwargs)
        self.text.tag_configure('STDOUT',   foreground='black')
        self.text.tag_configure('STDERR',   foreground='red')
        self.text.tag_configure('TIP', foreground='forestgreen')
        self.text.tag_configure('HISTORY',   foreground='purple')
        self.text.tag_configure('RETVAL',    foreground='orange')

        
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
        #self.__app.root.update()
        # set view
        self.text.see(END)
        self.text.update()



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
        
        
        
