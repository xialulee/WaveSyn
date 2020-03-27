from tkinter import Canvas, Frame
from tkinter.ttk import Scrollbar



class ScrolledCanvas(Frame):
    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)
        canvas = Canvas(self)        
        
        xbar = Scrollbar(self, orient='horizontal')
        xbar.config(command=canvas.xview)
        canvas.config(xscrollcommand=xbar.set)
        xbar.pack(side='bottom', fill='x')
        
        ybar = Scrollbar(self)
        ybar.config(command=canvas.yview)
        canvas.config(yscrollcommand=ybar.set)
        ybar.pack(side='right', fill='y')
        
        canvas.pack(expand='yes', fill='both')
        
        self.__canvas = canvas

    @property
    def canvas(self):
        return self.__canvas               
