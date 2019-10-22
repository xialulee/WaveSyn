# 2015 July 1
# xialulee

from tkinter import Canvas, Tk
from wavesynlib.languagecenter.designpatterns import Observable
from tkinter.filedialog import asksaveasfilename
from PIL import ImageGrab
from PIL.ImageTk import PhotoImage


class RectSelCanvas(Canvas, Observable):
    def __init__(self, master=None, cnf={}, **kw):
        Canvas.__init__(self, master, cnf, **kw)
        Observable.__init__(self)
        self.__boxId    = None
        self.__start_x   = None
        self.__start_y   = None
        
        self.bind('<Button-1>', self.onButton1Press)
        self.bind('<B1-Motion>', self.onMouseMove)
        self.bind('<ButtonRelease-1>', self.onButton1Release)
        
        
    def onButton1Press(self, event):
        self.__boxId    = self.create_rectangle(
            event.x, event.y, event.x, event.y
        )
        self.__start_x   = event.x
        self.__start_y   = event.y
        
        
    def onMouseMove(self, event):
        self.coords(self.__boxId, self.__start_x, self.__start_y, event.x, event.y)
        
    
    def onButton1Release(self, event):
        self.delete(self.__boxId)
        self.notify_observers(self.__start_x, self.__start_y, event.x, event.y)
        self.__start_x   = None
        self.__start_y   = None
        


if __name__ == '__main__':
    root    = Tk()
    
    canvas  = RectSelCanvas(root, cursor='crosshair')
    canvas.pack(fill='both', expand='yes')
    
    image           = ImageGrab.grab()
    photoImage      = PhotoImage(image)
    canvas['borderwidth']   = 0
    canvas.create_image((0, 0), anchor='nw', image=photoImage)   
    
    class Observer:
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
