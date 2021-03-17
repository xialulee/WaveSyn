import hy
from wavesynlib.interfaces.os.windows.inputhook.keyboardhook import KeyboardHook

from tkinter import Tk
import tkinter.messagebox as msgbox
import sys
from win32con import VK_CAPITAL, VK_ESCAPE



if __name__ == "__main__":
    khook = KeyboardHook()
    khook.unhook_at_exit()
    khook.add_key_to_key(old_key=VK_CAPITAL, new_key=VK_ESCAPE)
    try:
        khook.hook()
    except OSError:
        msgbox.showerror("Error", "Failed to setup a global keyboard hook.")
        sys.exit(1)
    root = Tk()
    root.mainloop()
