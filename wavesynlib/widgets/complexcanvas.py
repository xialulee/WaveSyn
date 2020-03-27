from tkinter import Canvas



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