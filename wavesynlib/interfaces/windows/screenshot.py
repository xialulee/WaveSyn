# 2015 July 1
# xialulee

from Tkinter import *
from os import path
from wavesynlib.languagecenter.designpatterns import Observable
from tkFileDialog import asksaveasfilename
from PIL import ImageGrab
from PIL.ImageTk import PhotoImage


class RectSelCanvas(Canvas, Observable):
    def __init__(self, master=None, cnf={}, **kw):
        Canvas.__init__(self, master, cnf, **kw)
        Observable.__init__(self)
        self.__boxId    = None
        self.__startX   = None
        self.__startY   = None
        
        self.bind('<Button-1>', self.onButton1Press)
        self.bind('<B1-Motion>', self.onMouseMove)
        self.bind('<ButtonRelease-1>', self.onButton1Release)
        
    def onButton1Press(self, event):
        self.__boxId    = self.create_rectangle(
            event.x, event.y, event.x, event.y
        )
        self.__startX   = event.x
        self.__startY   = event.y
        
    def onMouseMove(self, event):
        self.coords(self.__boxId, self.__startX, self.__startY, event.x, event.y)
    
    def onButton1Release(self, event):
        self.delete(self.__boxId)
        self.notify_observers(self.__startX, self.__startY, event.x, event.y)
        self.__startX   = None
        self.__startY   = None


if __name__ == '__main__':
    root    = Tk()
    
    canvas  = RectSelCanvas(root, cursor='crosshair')
    canvas.pack(fill=BOTH, expand=YES)    
    
    image           = ImageGrab.grab()
    photoImage      = PhotoImage(image)
    canvas['borderwidth']   = 0
    canvas.create_image((0, 0), anchor=NW, image=photoImage)   
    
    class Observer(object):
        def __init__(self, root, image):
            self.__image    = image
            self.__root     = root
        
        def update(self, *box):
            cropImage   = self.__image.crop(box)
            filename = asksaveasfilename(defaultextension='.png', filetypes=[('PNG Image', '*.png'), ('JPEG Image', '*.jpg')])
            if filename != '':
                cropImage.save(filename)
            root.quit()
            
    canvas.add_observer(Observer(root, image))
    
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (
        root.winfo_screenwidth(), root.winfo_screenheight()
    ))    
    
    root.mainloop()
