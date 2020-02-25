from wavesynlib.interfaces.os.windows.shell.taskbarmanager.definitions \
    import ITaskbarList4, GUID_CTaskbarList
from wavesynlib.interfaces.os.windows.shell.constants import TBPFLAG
from comtypes import CoCreateInstance
import ctypes as ct

GetParent = ct.windll.user32.GetParent

class TaskbarIcon:
    def __init__(self, root):
        self.__tbm  = CoCreateInstance(GUID_CTaskbarList, 
                                        interface=ITaskbarList4)
        self.__root = root

    @property
    def progress(self):
        '''Not implemented'''
        pass

    @progress.setter
    def progress(self, value):
        self.__tbm.SetProgressValue(GetParent(self.__root.winfo_id()), 
                                    int(value), 100)

    @property
    def state(self):
        '''Not Implemented'''
        pass

    @state.setter
    def state(self, state):
        self.__tbm.SetProgressState(GetParent(self.__root.winfo_id()), 
                                    state)



if __name__ == '__main__':
    from tkinter import Tk
    from tkinter.ttk import Scale, Combobox

    root = Tk()
    icon = TaskbarIcon(root)

    def on_combo_change(event):
        text = event.widget.get()
        icon.state = getattr(TBPFLAG, f"TBPF_{text}")

    combo = Combobox(
        root, 
        value=["NORMAL", "PAUSED", "ERROR"],
        stat="readonly")
    combo.bind("<<ComboboxSelected>>", on_combo_change)
    combo.current(0)
    combo.pack()

    def on_scale(value):
        value = int(float(value))
        icon.progress = value

    scale = Scale(
        root, 
        from_=0, to=100, value=0, 
        command=on_scale)
    scale.pack(fill="x")

    root.mainloop()