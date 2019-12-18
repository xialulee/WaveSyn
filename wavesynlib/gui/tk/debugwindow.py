from io import StringIO

from wavesynlib.widgets.tk import ScrolledText
from wavesynlib.languagecenter.wavesynscript import Scripting, WaveSynScriptAPI
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow



class DebugWindow(TkToolWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tk_object.title('Debug')
        self._make_window_manager_tab()
        self.__scrolledtext = stext = ScrolledText(self.tk_object)
        stext.pack(expand='yes', fill='both')
        self.__visible = True
        
        
    def print(self, *args, **kwargs):
        sio = StringIO()
        kwargs['file'] = sio
        print(*args, **kwargs)
        content = sio.getvalue()
        self.__scrolledtext.append_text(content)
        self.tk_object.update()
            
            
    def _close_callback(self):
        self.tk_object.withdraw()
        self.__visible = False
        return True
        
        
    @property
    def visible(self):
        return self.__visible
    
    
    @WaveSynScriptAPI
    def show_window(self):
        self.tk_object.update()
        self.tk_object.deiconify()
        self.__visible = True