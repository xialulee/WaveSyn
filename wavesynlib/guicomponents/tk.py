# -*- coding: utf-8 -*-
"""
Created on Fri Apr 03 15:46:05 2015

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import os
import sys

import math
import cmath

from Tkinter                                       import *
from ttk                                           import *
from Tkinter                                       import Frame
import tkFont
from tkFileDialog                                  import askdirectory

import PIL
from PIL                                           import ImageTk

from functools                                     import partial

from wavesynlib.languagecenter.utils               import autoSubs, MethodDelegator
from wavesynlib.languagecenter.designpatterns      import SimpleObserver, Observable


__DEBUG__ = False



    
import platform
win7plus    = False
if platform.system() == 'Windows':
    winver  = platform.version().split('.')    
    if int(winver[0])>=6 and int(winver[1])>=1:
        win7plus    = True

if win7plus:
    from wavesynlib.interfaces.windows.shell.taskbarmanager import ITaskbarList4, GUID_CTaskbarList
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
                

class PilImageFrame(Frame, object):
    def __init__(self, *args, **kwargs):
        pilImage    = kwargs.pop('pilImage')
        photo   = ImageTk.PhotoImage(pilImage)
        self.__photoImage   = photo
        Frame.__init__(self, *args, **kwargs)
        self.__label        = label = Label(self, image=photo)
        label.pack(expand=YES, fill=BOTH)
        



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
        tree    = Treeview(self)
        sbar.config(command=tree.yview)
        tree.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        tree.pack(side=LEFT, expand=YES, fill=BOTH)
        self.tree   = tree
        
    for new, origin in (
            ('insert', 'insert'), 
            ('delete', 'delete'),
            ('selection', 'selection'),
            ('item', 'item')
    ):
        locals()[new]    = MethodDelegator('tree', origin)        


class ScrolledText(Frame, object):
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
                    print('Ctrl+F: searching for {0}'.format(target))
                    print('position', where)
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
                
                
                
class DirIndicator(Frame, Observable):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        Observable.__init__(self)
        self.__text     = text      = Text(self, wrap=NONE, height=1.2, relief=SOLID)
        text.bind('<Configure>', self._onResize)
        text.bind('<KeyPress>', self._onKeyPress)
        text.pack(fill=X, expand=YES, side=LEFT)
        self.__defaultCursor        = text['cursor']
        self.__defaultBGColor       = text['background']


        # Browse Button
        text.tag_config('browse_button', foreground='orange')
        text.tag_bind('browse_button', '<Button-1>', self._onButtonClick)
        text.tag_bind('browse_button', '<Enter>', lambda *args: self._handCursor(True))
        text.tag_bind('browse_button', '<Leave>', lambda *args: self._handCursor(False))
        # End Browse Button
                
        self.__blankLen     = 2
        self.__browseText   = '...'
        self.__coding       = sys.getfilesystemencoding()
        self.__cwd          = None
        
        from wavesynlib.interfaces.timer.tk import TkTimer
        self.__timer        = TkTimer(self, interval=500)
        self.__timer.addObserver(self)
        self.__timer.active = True
                        
    def _onButtonClick(self, *args):
        directory   = askdirectory()
        if directory:
            os.chdir(directory)
            
    def _onResize(self, *args):
        self.__text.see(END)
        self.__text.mark_set(INSERT, END)


    def _handCursor(self, hand):
        text    = self.__text
        if hand:
            text.config(cursor='hand2')
        else:
            text.config(cursor=self.__defaultCursor)

    def _onFolderNameHover(self, tagName, enter=True, bgColor='pale green'):
        self._handCursor(enter)
        bgColor     = bgColor if enter else self.__defaultBGColor
        self.__text.tag_config(tagName, background=bgColor)        
        
    def _onSepClick(self, evt, path, menu=[None]):
        items   = [item for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))]
        if items: # Not Empty
            x, y    = self.winfo_pointerx(), self.winfo_pointery()
            menuWin = menu[0]
            if menuWin is not None:
                menuWin.destroy()
            menuWin     = menu[0]   = Toplevel()
            menuWin.overrideredirect(1) # No Title bar
            menuWin.geometry(autoSubs('200x300+$x+$y'))
            menuWin.bind('<FocusOut>', lambda evt: menuWin.destroy())
            itemList    = ScrolledList(menuWin)
            itemList.pack(expand=YES, fill=BOTH)
            itemList.list.focus_set()
            for item in items:
                itemList.insert(END, item)
                
            def onListClick(index, label):
                fullPath    = os.path.join(path, label)
                os.chdir(fullPath)
                menuWin.destroy()
                
            itemList.listClick  = onListClick
                        
    def _onKeyPress(self, evt):
        if evt.keycode == 13: # \n
            path    = self._getPathInText()
            if os.path.exists(path):
                os.chdir(path)
            else:
                self._refresh(self.__cwd)
            return 'break' # Not pass the event to the next handler.
            
    def _getPathInText(self):
        path    = self.__text.get('1.0', END)
        path    = path[:-(self.__blankLen + len(self.__browseText))]            
        return path
            
    def update(self, *args, **kwargs): # Observer protocol. For TkTimer.
        cwd     = os.getcwd()
        cwd     = cwd.replace(os.path.altsep, os.path.sep)
        if self.__cwd != cwd:
            self._refresh(cwd)
            self.notifyObservers(cwd)

    def _refresh(self, cwd):
        text        = self.__text
        self.__cwd  = cwd
        
        
        text    = self.__text
        text.delete('1.0', END)
        folderList  = cwd.split(os.path.sep)
        cumPath     = ''
        for index, folder in enumerate(folderList):
            folder      = folder.decode(self.__coding, 'ignore')
            cumPath += folder + os.path.sep 
            
            # Configure folder name
            tagName     = 'folder_name_' + str(index)
            text.tag_config(tagName)
            text.tag_bind(tagName, '<Button-1>', lambda evt, cumPath=cumPath: os.chdir(cumPath))
            text.tag_bind(tagName, '<Enter>', lambda evt, tagName=tagName: self._onFolderNameHover(tagName, enter=True))
            text.tag_bind(tagName, '<Leave>', lambda evt, tagName=tagName: self._onFolderNameHover(tagName, enter=False))
            text.insert(END, folder, tagName)
            # END Configure folder name
            
            # Configure folder sep
            sepName     = 'sep_tag_' + str(index)                
            text.tag_config(sepName)
            text.tag_bind(sepName, '<Button-1>', lambda evt, cumPath=cumPath: self._onSepClick(evt, cumPath))
            text.tag_bind(sepName, '<Enter>', lambda evt, tagName=sepName: self._onFolderNameHover(tagName, enter=True, bgColor='orange'))
            text.tag_bind(sepName, '<Leave>', lambda evt, tagName=sepName: self._onFolderNameHover(tagName, enter=False, bgColor='orange'))
            text.insert(END, os.path.sep, sepName)
            # END Configure folder sep
        

        text.insert(END, ' '*self.__blankLen)
        text.insert(END, self.__browseText, 'browse_button')                  
                

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
        


class FontFrame(Frame, object):
    def __init__(self, master=None, **kw):
        Frame.__init__(self, master, **kw)
        
        # Font selector
        selectorFrame = LabelFrame(self, text='Font Selector')
        selectorFrame.pack(side=LEFT)
        # Font face
        faceFrame = LabelFrame(selectorFrame, text='Font Face')
        faceFrame.pack()
        faceList = ScrolledList(faceFrame)
        faceList.pack()
        fonts = list(tkFont.families(self))
        fonts.sort()
        for font in fonts:
            faceList.insert(END, font)
        faceList.listClick = self.onFaceSelect
        self.faceList = faceList
            
        # Font size
        sizeFrame = LabelFrame(selectorFrame, text='Font Size')
        sizeFrame.pack()
        sizeCombo = Combobox(sizeFrame, takefocus=1, stat='readonly')
        sizeCombo.pack()
        sizeCombo['value'] = range(7, 23)
        sizeCombo.current(0)
        sizeCombo.bind('<<ComboboxSelected>>', self.onSizeSelect)
        self.sizeCombo = sizeCombo
        
        # Font Sample
        defaultFont = ('Courier', 10, tkFont.NORMAL)
        sampleFrame = LabelFrame(self, text='Samples')
        sampleFrame.pack(side=RIGHT, expand=YES, fill=Y)
        sampleLabel = Label(sampleFrame, text='\tabcdefghij\t\n\tABCDEFGHIJ\t\n\t0123456789\t', font=defaultFont)
        sampleLabel.pack(expand=YES)
        self.sampleLabel = sampleLabel
        
        self.face = defaultFont[0]
        self.size = defaultFont[1]
        sizeCombo.current(self.size - 7)
        
    def onFaceSelect(self, index, face):
        size = self.sizeCombo.get()
        self.setSample(face, size)
        
    def onSizeSelect(self, event):
        self.setSample(self.face, self.sizeCombo.get())
        
    def setSample(self, face, size):
        self.face = face
        self.size = size
        self.sampleLabel.config(font=(self.face, self.size, tkFont.NORMAL))                            
            
def askFont():
    win = Toplevel()
    win.title('Font Dialog')

    buttonFrame = Frame(win)
    retval = [None]
    def onClick(ret=None):
        win.destroy()
        retval[0] = ret
    
    buttonFrame.pack(side=BOTTOM)
    btnCancel = Button(buttonFrame, text='Cancel', command=lambda: onClick())
    btnCancel.pack(side=RIGHT)
    btnOk = Button(buttonFrame, text='OK', command=lambda: onClick((fontFrame.face, fontFrame.size)))
    btnOk.pack(side=RIGHT)    
        
    
    fontFrame = FontFrame(win)
    fontFrame.pack()
    win.focus_set()
    win.grab_set()
    win.wait_window()
    return retval[0]



from wavesynlib.interfaces.timer.basetimer import BaseObservableTimer            
class GUIConsumer(object):                    
    def __init__(self, producer, timer):
        if not callable(producer):
            raise TypeError('producer should be a callable object.')
        self.__producer = producer           
        
        if not isinstance(timer, BaseObservableTimer):
            raise TypeError('timer should be an instance of a derived class of BaseObservableTimer')
        self.__active = False
        self.__timer = timer
        self.__timer.addObserver(SimpleObserver(self.__onTick))
        self.__queue = Queue.Queue()
        self.__producerThread = None        
        
    def __onTick(self):
        try:
            while True:
                data = self.__queue.get_nowait()
                if self.__active is True:
                    self.consume(data)
        except Queue.Empty:
            pass
        
    def __runProducer(self):
        producer = self.__producer
        while True:
            self.__queue.put(producer())
        
    def consume(self, data):
        return NotImplemented
        
    @property
    def active(self):
        return self.__active
        
    @active.setter
    def active(self, val):
        self.__active = val
        if self.__active is True and self.__producerThread is None:
            self.__producerThread = thread.start_new_thread(self.__runProducer)
            

class ComplexCanvas(Canvas, object):
    def __init__(self, *args, **kwargs):
        Canvas.__init__(self, *args, **kwargs)
        self.__center   = None
        
    @property
    def center(self):
        return self.__center
        
    @center.setter
    def center(self, val):
        self.__center   = val
    
    def createCircle(self, radius, **options):
        center  = self.__center
        bbox    = (center.real-radius, center.imag-radius, center.real+radius, center.imag+radius)
        return self.create_oval(*bbox, **options)
        
    def createLine(self, p1, p2, **options):
        p1      = p1 + self.center
        p2      = p2 + self.center
        bbox    = (p1.real, p1.imag, p2.real, p2.imag)
        return self.create_line(*bbox, **options)
        
    def complexCoords(self, itemID, p1=None, p2=None, radius=None, center=0.0):
        if p1:
            p1      = p1 + self.center
            p2      = p2 + self.center
            bbox    = (p1.real, p1.imag, p2.real, p2.imag)
        else:
            center  += self.center
            delta   = radius + 1j * radius
            p3      = center - delta
            p4      = center + delta
            bbox    = (p3.real, p3.imag, p4.real, p4.imag)
        self.coords(itemID, *bbox)
            

class IQSlider(Frame, Observable):                
    class Indicator(object):
        def __init__(self, iq, solid=True):
            self.__iq           = iq
            self.__line         = iq.canvas.create_line(0, 0, 1, 1, fill='yellow')
            self.__circle       = iq.canvas.create_oval(0, 0, 1, 1, outline='yellow')
            self.__xLine        = iq.canvas.create_line(0, 0, 1, 1, fill='cyan')
            self.__yLine        = iq.canvas.create_line(0, 0, 1, 1, fill='cyan')            
            self.__textIQ       = iq.canvas.create_text((0, 0), anchor='se', fill='cyan', font=('Times New Roman',))
            self.__textPolar    = iq.canvas.create_text((0, 0), anchor='ne', fill='yellow', font=('Times New Roman',))
            self.__radius       = 3
            if not solid:
                iq.canvas.itemconfig(self.__line, dash=[1, 1])
                iq.canvas.itemconfig(self.__xLine, dash=[1, 1])
                iq.canvas.itemconfig(self.__yLine, dash=[1, 1])
            self.__active   = False
                
        def setPos(self, pos):
            radius  = self.__radius
            center  = self.__iq.center
            
            iq      = self.__iq   
            
            phi     = cmath.phase(pos-center)
            endPoint= iq.radius * cmath.exp(1j * phi) + center
            
            iq.canvas.coords(self.__line, center.real, center.imag, endPoint.real, endPoint.imag)
            iq.canvas.coords(self.__circle, pos.real-radius, pos.imag-radius, pos.real+radius, pos.imag+radius)
            
            iq.canvas.coords(self.__xLine, center.real-iq.radius, pos.imag, center.real+iq.radius, pos.imag)
            iq.canvas.coords(self.__yLine, pos.real, center.imag-iq.radius, pos.real, center.imag+iq.radius)
            
            iMag    = (pos.real - center.real) / iq.radius * iq.iRange
            qMag    = -(pos.imag - center.imag) / iq.radius * iq.qRange
            
            iq.canvas.itemconfig(self.__textIQ, text=u' I:{}, Q:{} '.format(int(iMag), int(qMag)))            
            iq.canvas.coords(self.__textIQ, pos.real, pos.imag)
            
            iq.canvas.itemconfig(self.__textPolar, text=u' A:{}, ϕ:{}° '.format(int(abs(iMag+1j*qMag)), int(360*math.atan2(qMag, iMag)/2/math.pi)))                        
            iq.canvas.coords(self.__textPolar, pos.real, pos.imag)
            
            if (pos.imag - center.imag) * (pos.real - center.real) > 0:
                anchorB     = 'sw'
                anchorY     = 'ne'                
            else:
                anchorB     = 'se'
                anchorY     = 'nw'
                
                
            iq.canvas.itemconfig(self.__textPolar, anchor=anchorY)
            iq.canvas.itemconfig(self.__textIQ, anchor=anchorB)                
            
            self.__active   = True
            
        @property
        def active(self):
            return self.__active
            
    
    
    def __init__(self, *args, **kwargs):
        self.__iRange   =   iRange  = kwargs.pop('iRange')
        self.__qRange   =   qRange  = kwargs.pop('qRange')
        Frame.__init__(self, *args, **kwargs)
        Observable.__init__(self)
                       
        self.__canvas   = canvas    = ComplexCanvas(self)

        canvas.grid(row=0, column=0, sticky='wens')
        canvas['bg']    = 'black'

        self.__qSlider  = qSlider   = Scale(self, from_=qRange, to=-qRange, orient='vertical')

        qSlider.grid(row=0, column=1, sticky='e')
        self.__iSlider  = iSlider   = Scale(self, from_=-iRange, to=iRange, orient='horizontal')        

        iSlider.grid(row=1, column=0, sticky='s')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.__pad  = 10        
        self.__width    = 0
        self.__height   = 0
        self.__center   = None
        self.__radius   = 0
        self.__bbox     = None
        
        self.__compMag  = 0 + 0j
        
        canvas.bind('<Configure>', self._onResize)
        self.__borderBox    = canvas.create_rectangle(0, 0, 10, 10, outline='green')        
        self.__borderCircle = canvas.create_oval(0, 0, 10, 10, outline='green', dash=[1, 2])
        self.__middleCircle = canvas.create_oval(0, 0, 10, 10, outline='green', dash=[1, 2])
        self.__vLine        = canvas.create_line(0, 0, 10, 10, fill='green', dash=[1, 2])
        self.__hLine        = canvas.create_line(0, 0, 10, 10, fill='green', dash=[1, 2])
        self.__dLine        = canvas.create_line(0, 0, 10, 10, fill='green', dash=[1, 2])
        self.__cdLine       = canvas.create_line(0, 0, 10, 10, fill='green', dash=[1, 2])
        self.__scaleCircles = []
        for k in range(60):
            if k % 5 == 0:
                color   = 'gold'
            else:
                color   = 'green'
            self.__scaleCircles.append(canvas.create_oval(0, 0, 10, 10, fill=color))
            
        self.__indicator1   = self.Indicator(self, solid=False)
        self.__indicator2   = self.Indicator(self)
        
        canvas.bind('<Motion>', self._onMouseMove)
        canvas.bind('<Button-1>', self._onClick)
        iSlider['command']  = self._onIQScale
        qSlider['command']  = self._onIQScale
        

    @property
    def canvas(self):
        return self.__canvas
        
    @property
    def center(self):
        return self.__center
        
    @property
    def bbox(self):
        return self.__bbox
        
    @property
    def radius(self):
        return self.__radius
        
    @property
    def iRange(self):
        return self.__iRange
        
    @property
    def qRange(self):
        return self.__qRange
        
    def isInBox(self, pos):
        bbox    = self.bbox
        if bbox[0]<=pos.real<=bbox[2] and bbox[1]<=pos.imag<=bbox[3]:
            return True
        else:
            return False
                
    def _redraw(self):
        canvas  = self.__canvas
        radius  = self.__radius
        center  = self.__center
        
        canvas.center   = center
        
        b1      = - radius - 1j * radius
        b2      = radius + 1j * radius

        for item in (self.__borderBox, self.__borderCircle):
            canvas.complexCoords(item, p1=b1, p2=b2)
                
        canvas.complexCoords(self.__middleCircle, p1=0.5*b1, p2=0.5*b2)
        
        canvas.complexCoords(self.__vLine, -1j*radius, 1j*radius)
        canvas.complexCoords(self.__hLine, -radius, radius)
        canvas.complexCoords(self.__dLine, p1=b1, p2=b2)
        canvas.complexCoords(self.__cdLine, p1=b1.conjugate(), p2=b2.conjugate())
                
        exp     = cmath.exp
        sR      = 3
        delta   = 2 * math.pi / len(self.__scaleCircles)
        
        for index, circle in enumerate(self.__scaleCircles):
            pos = radius * exp(1j * delta * index)
            canvas.complexCoords(circle, center=pos, radius=sR)
            
        if self.__indicator2.active:
            posX    = self.__compMag.real / self.__iRange * radius + center.real
            posY    = -self.__compMag.imag / self.__qRange * radius + center.imag
            self.__indicator2.setPos(posX + 1j * posY)
            
        if self.__indicator1.active:
            posX    = self.__iSlider.get() / self.__iRange * radius + center.real
            posY    = -self.__qSlider.get() / self.__qRange * radius + center.imag
            self.__indicator1.setPos(posX + 1j * posY)
        
        
    def _onResize(self, event):
        pad     = self.__pad
        width, height   = event.width, event.height
        size                = min(width, height) - pad
        self.__iSlider['length']   = size
        self.__qSlider['length']   = size 
        self.__radius   = radius    = size / 2 - pad
        self.__width    = width
        self.__height   = height
        self.__center   = center    = (width / 2) + 1j * (height / 2)
        
        b1      = center - radius - 1j * radius
        b2      = center + radius + 1j * radius
        self.__bbox     = [int(b) for b in (b1.real, b1.imag, b2.real, b2.imag)]                
        self._redraw()
        
    def _onMouseMove(self, event):
        pos     = event.x + 1j * event.y
        if self.isInBox(pos):
            absPos  = pos-self.center
            bbox    = self.bbox
            radius  = (bbox[2] - bbox[0]) / 2
            self.__iSlider.set(int(absPos.real/radius*self.__iRange))
            self.__qSlider.set(int(-absPos.imag/radius*self.__qRange))
            self.__indicator1.setPos(pos)
            
    def _onClick(self, event):
        pos     = event.x + 1j * event.y
        if self.isInBox(pos):
            self.__indicator2.setPos(pos)
            self.__compMag  = self.__iSlider.get() + 1j * self.__qSlider.get()
            
    def _onIQScale(self, val):
        self._redraw()

            
            
        
class ArrayRenderMixin(object):
    def renderArray(self, arr, imageId=None):
        image   = PIL.Image.fromarray(arr)
        photoImage   = ImageTk.PhotoImage(image=image)

        if not imageId:
            imageId  = self.create_image((0, 0), image=photoImage, anchor='nw')
        else:
            self.itemconfig(imageId, image=photoImage)
        return imageId, photoImage

        
if __name__ == '__main__':
#    window  = Tk()
#    tree    = ScrolledTree(window)
#    root    = tree.insert('', END, text='root')
#    node    = tree.insert(root, END, text='node')
#    window.mainloop()
#    window = Tk()
#    print (askFont())
#    window.mainloop()
    root    = Tk()
    iq      = IQSlider(root, iRange=512, qRange=512, relief='raised')
    iq.pack(expand='yes', fill='both')
    root.mainloop()
    

