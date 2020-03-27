from tkinter import Frame
from tkinter.ttk import Button, Scale, Label
from tkinter.filedialog import asksaveasfilename

import platform
from pathlib import Path

import PIL
from PIL import ImageTk
from PIL import Image



class PILImageFrame(Frame):
    def __init__(self, *args, **kwargs):
        pil_image = kwargs.pop('pil_image')
        balloon = None
        if 'balloon' in kwargs:
            balloon = kwargs.pop('balloon')
        photo = ImageTk.PhotoImage(pil_image)
        self.__photo = photo
        self.__origin_image = pil_image
        self.__zoomed_image = pil_image
        super().__init__(*args, **kwargs)
        
        self.__icons = icons = {}
        image_dir = Path(__file__).parent / 'images'

        for name in ('save', 'savezoom', 'copy'):
            icon_path = image_dir / (name+'.png')
            icon = ImageTk.PhotoImage(file=str(icon_path))
            icons[name] = icon

        frame = Frame(self)
        frame.pack(fill='x')
        
        save_dlg = lambda: asksaveasfilename(filetypes=[
                ('JPEG', '.jpg'), ('PNG', '.png')], 
            defaultextension='.jpg')        
                        
        def on_save(image):
            filename = save_dlg()
            if filename:
                image.save(filename)
        
        Label(frame, text=f'id={id(self)}').pack(side='left')
        save_btn = Button(frame, 
               image=icons['save'], 
               command=lambda:on_save(self.__origin_image))
        save_btn.pack(side='left')
        if balloon:
            balloon.bind_widget(save_btn, balloonmsg='Save image.')
        
        savezoom_btn = Button(frame, 
               image=icons['savezoom'], 
               command=lambda:on_save(self.__zoomed_image))
        savezoom_btn.pack(side='left')
        if balloon:
            balloon.bind_widget(savezoom_btn, balloonmsg='Save zoomed image.')
        
        if platform.system().lower() == 'windows':
            from wavesynlib.interfaces.os.windows.clipboard import clipb
            
            def on_copy():
                clipb.image_to_clipboard(self.__origin_image)
            copy_btn = Button(frame, image=icons['copy'], command=on_copy)
            copy_btn.pack(side='left')
            if balloon:
                balloon.bind_widget(copy_btn, balloonmsg='Copy image.')

        scale = Scale(frame, from_=0, to=100, orient='horizontal', value=100)
        scale.pack(side='left')
        zoomed_label = Label(frame, text='100%')
        zoomed_label.pack(side='left')
        
        self.__label = label = Label(self, image=photo)
        label.pack(expand='yes', fill='both')
        
        def on_scale(val):
            val = float(val)
            width, height = self.__origin_image.size
            width = int(width * val / 100)
            height = int(height * val / 100)
            if width<=0 or height<=0:
                return
            zoomed_image = self.__origin_image.resize((width, height), 
                                                      Image.ANTIALIAS)
            self.__zoomed_image = zoomed_image
            self.__photo = ImageTk.PhotoImage(zoomed_image)
            self.__label['image'] = self.__photo
            zoomed_label['text'] = f'{int(val)}%'
            
        scale['command'] = on_scale
