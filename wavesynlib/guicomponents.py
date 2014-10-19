#-*- coding:utf-8 -*

from Tkinter    import *
from ttk        import *
from Tkinter    import Frame

from functools  import partial

from common     import MethodDelegator



__DEBUG__ = False


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


def checkValue(d, i, P, s, S, v, V, W, func):
    try:
        func(P)
        return True
    except ValueError:
        return True if P=='' or P=='-' else False
        
def checkPositiveFloat(d, i, P, s, S, v, V, W):
    try:
        assert float(P) > 0
        return True
    except (ValueError, AssertionError):
        return True if P=='' else False

class ValueChecker(object):
    def __init__(self, root):
        self.__root = root
        self.checkInt   = (root.register(partial(checkValue, func=int)),
                    '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.checkFloat = (root.register(partial(checkValue, func=float)),
                    '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.checkPositiveFloat = (root.register(checkPositiveFloat),
                       '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')



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
        
        
class LabeledScale(Frame, object):
    def __init__(self, *args, **kwargs):
        from_   = kwargs.pop('from_')
        to      = kwargs.pop('to')
        name    = kwargs.pop('name')
        formatter   = kwargs.pop('formatter', str)
        self.__formatter    = formatter
        Frame.__init__(self, *args, **kwargs)
        Label(self, text=name).pack(side=LEFT)
        self.__scale    = Scale(self, from_=from_, to=to, command=self.onChange)
        self.__scale.pack(side=LEFT, fill=X)
        lblVal  = Label(self)
        lblVal.pack(side=LEFT)
        self.__labelValue   = lblVal
        
    def onChange(self, val):
#        val = self.__scale.get()
        self.__labelValue['text']  = self.__formatter(val)
        
    def get(self):
        return self.__scale.get()
        
    def set(self, val):
        return self.__scale.set(val)

        
        
class ParamItem(Frame, object):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.__label    = Label(self)
        self.__label.pack(side=LEFT)
        self.__entry    = Entry(self)
        self.__entry.pack(fill=X, expand=YES)
        self.__checkFunc    = None
        self.__image        = None

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
    def labelImage(self):
        return self.__label['image']
        
    @labelImage.setter
    def labelImage(self, image):
        self.__image    = image
        self.__label['image']   = image

    @property
    def entryText(self):
        return self.__entry.get()

    @entryText.setter
    def entryText(self, text):
        self.__entry.delete(0, END)
        self.__entry.insert(0, text)
        
    @property
    def entryVar(self):
        return self.__entry['textvariable']
        
    @entryVar.setter
    def entryVar(self, val):
        self.__entry.config(textvariable=val)

    def getInt(self):
        i   = self.__entry.get()
        return 0 if not i else int(self.__entry.get())

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
        self.bind('<Control-Key-c>', lambda event: 0)

    def selectAll(self):
        self.tag_add(SEL, '1.0', 'end-1c')
        self.see(INSERT)
        self.focus()
        return 'break'


class ScrolledTree(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.pack(expand=YES, fill=BOTH)
        self.makeWidgets()
        
    def makeWidgets(self):
        sbar    = Scrollbar(self)
        tree    = ttk.Treeview(self)
        sbar.config(command=tree.yview)
        tree.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        tree.pack(side=LEFT, expand=YES, fill=BOTH)
        self.tree   = tree
        
    for new, origin in (('insert', 'insert'), ('delete', 'delete')):
        locals()[new]    = MethodDelegator('tree', origin)        


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



class ScrolledList(Frame, object):
    methodNameMap   = {
        'insert':'insert', 
        'delete':'delete', 
        'itemConfig':'itemconfig',
        'listConfig':'config'
    }
    
    for methodName in methodNameMap:
        locals()[methodName]    = MethodDelegator('list', methodNameMap[methodName])
    
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

    def clear(self):
        self.__list.delete(0, END)
                
    @property
    def curSelection(self):
        return self.__list.curselection()
        
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
        super(Group, self).__init__(*args, **kwargs)
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
        
        
        
if __name__ == '__main__':
    window  = Tk()
    tree    = ScrolledTree(window)
    root    = tree.insert('', END, text='root')
    node    = tree.insert(root, END, text='node')
    window.mainloop()
    