import math
import cmath
from tkinter import Frame, Tk
from tkinter.ttk import Scale

from wavesynlib.languagecenter.designpatterns import Observable
from .complexcanvas import ComplexCanvas



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



if __name__ == "__main__":
    root    = Tk()
    iq      = IQSlider(root, i_range=512, q_range=512, relief='raised')
    iq.pack(expand='yes', fill='both')
    root.mainloop()