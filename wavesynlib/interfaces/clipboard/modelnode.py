# -*- coding: utf-8 -*-
"""
Created on Fri Jan 01 18:41:20 2016

@author: Feng-cong Li
"""

import platform

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting


class TkClipboard(ModelNode):
    def __init__(self, *args, **kwargs):
        super(TkClipboard, self).__init__(*args, **kwargs)
       
    @Scripting.printable
    def clear(self):
        self.root_node.root.clipboard_clear()
    
    @Scripting.printable
    def write(self, content):
        self.root_node.root.clipboard_append(content)
        
    @Scripting.printable
    def read(self):
        return self.root_node.root.clipboard_get() 


if platform.system().lower() == 'windows':
    from cStringIO                               import StringIO
    from wavesynlib.interfaces.windows.clipboard import clipb
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
            import qrcode
            string  = self.read()
            image   = qrcode.make(string)
            self.root_node.print_tip([{'type':'pil_image', 'content':image},
                                      {'type':'text', 'content':'The QR code of the text stored by clipboard is shown above.'}])
            
        @Scripting.printable
        def to_console_image(self):
            from PIL import ImageGrab
            image = ImageGrab.grabclipboard()
            if image:
                self.root_node.print_tip([{'type':'pil_image', 'content':image},
                                          {'type':'text', 'content':'Image in clipboard is shown above.'}])
            else:
                raise TypeError('Data in clipboard is not an image.')

else: # Use Tk clipboard. TkClipboard is inferior to Clipboard. However, it is cross-platform.
    Clipboard   = TkClipboard   