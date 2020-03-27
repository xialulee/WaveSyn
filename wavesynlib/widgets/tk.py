# -*- coding: utf-8 -*-
"""
Created on Fri Apr 03 15:46:05 2015

@author: Feng-cong Li
"""
import os
import sys
import platform
from importlib import import_module

import math
import cmath

import json
import random

from tkinter import Text, Listbox, IntVar, Tk, Toplevel, Canvas
from tkinter.ttk import Label, Scale, Entry, Button, Scrollbar, Treeview, Combobox
from tkinter import tix
from tkinter import Frame
from tkinter.filedialog import askdirectory, asksaveasfilename

import PIL
from PIL import ImageTk
from PIL import Image

from functools import partial

from wavesynlib.languagecenter.utils import (
        MethodDelegator, FunctionChain, get_caller_dir)
from wavesynlib.languagecenter.designpatterns import Observable

__DEBUG__ = False
    


#class FontFrame(Frame, object):
#    def __init__(self, master=None, **kw):
#        Frame.__init__(self, master, **kw)
#        
#        # Font selector
#        selector_frame = LabelFrame(self, text='Font Selector')
#        selector_frame.pack(side=LEFT)
#        # Font face
#        face_frame = LabelFrame(selector_frame, text='Font Face')
#        face_frame.pack()
#        face_list = ScrolledList(face_frame)
#        face_list.pack()
#        fonts = list(tkFont.families(self))
#        fonts.sort()
#        for font in fonts:
#            face_list.insert('end', font)
#        face_list.list_click_callback = self._on_face_select
#        self.face_list = face_list
#            
#        # Font size
#        size_frame = LabelFrame(selector_frame, text='Font Size')
#        size_frame.pack()
#        size_combo = Combobox(size_frame, takefocus=1, stat='readonly')
#        size_combo.pack()
#        size_combo['value'] = range(7, 23)
#        size_combo.current(0)
#        size_combo.bind('<<ComboboxSelected>>', self._on_size_select)
#        self.size_combo = size_combo
#        
#        # Font Sample
#        default_font = ('Courier', 10, tkFont.NORMAL)
#        sample_frame = LabelFrame(self, text='Samples')
#        sample_frame.pack(side=RIGHT, expand=YES, fill=Y)
#        sample_label = Label(sample_frame, 
#                             text='\tabcdefghij\t\n\tABCDEFGHIJ\t\n\t0123456789\t', 
#                             font=default_font)
#        sample_label.pack(expand=YES)
#        self.sample_label = sample_label
#        
#        self.face = default_font[0]
#        self.size = default_font[1]
#        size_combo.current(self.size - 7)
#        
#    def _on_face_select(self, index, face):
#        size = self.size_combo.get()
#        self._set_sample(face, size)
#        
#    def _on_size_select(self, event):
#        self._set_sample(self.face, self.size_combo.get())
#        
#    def _set_sample(self, face, size):
#        self.face = face
#        self.size = size
#        self.sample_label.config(font=(self.face, self.size, tkFont.NORMAL))                            
#            
#def ask_font():
#    win = Toplevel()
#    win.title('Font Dialog')
#
#    buttonFrame = Frame(win)
#    retval = [None]
#    def onClick(ret=None):
#        win.destroy()
#        retval[0] = ret
#    
#    buttonFrame.pack(side='bottom')
#    btnCancel = Button(buttonFrame, text='Cancel', command=lambda: onClick())
#    btnCancel.pack(side=RIGHT)
#    btnOk = Button(buttonFrame, text='OK', command=lambda: onClick((fontFrame.face, fontFrame.size)))
#    btnOk.pack(side=RIGHT)    
#            
#    fontFrame = FontFrame(win)
#    fontFrame.pack()
#    
#    win.focus_set()
#    win.grab_set()
#    win.wait_window()
#    return retval[0]
    
    

