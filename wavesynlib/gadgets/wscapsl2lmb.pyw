from wavesynlib.interfaces.os.windows.inputhook.keyboardhook import KeyboardHook

from tkinter import Tk
import tkinter.messagebox as msgbox
import sys
from win32con import VK_CAPITAL



if __name__ == "__main__":
    khook = KeyboardHook()
    khook.unhook_at_exit()
    khook.add_key_to_mouse(key=VK_CAPITAL, mouse_btn="left")
    try:
        khook.hook()
    except OSError:
        msgbox.showerror("Error", "Failed to setup a global keyboard hook.")
        sys.exit(1)
    root = Tk()
    root.mainloop()
