# -*- coding: utf-8 -*-
"""
Created on Fri Apr 03 15:46:05 2015

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import os
import sys
import platform

import math
import cmath

from six.moves.tkinter import *
from six.moves.tkinter_ttk import *
from six.moves.tkinter import Frame
import six.moves.tkinter_font as tkFont
from six.moves.tkinter_tkfiledialog import askdirectory

import PIL
from PIL import ImageTk

from functools import partial

from wavesynlib.languagecenter.utils import auto_subs, MethodDelegator
from wavesynlib.languagecenter.designpatterns import SimpleObserver, Observable
from wavesynlib.interfaces.timer.basetimer import BaseObservableTimer

__DEBUG__ = False
    
win = False
win7plus = False
if platform.system() == 'Windows':
    win = True
    winver  = platform.version().split('.')    
    if int(winver[0])>=6 and int(winver[1])>=1:
        win7plus = True

if win7plus:
    from wavesynlib.interfaces.windows.shell.taskbarmanager import (
        ITaskbarList4, GUID_CTaskbarList)
    from comtypes import CoCreateInstance
    import ctypes as ct
    from win32con import GWL_EXSTYLE, WS_EX_LAYERED, LWA_ALPHA
    
    GetParent = ct.windll.user32.GetParent
    SetWindowLongA = ct.windll.user32.SetWindowLongA
    SetLayeredWindowAttributes = ct.windll.user32.SetLayeredWindowAttributes

    class TaskbarIcon(object):
        def __init__(self, root):
            self.__tbm  = CoCreateInstance(GUID_CTaskbarList, 
                                           interface=ITaskbarList4)
            self.__root = root

        @property
        def progress(self):
            '''Not implemented'''
            pass

        @progress.setter
        def progress(self, value):
            self.__tbm.SetProgressValue(GetParent(self.__root.winfo_id()), 
                                        int(value), 100)

        @property
        def state(self):
            '''Not Implemented'''
            pass

        @state.setter
        def state(self, state):
            self.__tbm.SetProgressState(GetParent(self.__root.winfo_id()), 
                                        state)
                                        
                                        
    class Transparenter(object):
        def __init__(self, tk_window):
            self._tk_object = tk_window
            self._handle = None
            
        def _get_window_handle(self):
            if self._handle is None:
                self._handle = GetParent(self._tk_object.winfo_id())
            SetWindowLongA(self._handle, GWL_EXSTYLE, WS_EX_LAYERED)
            return self._handle
            
        def set_transparency(self, transparency):
            transparency = ct.c_ubyte(transparency)
            handle = self._get_window_handle()
            SetLayeredWindowAttributes(handle, 0, transparency, LWA_ALPHA)
            
else:
    class TaskbarIcon(object):
        def __init__(self, root):
            pass


def check_value(d, i, P, s, S, v, V, W, func):
    try:
        func(P)
        return True
    except ValueError:
        return True if P == '' or P == '-' else False
        
        
def check_positive_float(d, i, P, s, S, v, V, W):
    try:
        assert float(P) > 0
        return True
    except (ValueError, AssertionError):
        return True if P=='' else False
        

class ValueChecker(object):
    def __init__(self, root):
        self.__root = root
        self.check_int = (root.register(partial(check_value, func=int)),
                            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.check_float = (root.register(partial(check_value, func=float)),
                            '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.check_positive_float = (root.register(check_positive_float),
                                     '%d', '%i', '%P', '%s', '%S', '%v', 
                                     '%V', '%W')


#class LabeledEntry(Frame, object):
#    def __init__(self, *args, **kwargs):
#        Frame.__init__(self, *args, **kwargs)
#        self.__entry = Entry(self)
#        self.__label = Label(self)
#        
#        if 'labelfirst' in kwargs and kwargs['labelfirst']:
#            self.__label.pack(side=LEFT)
#            self.__entry.pack(side=LEFT)
#        else:
#            self.__entry.pack(side=LEFT)
#            self.__label.pack(side=LEFT)
#            
#        if 'labeltext' in kwargs:
#            self.__label['text']    =kwargs['labeltext']
#
#    @property
#    def entry(self):
#        return self.__entry
#
#    @property
#    def label(self):
#        return self.__label
        
        
class LabeledScale(Frame, object):
    def __init__(self, *args, **kwargs):
        from_ = kwargs.pop('from_')
        to = kwargs.pop('to')
        name = kwargs.pop('name')
        formatter = kwargs.pop('formatter', str)
        self.__formatter = formatter
        Frame.__init__(self, *args, **kwargs)
        
        if name is not None:
            Label(self, text=name).pack(side=LEFT)
        
        self.__scale = Scale(self, from_=from_, to=to, 
                                command=self._on_change)
        self.__scale.pack(side=LEFT, fill=X, expand=YES)
        
        self.__value_label = value_label = Label(self)
        value_label.pack(side=LEFT)
                
    def _on_change(self, val):
        self.__value_label['text']  = self.__formatter(val)
        
    def get(self):
        return self.__scale.get()
        
    def set(self, val):
        return self.__scale.set(val)
                                                                  
        
class LabeledEntry(Frame, object):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.__label = Label(self)
        self.__label.pack(side=LEFT)
        self.__entry = Entry(self)
        self.__entry.pack(fill=X, expand=YES)
        self.__checker_function = None
        self.__image = None

    @property
    def label(self):
        return self.__label

    @property
    def entry(self):
        return self.__entry

    @property
    def label_text(self):
        return self.__label['text']

    @label_text.setter
    def label_text(self, text):
        self.__label['text']    = text
        
    @property
    def label_image(self):
        return self.__label['image']
        
    @label_image.setter
    def label_image(self, image):
        self.__image = image
        self.__label['image'] = image

    @property
    def entry_text(self):
        return self.__entry.get()

    @entry_text.setter
    def entry_text(self, text):
        self.__entry.delete(0, END)
        self.__entry.insert(0, text)
        
    @property
    def entry_variable(self):
        return self.__entry['textvariable']
        
    @entry_variable.setter
    def entry_variable(self, val):
        self.__entry.config(textvariable=val)

    def get_int(self):
        i = self.__entry.get()
        return 0 if not i else int(self.__entry.get())

    def get_float(self):
        return float(self.__entry.get())

    @property
    def label_width(self):
        return self.__label['width']

    @label_width.setter
    def label_width(self, width):
        self.__label['width']   = width

    @property
    def entry_width(self):
        return self.__entry['width']

    @entry_width.setter
    def entry_width(self, width):
        self.__entry['width']   = width

    @property
    def checker_function(self):
        return self.__checker_function

    @checker_function.setter
    def checker_function(self, func):
        self.__checker_function    = func
        self.__entry.config(validate='key', validatecommand=func)
                

class PILImageFrame(Frame, object):
    def __init__(self, *args, **kwargs):
        pil_image = kwargs.pop('pil_image')
        photo = ImageTk.PhotoImage(pil_image)
        self.__photoImage = photo
        Frame.__init__(self, *args, **kwargs)
        self.__label = label = Label(self, image=photo)
        label.pack(expand=YES, fill=BOTH)
        

class TextWinHotkey(Text):
    def __init__(self, *args, **kwargs):
        Text.__init__(self, *args, **kwargs)
        self.bind('<Control-Key-a>', lambda event: self.select_all())
        self.bind('<Control-Key-c>', lambda event: 0)

    def select_all(self):
        self.tag_add(SEL, '1.0', 'end-1c')
        self.see(INSERT)
        self.focus()
        return 'break'


class ScrolledTree(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        self.pack(expand=YES, fill=BOTH)
        self.make_widgets()
        
    def make_widgets(self):
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
        locals()[new] = MethodDelegator('tree', origin)        


class ScrolledText(Frame, object):
    '''This class is based on Programming Python 3rd Edition P517'''
    def __init__(self, parent=None, text='', file=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.make_widgets()
        self.set_text(text, file)
        
    def make_widgets(self):
        sbar    = Scrollbar(self)
        text    = TextWinHotkey(self, relief=SUNKEN)
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        text.pack(side=LEFT, expand=YES, fill=BOTH)
        self.text   = text

    def set_text(self, text='', file=None):
        if file:
            with open(file, 'r') as f:
                text = f.read().decode('gbk')
        self.text.delete('1.0', END)
        self.text.insert('1.0', text)
        self.text.mark_set(INSERT, '1.0')
        self.text.focus()
        
    def clear(self):
        self.set_text()

    def append_text(self, text=''):
        self.text.insert(END, text)

    def get_text(self):
        return self.text.get('1.0', END+'-1c')

    def select_all(self):
        return self.text.select_all()

    def find_text(self, target):
        if target:
            where = self.text.search(target, INSERT, END)
            if where:
                if __DEBUG__:
                    print('Ctrl+F: searching for {0}'.format(target))
                    print('position', where)
                pastit = where + ('+%dc' % len(target))
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
    method_name_map   = {
        'insert':'insert', 
        'delete':'delete', 
        'item_config':'itemconfig',
        'list_config':'config'
    }
    
    for method_name in method_name_map:
        locals()[method_name] = MethodDelegator('list', 
                                                method_name_map[method_name])
    
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        sbar = Scrollbar(self)
        list = Listbox(self)
        sbar.config(command=list.yview)
        list.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        list.pack(side=LEFT, expand=YES, fill=BOTH)
        list.bind('<<ListboxSelect>>', self._on_listbox_click)
        
        self.__list_click_callback = None
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
    def current_selection(self):
        return self.__list.curselection()
        
    @property
    def list_click_callback(self):
        return self.__list_click_callback

    @list_click_callback.setter
    def list_click_callback(self, val):
        if not callable(val):
            raise TypeError
        self.__list_click_callback = val

    def _on_listbox_click(self, event):
        index = self.__list.curselection()
        if len(index) > 0:
            index = index[0]
            label = self.__list.get(index)
            if self.list_click_callback:
                self.list_click_callback(index, label)

class DirIndicator(Frame, Observable):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        Observable.__init__(self)
        self._text = text = Text(self, wrap=NONE, height=1.2, relief=SOLID)
        text.bind('<Configure>', self._on_resize)
        text.bind('<KeyPress>', self._on_key_press)
        text.pack(fill=X, expand=YES, side=LEFT)
        self._default_cursor = text['cursor']
        self._default_background_color = text['background']


        # Browse Button
        text.tag_config('browse_button', foreground='orange')
        text.tag_bind('browse_button', '<Button-1>', self._on_button_click)
        text.tag_bind('browse_button', '<Enter>',
                      lambda *args: self._change_cursor_to_hand(True))
        text.tag_bind('browse_button', '<Leave>',
                      lambda *args: self._change_cursor_to_hand(False))
        # End Browse Button
                
        self._blank_len = 2
        self._browse_text = 'BROWSE'
        self._coding = sys.getfilesystemencoding()
        self._directory          = None
                                
    def _on_button_click(self, *args):
        directory   = askdirectory()
        if directory:
            self.change_dir(directory)
            
    def _on_resize(self, *args):
        self._text.see(END)
        self._text.mark_set(INSERT, END)


    def _change_cursor_to_hand(self, hand):
        text    = self._text
        if hand:
            text.config(cursor='hand2')
        else:
            text.config(cursor=self._default_cursor)

    def _on_folder_name_hover(self, tagName, enter=True, 
                              background_color='pale green'):
        self._change_cursor_to_hand(enter)
        background_color     = background_color if enter else \
            self._default_background_color
        self._text.tag_config(tagName, background=background_color)        
        
    def _on_seperator_click(self, evt, path, menu=[None]):
        items   = [item for item in os.listdir(path) if 
                   os.path.isdir(os.path.join(path, item))]
        if items: # Not Empty
            x, y    = self.winfo_pointerx(), self.winfo_pointery()
            menuWin = menu[0]
            if menuWin is not None:
                menuWin.destroy()
            menuWin     = menu[0]   = Toplevel()
            menuWin.overrideredirect(1) # No Title bar
            menuWin.geometry(auto_subs('200x300+$x+$y'))
            menuWin.bind('<FocusOut>', lambda evt: menuWin.destroy())
            itemList    = ScrolledList(menuWin)
            itemList.pack(expand=YES, fill=BOTH)
            itemList.list.focus_set()
            for item in items:
                itemList.insert(END, item)
                
            def on_list_click(index, label):
                fullPath    = os.path.join(path, label)
                self.change_dir(fullPath)
                menuWin.destroy()
                
            itemList.list_click_callback  = on_list_click
                        
    def _on_key_press(self, evt):
        rend, cend = self._text.index('end-1c').split('.')
        cend = int(cend)
        r, c = self._text.index('insert').split('.')
        c = int(c)
        if c > cend - self._blank_len - len(self._browse_text):
            if evt.keycode not in (37, 39):
                return 'break'
        
        if evt.keycode == 13: # \n
            path = self._get_path()
            if os.path.exists(path):
                self.change_dir(path)
            else:
                self._refresh()
            return 'break' # Not pass the event to the next handler.

            
    def _get_path(self):
        path    = self._text.get('1.0', END)
        path    = path[:-(self._blank_len + len(self._browse_text))]            
        return path
            
    def _refresh(self):
        text = self._text
        directory = self._directory

        text.delete('1.0', END)
        folderList  = directory.split(os.path.sep)
        cumPath     = ''
        for index, folder in enumerate(folderList):
            if not isinstance(folder, unicode):
                folder = folder.decode(self._coding, 'ignore')
            cumPath += folder + os.path.sep 
            
            # Configure folder name
            tagName     = 'folder_name_' + str(index)
            text.tag_config(tagName)
            text.tag_bind(tagName, '<Button-1>', 
                          lambda evt, cumPath=cumPath: self.change_dir(cumPath))
            text.tag_bind(tagName, '<Enter>', 
                          lambda evt, tagName=tagName: 
                              self._on_folder_name_hover(tagName, enter=True))
            text.tag_bind(tagName, '<Leave>', 
                          lambda evt, tagName=tagName: 
                              self._on_folder_name_hover(tagName, enter=False))
            text.insert(END, folder, tagName)
            # END Configure folder name
            
            # Configure folder sep
            sepName     = 'sep_tag_' + str(index)                
            text.tag_config(sepName)
            text.tag_bind(sepName, '<Button-1>', 
                          lambda evt, cumPath=cumPath: 
                              self._on_seperator_click(evt, cumPath))
            text.tag_bind(sepName, '<Enter>', 
                          lambda evt, tagName=sepName: 
                          self._on_folder_name_hover(tagName, 
                                                     enter=True, 
                                                     background_color='orange'))
            text.tag_bind(sepName, '<Leave>', 
                          lambda evt, tagName=sepName: 
                              self._on_folder_name_hover(tagName, 
                                                         enter=False, 
                                                         background_color='orange'))
            text.insert(END, os.path.sep, sepName)
            # END Configure folder sep
        

        text.insert(END, ' '*self._blank_len)
        text.insert(END, self._browse_text, 'browse_button')      

    def change_dir(self, dirname):
        dirname = os.path.abspath(dirname)
        self._directory = dirname
        self._refresh()
        self.notify_observers(dirname)
        
    @property
    def directory(self):
        return self._directory


class CWDIndicator(DirIndicator):
    def __init__(self, *args, **kwargs):
        DirIndicator.__init__(self, *args, **kwargs)
                        
        from wavesynlib.interfaces.timer.tk import TkTimer
        self.__timer        = TkTimer(self, interval=500)
        self.__timer.add_observer(self)
        self.__timer.active = True
                                                              
    def update(self, *args, **kwargs): 
        '''Method "update" is called by Observable objects. 
Here, it is called by the timer of CWDIndicator instance.
Normally, no argument is passed.'''        
        cwd = os.getcwd()
        cwd = cwd.decode(self._coding, 'ignore')
        if os.path.altsep is not None: # Windows OS
            cwd = cwd.replace(os.path.altsep, os.path.sep)
        if self._directory != cwd:
            self.change_dir(cwd)

    def change_dir(self, dirname):
        os.chdir(dirname)  
        super(CWDIndicator, self).change_dir(dirname)          
                

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
        selector_frame = LabelFrame(self, text='Font Selector')
        selector_frame.pack(side=LEFT)
        # Font face
        face_frame = LabelFrame(selector_frame, text='Font Face')
        face_frame.pack()
        face_list = ScrolledList(face_frame)
        face_list.pack()
        fonts = list(tkFont.families(self))
        fonts.sort()
        for font in fonts:
            face_list.insert(END, font)
        face_list.list_click_callback = self._on_face_select
        self.face_list = face_list
            
        # Font size
        size_frame = LabelFrame(selector_frame, text='Font Size')
        size_frame.pack()
        size_combo = Combobox(size_frame, takefocus=1, stat='readonly')
        size_combo.pack()
        size_combo['value'] = range(7, 23)
        size_combo.current(0)
        size_combo.bind('<<ComboboxSelected>>', self._on_size_select)
        self.size_combo = size_combo
        
        # Font Sample
        default_font = ('Courier', 10, tkFont.NORMAL)
        sample_frame = LabelFrame(self, text='Samples')
        sample_frame.pack(side=RIGHT, expand=YES, fill=Y)
        sample_label = Label(sample_frame, 
                             text='\tabcdefghij\t\n\tABCDEFGHIJ\t\n\t0123456789\t', 
                             font=default_font)
        sample_label.pack(expand=YES)
        self.sample_label = sample_label
        
        self.face = default_font[0]
        self.size = default_font[1]
        size_combo.current(self.size - 7)
        
    def _on_face_select(self, index, face):
        size = self.size_combo.get()
        self._set_sample(face, size)
        
    def _on_size_select(self, event):
        self._set_sample(self.face, self.size_combo.get())
        
    def _set_sample(self, face, size):
        self.face = face
        self.size = size
        self.sample_label.config(font=(self.face, self.size, tkFont.NORMAL))                            
            
def ask_font():
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


class GUIConsumer(object):                    
    def __init__(self, producer, timer):
        if not callable(producer):
            raise TypeError('producer should be a callable object.')
        self.__producer = producer           
        
        if not isinstance(timer, BaseObservableTimer):
            raise TypeError('timer should be an instance of a derived class of BaseObservableTimer')
        self.__active = False
        self.__timer = timer
        self.__timer.add_observer(SimpleObserver(self._on_tick))
        self.__queue = Queue.Queue()
        self.__producerThread = None        
        
    def _on_tick(self):
        try:
            while True:
                data = self.__queue.get_nowait()
                if self.__active is True:
                    self.consume(data)
        except Queue.Empty:
            pass
        
    def _run_producer(self):
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
            self.__producerThread = thread.start_new_thread(self._run_producer)
            

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
    
    def complex_create_circle(self, radius, **options):
        center  = self.__center
        bbox    = (center.real-radius, center.imag-radius, center.real+radius, center.imag+radius)
        return self.create_oval(*bbox, **options)
        
    def complex_create_line(self, p1, p2, **options):
        p1      = p1 + self.center
        p2      = p2 + self.center
        bbox    = (p1.real, p1.imag, p2.real, p2.imag)
        return self.create_line(*bbox, **options)
        
    def complex_coords(self, item_id, p1=None, p2=None, radius=None, center=0.0):
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
        self.coords(item_id, *bbox)
            

class IQSlider(Frame, Observable):                
    class Indicator(object):
        def __init__(self, iq, solid=True):
            self.__iq           = iq
            self.__line         = iq.canvas.create_line(0, 0, 1, 1, fill='yellow')
            self.__circle       = iq.canvas.create_oval(0, 0, 1, 1, outline='yellow')
            self.__xLine        = iq.canvas.create_line(0, 0, 1, 1, fill='cyan')
            self.__yLine        = iq.canvas.create_line(0, 0, 1, 1, fill='cyan')            
            self.__iq_text       = iq.canvas.create_text((0, 0), anchor='se', fill='cyan', font=('Times New Roman',))
            self.__textPolar    = iq.canvas.create_text((0, 0), anchor='ne', fill='yellow', font=('Times New Roman',))
            self.__radius       = 3
            if not solid:
                iq.canvas.itemconfig(self.__line, dash=[1, 1])
                iq.canvas.itemconfig(self.__xLine, dash=[1, 1])
                iq.canvas.itemconfig(self.__yLine, dash=[1, 1])
            self.__active   = False
                
        def set_pos(self, pos):
            radius  = self.__radius
            center  = self.__iq.center
            
            iq      = self.__iq   
            
            phi     = cmath.phase(pos-center)
            endPoint= iq.radius * cmath.exp(1j * phi) + center
            
            iq.canvas.coords(self.__line, center.real, center.imag, endPoint.real, endPoint.imag)
            iq.canvas.coords(self.__circle, pos.real-radius, pos.imag-radius, pos.real+radius, pos.imag+radius)
            
            iq.canvas.coords(self.__xLine, center.real-iq.radius, pos.imag, center.real+iq.radius, pos.imag)
            iq.canvas.coords(self.__yLine, pos.real, center.imag-iq.radius, pos.real, center.imag+iq.radius)
            
            i_magnitude    = (pos.real - center.real) / iq.radius * iq.i_range
            q_magnitude    = -(pos.imag - center.imag) / iq.radius * iq.q_range
            
            iq.canvas.itemconfig(self.__iq_text, text=u' I:{}, Q:{} '.format(int(i_magnitude), int(q_magnitude)))            
            iq.canvas.coords(self.__iq_text, pos.real, pos.imag)
            
            iq.canvas.itemconfig(self.__textPolar, text=u' A:{}, ϕ:{}° '.format(int(abs(i_magnitude+1j*q_magnitude)), int(360*math.atan2(q_magnitude, i_magnitude)/2/math.pi)))                        
            iq.canvas.coords(self.__textPolar, pos.real, pos.imag)
            
            if (pos.imag - center.imag) * (pos.real - center.real) > 0:
                anchor_cart     = 'sw'
                anchor_polar    = 'ne'                
            else:
                anchor_cart     = 'se'
                anchor_polar    = 'nw'
                
                
            iq.canvas.itemconfig(self.__textPolar, anchor=anchor_polar)
            iq.canvas.itemconfig(self.__iq_text, anchor=anchor_cart)                
            
            self.__active   = True
            
        @property
        def active(self):
            return self.__active
            
    
    
    def __init__(self, *args, **kwargs):
        self.__i_range   =   i_range  = kwargs.pop('i_range')
        self.__q_range   =   q_range  = kwargs.pop('q_range')
        Frame.__init__(self, *args, **kwargs)
        Observable.__init__(self)
                       
        self.__canvas   = canvas    = ComplexCanvas(self)

        canvas.grid(row=0, column=0, sticky='wens')
        canvas['bg']    = 'black'

        self.__q_slider  = q_slider   = Scale(self, from_=q_range, to=-q_range, orient='vertical')

        q_slider.grid(row=0, column=1, sticky='e')
        self.__i_slider  = i_slider   = Scale(self, from_=-i_range, to=i_range, orient='horizontal')        

        i_slider.grid(row=1, column=0, sticky='s')
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.__pad  = 10        
        self.__width    = 0
        self.__height   = 0
        self.__center   = None
        self.__radius   = 0
        self.__bbox     = None
        
        self.__complex_magnitude  = 0 + 0j
        
        canvas.bind('<Configure>', self._on_resize)
        self.__borderBox    = canvas.create_rectangle(0, 0, 10, 10, outline='green')        
        self.__borderCircle = canvas.create_oval(0, 0, 10, 10, outline='green', dash=[1, 2])
        self.__middleCircle = canvas.create_oval(0, 0, 10, 10, outline='green', dash=[1, 2])
        self.__vLine        = canvas.create_line(0, 0, 10, 10, fill='green', dash=[1, 2])
        self.__hLine        = canvas.create_line(0, 0, 10, 10, fill='green', dash=[1, 2])
        self.__dLine        = canvas.create_line(0, 0, 10, 10, fill='green', dash=[1, 2])
        self.__cdLine       = canvas.create_line(0, 0, 10, 10, fill='green', dash=[1, 2])
        self.__scale_circles = []
        for k in range(60):
            if k % 5 == 0:
                color   = 'gold'
            else:
                color   = 'green'
            self.__scale_circles.append(canvas.create_oval(0, 0, 10, 10, fill=color))
            
        self.__indicator1   = self.Indicator(self, solid=False)
        self.__indicator2   = self.Indicator(self)
        
        canvas.bind('<Motion>', self._on_mouse_move)
        canvas.bind('<Button-1>', self._on_click)
        i_slider['command']  = self._on_iq_scale
        q_slider['command']  = self._on_iq_scale
        

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
    def i_range(self):
        return self.__i_range
        
    @property
    def q_range(self):
        return self.__q_range
        
    def is_point_in_box(self, pos):
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
            canvas.complex_coords(item, p1=b1, p2=b2)
                
        canvas.complex_coords(self.__middleCircle, p1=0.5*b1, p2=0.5*b2)
        
        canvas.complex_coords(self.__vLine, -1j*radius, 1j*radius)
        canvas.complex_coords(self.__hLine, -radius, radius)
        canvas.complex_coords(self.__dLine, p1=b1, p2=b2)
        canvas.complex_coords(self.__cdLine, p1=b1.conjugate(), p2=b2.conjugate())
                
        exp     = cmath.exp
        __scale_circle_radius      = 3
        delta   = 2 * math.pi / len(self.__scale_circles)
        
        for index, circle in enumerate(self.__scale_circles):
            pos = radius * exp(1j * delta * index)
            canvas.complex_coords(circle, center=pos, radius=__scale_circle_radius)
            
        if self.__indicator2.active:
            pos_x    = self.__complex_magnitude.real / self.__i_range * radius + center.real
            pos_y    = -self.__complex_magnitude.imag / self.__q_range * radius + center.imag
            self.__indicator2.set_pos(pos_x + 1j * pos_y)
            
        if self.__indicator1.active:
            pos_x    = self.__i_slider.get() / self.__i_range * radius + center.real
            pos_y    = -self.__q_slider.get() / self.__q_range * radius + center.imag
            self.__indicator1.set_pos(pos_x + 1j * pos_y)
        
        
    def _on_resize(self, event):
        pad     = self.__pad
        width, height   = event.width, event.height
        size                = min(width, height) - pad
        self.__i_slider['length']   = size
        self.__q_slider['length']   = size 
        self.__radius   = radius    = size / 2 - pad
        self.__width    = width
        self.__height   = height
        self.__center   = center    = (width / 2) + 1j * (height / 2)
        
        b1      = center - radius - 1j * radius
        b2      = center + radius + 1j * radius
        self.__bbox     = [int(b) for b in (b1.real, b1.imag, b2.real, b2.imag)]                
        self._redraw()
        
    def _on_mouse_move(self, event):
        pos     = event.x + 1j * event.y
        if self.is_point_in_box(pos):
            absPos  = pos-self.center
            bbox    = self.bbox
            radius  = (bbox[2] - bbox[0]) / 2
            self.__i_slider.set(int(absPos.real/radius*self.__i_range))
            self.__q_slider.set(int(-absPos.imag/radius*self.__q_range))
            self.__indicator1.set_pos(pos)
            
    def _on_click(self, event):
        pos     = event.x + 1j * event.y
        if self.is_point_in_box(pos):
            self.__indicator2.set_pos(pos)
            self.__complex_magnitude  = self.__i_slider.get() + 1j * self.__q_slider.get()
            
    def _on_iq_scale(self, val):
        self._redraw()

            
            
        
class ArrayRenderMixin(object):
    def render_array(self, arr, image_id=None):
        image   = PIL.Image.fromarray(arr)
        photoImage   = ImageTk.PhotoImage(image=image)

        if not image_id:
            image_id  = self.create_image((0, 0), image=photoImage, anchor='nw')
        else:
            self.itemconfig(image_id, image=photoImage)
        return image_id, photoImage

        
if __name__ == '__main__':
    #    window  = Tk()
    #    tree    = ScrolledTree(window)
    #    root    = tree.insert('', END, text='root')
    #    node    = tree.insert(root, END, text='node')
    #    window.mainloop()
    #    window = Tk()
    #    print (ask_font())
    #    window.mainloop()
    root    = Tk()
    iq      = IQSlider(root, i_range=512, q_range=512, relief='raised')
    iq.pack(expand='yes', fill='both')
    root.mainloop()
    

