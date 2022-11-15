from pathlib import Path
import tkinter
from tkinter.ttk import Button
from PIL import ImageTk
from typing import Any
from wavesynlib.languagecenter.datatypes import CommandObject
from .utils.loadicon import load_icon


class WSButton(Button):
    def __init__(self, *args, **kwargs):
        icon = kwargs.pop('image', None)
        if icon:
            if isinstance(icon, (Path, str)):
                icon = load_icon(icon, common=True)
            kwargs['image'] = icon
        self.__icon = icon
        command_object = kwargs.pop('command_object', None)
        super().__init__(*args, **kwargs)
        if command_object:
            self['command_object'] = command_object
    
    @property
    def common_icon(self):
        return self.__icon
    
    @common_icon.setter
    def common_icon(self, icon):
        self.__icon = load_icon(icon, common=True)
        self["image"] = self.__icon

    def __setitem__(self, key: str, value: Any) -> None:
        if key == 'command_object':
            command_object = value
            self.__command_object = command_object

            def on_can_execute_change(event):
                if event.name == 'can_execute_changed':
                    try:
                        self['state'] = \
                            'normal' if event.sender.can_execute() else 'disabled'
                    except tkinter.TclError:
                        pass
            command_object.add_observer(on_can_execute_change)
            command_object.change_can_execute()
            self['command'] = command_object
        else:
            super().__setitem__(key, value)
            
    def config(self, **kwargs):
        command_object = kwargs.pop("command_object", None)
        if command_object:
            self["command_object"] = command_object
        super().config(**kwargs)
        

if __name__ == "__main__":
    root = tkinter.Tk()
    tkinter.Label(root, text="You cannot quit until input something.").pack()
    entry_text = tkinter.StringVar("")
    (entry := tkinter.Entry(root, textvariable=entry_text)).pack()
    command_object = CommandObject(root.destroy, lambda: entry_text.get() != "")
    entry_text.trace("w", lambda *args: command_object.change_can_execute())
    (button := WSButton(root, text="Quit", command_object=command_object)).pack()
    root.mainloop()
