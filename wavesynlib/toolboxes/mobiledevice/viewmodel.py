from tkinter import IntVar, BooleanVar
from wavesynlib.languagecenter.datatypes import CommandObject
from wavesynlib.languagecenter.wavesynscript import code_printer



class ViewModel:
    def __init__(self, window):
        self.transfer_progress = IntVar()
        self.idle = BooleanVar()
        self.idle.set(True)

        @CommandObject
        def read_clipb():
            with code_printer():
                window.read_device_clipboard(on_finish=None)
        read_clipb.bind_tkvar(self.idle)
        self.read_clipb = read_clipb

        @CommandObject
        def write_clipb():
            with code_printer():
                window.write_device_clipboard()
        write_clipb.bind_tkvar(self.idle)
        self.write_clipb = write_clipb
