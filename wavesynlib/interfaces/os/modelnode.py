# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 19:12:09 2016

@author: Feng-cong Li
"""
import os
import platform
import ctypes
import re
from importlib import import_module
import webbrowser

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode, constant_handler



class TkClipboard(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
       
    @Scripting.printable
    def clear(self):
        '''Clear the clipboard.'''
        self.root_node.gui.root.clipboard_clear()
        
    
    @Scripting.printable
    def write(self, content):
        '''Put a string into the clipboard.
        
content: A string which will be put into the clipbaord.'''
        self.clear()
        self.root_node.gui.root.clipboard_append(content)
        
        
    @Scripting.printable
    def read(self):
        '''Read a string from the clipboard if the content of the clipboard is text.'''
        return self.root_node.gui.root.clipboard_get()
    
        
    @Scripting.printable
    def remove_text_formatting(self):
        content = self.read()
        self.write(content)
    
    
    @Scripting.printable
    def remove_newlines(self, insert_blanks=True):
        '''Delete the new lines or replace the new lines with blanks.

insert_blanks: Delete the new lines if False else replace the new lines with blanks.
    Default: True.'''
        text = self.read()
        if insert_blanks:
            text = re.sub(r'(?<=[^- ])\n', ' \n', text)
            text = re.sub(r'-?\n', '', text)
        else:
            text = text.replace('\n', '')
        self.write(text)
        

        
class TkMouse(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @Scripting.printable
    def get_x(self):
        return self.root_node.gui.root.winfo_pointerx()
        
    
    @Scripting.printable
    def get_y(self):
        return self.root_node.gui.root.winfo_pointery()
        
    
    
if platform.system().lower() == 'windows':
    from six.moves import cStringIO as StringIO
    from wavesynlib.interfaces.os.windows.clipboard import clipb
    import win32clipboard as cw  
    import win32con
    
    class Clipboard(TkClipboard):
        @constant_handler(print_replacement=False)
        def get_clipboard_html(self, arg, **kwargs):
            return self.read(html=True)
            
            
        @constant_handler(print_replacement=False)
        def get_clipboard_image(self, arg, **kwargs):
            from PIL import ImageGrab
            image = ImageGrab.grabclipboard()
            if not image:
                raise TypeError('The data in clipboard is not an image.')
            return image
            
        
        @Scripting.printable
        def write(self, content, html=None, table=None, code=None):
            if table:
                from wavesynlib.languagecenter.html.utils import iterable_to_table
                html = True
                content = iterable_to_table(content)          
            if (not html) and (not code) :
                super().write(content)
            else:
                stream = StringIO()
                stream.write(content)
                stream.seek(0)                    
                clipb.stream_to_clipboard(stream, mode=None, code=code, tee=None, null=None, html=html)
                
                
        @Scripting.printable
        def read(self, html=None, code=None):
            if (not html) and (not code):
                return super().read()
            else:
                stream = StringIO()
                clipb.clipboard_to_stream(stream, mode=None, code=code, null=None, html=html)
                stream.seek(0)
                return stream.read()
                
            
        @Scripting.printable
        def to_console_qr(self):
            try:
                import qrcode
            except ImportError:
                self.root_node.print_tip([{'type':'text', 'content':'This functionality depends on qrcode. Please use "pip install qrcode" to install it.'}])
            string  = self.read()
            image   = qrcode.make(string)
            self.root_node.print_tip([{'type':'pil_image', 'content':image},
                                      {'type':'text', 'content':'The QR code of the text stored by clipboard is shown above.'}])
            
    
        @Scripting.printable
        def to_console_image(self):
            from PIL import ImageGrab
            image = ImageGrab.grabclipboard()
            if image:
                return_list = self.root_node.print_tip([{'type':'pil_image', 'content':image},
                                                        {'type':'text', 'content':'Image in clipboard is shown above.'}])
                return return_list[0]
            else:
                raise TypeError('Data in clipboard is not an image.')
                
                
        @Scripting.printable
        def to_console_file_list(self):
            self.root_node.print_tip([{'type':'text', 'content':'The files in clipboard are listed as follows:'},
                                      {'type':'file_list', 'content':clipb.get_clipboard_file_list()}])
                
                
        @Scripting.printable
        def to_console(self):            
            def for_text():
                self.root_node.print_tip([{'type':'text', 'content':'\n'.join(('The text in clipboard is listed as follows', self.read()))}])
                
            def for_image():
                return self.to_console_image()
                
            def for_file_list():
                self.to_console_file_list()             
                
            def for_unknown_type():
                raise NotImplementedError("The format of the clipboard's content is not supported.")
                            
            func_map = {
                cw.CF_TEXT: for_text,
                cw.CF_UNICODETEXT: for_text,
                cw.CF_BITMAP: for_image,
                cw.CF_HDROP: for_file_list
            }   

            format_code = cw.GetPriorityClipboardFormat([cw.CF_TEXT, cw.CF_UNICODETEXT, cw.CF_BITMAP, cw.CF_HDROP])
            return func_map.get(format_code, for_unknown_type)()             
            
            
        @Scripting.printable
        def convert_file_to_image(self):
            path = clipb.get_clipboard_file_list()[0]
            ext = os.path.splitext(path)[-1]
            is_psd = ext=='.psd' 
            with open(path, 'rb') as file_obj:
                clipb.image_file_to_clipboard(file_obj, is_psd)
                
    
            
    class Mouse(TkMouse): 
        _const_map = {
            'left_button_down':     win32con.MOUSEEVENTF_LEFTDOWN,
            'left_button_up':       win32con.MOUSEEVENTF_LEFTUP,
            'right_button_down':    win32con.MOUSEEVENTF_RIGHTDOWN,
            'right_button_up':      win32con.MOUSEEVENTF_RIGHTUP,
            'middle_button_down':   win32con.MOUSEEVENTF_MIDDLEDOWN,
            'middle_button_up':     win32con.MOUSEEVENTF_MIDDLEUP
        }

              
        @Scripting.printable
        def set_x(self, x):
            x = self.root_node.gui.dialogs.ask_integer(
                x, 
                title='Set Mouse Cursor Position', 
                prompt='Please input x-coordinate:')
            y = self.get_y()
            ctypes.windll.user32.SetCursorPos(x, y)

            
        @Scripting.printable
        def set_y(self, y):
            x = self.get_x()
            y = self.root_node.gui.dialogs.ask_integer(
                y, 
                title='Set Mouse Cursor Position',
                prompt='Please input y-coordinate:')
            ctypes.windll.user32.SetCursorPos(x, y)

            
        @Scripting.printable
        def click(self, button='left'):
            button = button.upper()
            for action in ('DOWN', 'UP'):
                const = getattr(win32con, 'MOUSEEVENTF_{}{}'.format(button, action))
                ctypes.windll.user32.mouse_event(const, 0, 0, 0, 0)
                
                
        #To Do: Keyboard class. Use keybd_event.
                
           
    from comtypes import CoCreateInstance
    from wavesynlib.interfaces.os.windows.shell import desktopwallpaper           
           
    class DesktopWallpaper(ModelNode):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.__idw = CoCreateInstance(
                desktopwallpaper.CLSID_DesktopWallpaper,
                interface=desktopwallpaper.IDesktopWallpaper
            )
            
            
        def set(self, path, monitor_id=None):
            self.__idw.SetWallpaper(monitor_id, path)
            
            
        def get(self, monitor_id=None):
            return self.__idw.GetWallpaper(monitor_id)
            
        
        @property
        def position(self):
            return self.__idw.GetPosition()
            
            
        @position.setter
        def position(self, val):
            self.__idw.SetPosition(val)
            
            
else: 
# Use Tk clipboard. TkClipboard is inferior to Clipboard. However, it is cross-platform.    
    Clipboard = TkClipboard  
    Mouse = TkMouse
    
    class DesktopWallpaper(ModelNode):
        pass    
    
    
try:
    import psutil
    def _get_mem_percent():
        return psutil.virtual_memory().percent
        
    def _get_cpu_percent():
        return psutil.cpu_percent()
except ImportError:
    _get_mem_percent = None
    _get_cpu_percent = None



class OperatingSystem(ModelNode):
    def _not_implemented(*args, **kwargs):
        raise NotImplementedError
    
    _sys_name = platform.system().lower()        
    _obj_map = {'winopen': f'wavesynlib.interfaces.os.{_sys_name}.shell.winopen', 
                'get_memory_usage': f'wavesynlib.interfaces.os.{_sys_name}.memstatus'}
    
    for name in _obj_map:
        try:
            __mod = import_module(_obj_map[name])
            _obj_map[name] = getattr(__mod, name)
        except ImportError:
            _obj_map[name] = _not_implemented
            
    
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        self.clipboard = ModelNode(is_lazy=True, class_object=Clipboard)
        self.mouse = ModelNode(is_lazy=True, class_object=Mouse)
        self.desktop_wallpaper = ModelNode(is_lazy=True, class_object=DesktopWallpaper)
        
        if platform.system().lower() == 'windows':
            from wavesynlib.interfaces.os.windows.modelnode import Windows
            self.windows = ModelNode(is_lazy=True, class_object=Windows)
            
    
    @Scripting.printable    
    def win_open(self, path):
        func = self._obj_map['winopen']
        return func(path)
    
    
    @Scripting.printable
    def chdir(self, directory):
        os.chdir(directory)
        
        
    @Scripting.printable
    def map_open(self, latitude, longitude):
        uri = f'bingmaps:?collection=point.{latitude}_{longitude}_Pin'
        webbrowser.open(uri)
        
        
    if _get_mem_percent is None:
        @Scripting.printable
        def get_memory_usage(self):
            func = self._obj_map['get_memory_usage']
            try:
                return func()
            except NotImplementedError:
                return 0
    else:
        @Scripting.printable
        def get_memory_usage(self):
            return int(_get_mem_percent())
            
            
    if _get_cpu_percent is None:
        @Scripting.printable
        def get_cpu_usage(self):
            return 0
    else:
        @Scripting.printable
        def get_cpu_usage(self):
            return int(_get_cpu_percent())            