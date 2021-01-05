import tkinter
from tkinter.ttk import Button
from typing import Any

from wavesynlib.languagecenter.designpatterns import SimpleObserver
from wavesynlib.languagecenter.datatypes import CommandObject



class WSButton(Button):
    def __init__(self, *args, **kwargs):
        command_object = kwargs.pop("command_object", None)
        super().__init__(*args, **kwargs)
        if command_object:
            self["command_object"] = command_object


    def __setitem__(self, key: str, value: Any) -> None:
        if key == "command_object":
            command_object = value
            self.__command_object = command_object

            def on_can_execute_change(event):
                if event == "can_execute_changed":
                    if command_object.can_execute():
                        state = "normal"
                    else:
                        state = "disabled"
                    self["state"] = state
            
            on_can_execute_change("can_execute_changed")
            command_observer = SimpleObserver(on_can_execute_change)
            command_object.add_observer(command_observer)
            self["command"] = command_object
            return
        return super().__setitem__(key, value)


    def config(self, **kwargs):
        command_object = kwargs.pop("command_object", None)
        if command_object:
            self["command_object"] = command_object
        return super().config(**kwargs)



if __name__ == "__main__":
    root = tkinter.Tk()
    tkinter.Label(root, text="You cannot quit until input something.").pack()
    entry_text = tkinter.StringVar("")
    (entry := tkinter.Entry(root, textvariable=entry_text)).pack()
    command_object = CommandObject(root.destroy, lambda: entry_text.get() != "")
    entry_text.trace("w", lambda *args: command_object.change_can_execute())
    (button := WSButton(root, text="Quit", command_object=None)).pack()
    button.config(command_object=command_object)
    root.mainloop()