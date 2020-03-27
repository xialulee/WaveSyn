import ctypes as ct
from win32con import GWL_EXSTYLE, WS_EX_LAYERED, LWA_ALPHA

GetParent = ct.windll.user32.GetParent
SetWindowLongA = ct.windll.user32.SetWindowLongA
SetLayeredWindowAttributes = ct.windll.user32.SetLayeredWindowAttributes

                                    
class Transparenter(object):
    def __init__(self, tk_window):
        self._tk_object = tk_window
        self._handle = None
        
    def _get_window_handle(self):
        if self._handle is None:
            self._handle = GetParent(self._tk_object.winfo_id())
        SetWindowLongA(self._handle, GWL_EXSTYLE, WS_EX_LAYERED)
        return self._handle
        
    def set_opacity(self, opacity):
        opacity = ct.c_ubyte(opacity)
        handle = self._get_window_handle()
        SetLayeredWindowAttributes(handle, 0, opacity, LWA_ALPHA)
