from wavesynlib.widgets.tk import ScrolledText
from wavesynlib.languagecenter.wavesynscript import Scripting, WaveSynScriptAPI
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow

class DocWindow(TkToolWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tk_object.title('Document')
        self._make_window_manager_tab()
        self.__scrolledtext = stext = ScrolledText(self.tk_object)      
        stext.pack(expand='yes', fill='both')
        self.__visible = True
        
        @Scripting.root_node.gui.console.console_text.encounter_func_callback.add_function
        def on_encounter_func(cs):
            if cs and self.visible:
                self.text = str(cs[0].docstring())
            self.root_node.gui.console.console_text.text.focus_set()        
        
        
    @property
    def text(self):
        return self.__scrolledtext.get_text()
    
    
    @text.setter
    def text(self, content):
        self.__scrolledtext.set_text(content)
        
        
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
