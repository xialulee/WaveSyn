# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 19:12:09 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import platform
import re

from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode
from wavesynlib.languagecenter.utils import eval_format


class TkClipboard(ModelNode):
    def __init__(self, *args, **kwargs):
        super(TkClipboard, self).__init__(*args, **kwargs)
       
    @Scripting.printable
    def clear(self):
        self.root_node.root.clipboard_clear()
    
    @Scripting.printable
    def write(self, content):
        self.clear()
        self.root_node.root.clipboard_append(content)
        
    @Scripting.printable
    def read(self):
        return self.root_node.root.clipboard_get()
        
    @Scripting.printable
    def remove_text_formatting(self):
        content = self.read()
        self.write(content)
        
    @Scripting.printable
    def remove_newlines(self, insert_blanks=True):
        text = self.read()
        if insert_blanks:
            text = re.sub(r'(?<=[^- ])\n', ' \n', text)
            text = re.sub(r'-?\n', '', text)
        else:
            text = text.replace('\n', '')
        self.write(text)


if platform.system().lower() == 'windows':
    from cStringIO import StringIO
    from wavesynlib.interfaces.os.windows.clipboard import clipb
    class Clipboard(TkClipboard):
        @Scripting.printable
        def write(self, content, fmt=None, code=None):
            if (not fmt) and (not code) :
                super(Clipboard, self).write(content)
            else:
                stream  = StringIO()
                stream.write(content)
                stream.seek(0)
                clipb.stream_to_clipboard(stream, fmt, code, None, None)
                
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
            import win32clipboard as cw
            
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

else: # Use Tk clipboard. TkClipboard is inferior to Clipboard. However, it is cross-platform.
    Clipboard   = TkClipboard  
    
    
try:
    import psutil
    def _get_mem_percent():
        return psutil.virtual_memory().percent
except ImportError:
    _get_mem_percent = None


class OperatingSystem(ModelNode):
    def _not_implemented(*args, **kwargs):
        raise NotImplementedError
    
    _sys_name = platform.system().lower()        
    _obj_map = {'winopen':'wavesynlib.interfaces.os.{_sys_name}.shell.winopen', 
                'get_memory_usage':'wavesynlib.interfaces.os.{_sys_name}.memstatus'}
    
    for name in _obj_map:
        try:
            __mod = __import__(eval_format(_obj_map[name]), globals(), locals(), [name], -1)
            _obj_map[name] = getattr(__mod, name)
        except ImportError:
            _obj_map[name] = _not_implemented
            
    
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        with self.attribute_lock:
            self.clipboard = Clipboard()
            
    
    @Scripting.printable    
    def win_open(self, path):
        func = self._obj_map['winopen']
        return func(path)
        
        
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