#class GUIConsumer(object):                    
#    def __init__(self, producer, timer):
#        if not callable(producer):
#            raise TypeError('producer should be a callable object.')
#        self.__producer = producer           
#        
#        if not isinstance(timer, BaseObservableTimer):
#            raise TypeError('timer should be an instance of a derived class of BaseObservableTimer')
#        self.__active = False
#        self.__timer = timer
#        self.__timer.add_observer(SimpleObserver(self._on_tick))
#        self.__queue = Queue.Queue()
#        self.__producerThread = None        
#        
#    def _on_tick(self):
#        try:
#            while True:
#                data = self.__queue.get_nowait()
#                if self.__active is True:
#                    self.consume(data)
#        except Queue.Empty:
#            pass
#        
#    def _run_producer(self):
#        producer = self.__producer
#        while True:
#            self.__queue.put(producer())
#        
#    def consume(self, data):
#        return NotImplemented
#        
#    @property
#    def active(self):
#        return self.__active
#        
#    @active.setter
#    def active(self, val):
#        self.__active = val
#        if self.__active is True and self.__producerThread is None:
#            self.__producerThread = thread.start_new_thread(self._run_producer)
            

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
    
    def complex_create_circle(self, radius, center=None, **options):
        if center is None:
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
            
            iq.canvas.itemconfig(self.__iq_text, text=f' I:{int(i_magnitude)}, Q:{int(q_magnitude)} ')            
            iq.canvas.coords(self.__iq_text, pos.real, pos.imag)
            
            iq.canvas.itemconfig(self.__textPolar, text=f' A:{int(abs(i_magnitude+1j*q_magnitude))}, ϕ:{int(360*math.atan2(q_magnitude, i_magnitude)/2/math.pi)}° ')                        
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
        


def json_to_tk(parent, json_code, balloon=None):
    '''\
Example: [
    {"name":"alert_button", "class":"Button", "module":"ttk", 
    "config":{"text":"Alert!"}, "pack":{"fill":"x"}}
]
    '''
    import tkinter as tk
    import tkinter.ttk as ttk
    
    if isinstance(json_code, str):
        json_obj = json.loads(json_code)
    else:
        json_obj = json_code
    retval = {}

    for item in json_obj:
#        try:
#            class_name = item.get('class')
#        except KeyError:
#            class_name = item.get('class_')
            
        if 'class' in item:
            class_name = item['class']
        else:
            class_name = item['class_']

        mod = item.get('module', None)
        if mod:
            mod = locals()[mod]
            cls = getattr(mod, class_name)            
        else:
            if isinstance(class_name, type):
                cls = class_name
            elif class_name in globals():
                cls = globals()[class_name]
            elif class_name in ttk.__dict__:
                cls = ttk.__dict__[class_name]
            else:
                cls = tk.__dict__[class_name]
        
        widget = cls(parent, **item.get('config', {}))
        if 'grid' in item:
            widget.grid(**item.get('grid', {}))        
        else:
            widget.pack(**item.get('pack', {}))
        
        if 'balloonmsg' in item and balloon is not None:
            balloon.bind_widget(widget, balloonmsg=item.get('balloonmsg'))
        
        if 'children' in item:
            sub_widgets = json_to_tk(widget, item.get('children'), balloon=balloon)
            for sub_widget in sub_widgets:
                if sub_widget in retval:
                    raise ValueError('Multiple widgets have a same name.')
                retval[sub_widget] = sub_widgets[sub_widget]
        if 'setattr' in item:
            attr_map = item.get('setattr')
            for attr_name in attr_map:
                setattr(widget, attr_name, attr_map[attr_name])
        if 'name' in item:
            retval[item.get('name')] = widget
    return retval

        
if __name__ == '__main__':
#    window  = Tk()
#    tree    = ScrolledTree(window)
#    root    = tree.insert('', 'end', text='root')
#    node    = tree.insert(root, END, text='node')
#    window.mainloop()

    #    window = Tk()
    #    print (ask_font())
    #    window.mainloop()

#    root    = Tk()
#    iq      = IQSlider(root, i_range=512, q_range=512, relief='raised')
#    iq.pack(expand='yes', fill='both')
#    root.mainloop()

    root = Tk()
    json_code = '''[
    {"name":"alert_button", "class":"Button", "config":{"text":"Alert!"}, "pack":{"fill":"x"}}
]
    '''
    widgets = json_to_tk(root, json_code)
    widgets['alert_button']['command'] = lambda: print('Alert!')
    root.mainloop()
    
#    root = tix.Tk()
#    cl = CheckTree(root)
#    cl.pack(expand='yes', fill='both')
#    n1 = cl.add(text='root node')
#    for k in range(32):
#        child = cl.add(parent_node=n1, text='child'+str(k))
#    print(cl.tree_model)
#    root.mainloop()
