from __future__ import annotations

from tkinter import Tk
from queue import Empty

from quantities import second as sec
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.widgets.tk.desctotk import json_to_tk
from .widgets import main_panel


def main(messages_from_interrupter, messages_to_interrupter):
    root = Tk()
    root.title('WaveSyn-Interrupter')
    root.protocol('WM_DELETE_WINDOW', lambda : None)
    root.wm_attributes('-topmost', True)
    widgets_desc = [main_panel]
    widgets = json_to_tk(root, widgets_desc)

    widgets["abort_btn"]["command"] = lambda: \
        messages_from_interrupter.put({
            "type":    "command",
            "command": "interrupt_main_thread",
            "args":    ""
        })

    queue_monitor = TkTimer(root, interval = 0.25*sec)

    @queue_monitor.add_observer
    def queue_observer(event):
        try:
            message = messages_to_interrupter.get_nowait()
        except Empty:
            return
        if message['type'] == 'command' and message['command'] == 'exit':
            root.deiconify()
            root.destroy()
    queue_monitor.active = True
    root.iconify()
    root.mainloop()
