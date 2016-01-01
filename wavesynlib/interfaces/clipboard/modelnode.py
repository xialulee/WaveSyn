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
        self.rootNode.root.clipboard_clear()
    
    @Scripting.printable
    def write(self, content):
        self.rootNode.root.clipboard_append(content)
        
    @Scripting.printable
    def read(self):
        return self.rootNode.root.clipboard_get() 


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
                clipb.stream2clipb(stream, fmt, code, None, None)
else: # Use Tk clipboard, which is cross-platform.
    Clipboard   = TkClipboard   