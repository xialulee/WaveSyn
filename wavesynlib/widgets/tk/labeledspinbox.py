from tkinter import Frame, Spinbox, Toplevel, Entry, Button, StringVar
from tkinter.ttk import Label
from .utils.loadicon import load_icon

from wavesynlib.languagecenter.designpatterns import Observable


class LabeledSpinbox(Frame, Observable):

    def __init__(self, *args, **kwargs):
        from_ = kwargs.pop("from_", 0)
        to = kwargs.pop("to", 100)
        # super().__init__(*args, **kwargs)
        Frame.__init__(self, *args, **kwargs)
        Observable.__init__(self)
        (label := Label(self)).pack(side="left")
        self.__label = label
        self.__spin_var = StringVar()
        (spinbox := Spinbox(
            self, from_=from_, to=to, 
            textvariable=self.__spin_var,
            command=self.__on_command
        )).pack(side="left", fill="x", expand="yes")
        self.__spinbox = spinbox
        (button := Button(self, text="\u2699", command=self.__open_increment_dialog)).pack(side="right")
        self.__button = button
        self.__image = None
        self.__spin_var.trace_add('write', self.__on_value_change)

    def __on_value_change(self, *args):
        self.notify_observers("value change", self.spinbox_value)

    def __on_command(self, *args):
        self.notify_observers("command", self.spinbox_value)

    def __open_increment_dialog(self):
        dialog = Toplevel(self)
        dialog.title("Set Increment Value")
        dialog.geometry("200x100")

        Label(dialog, text="Increment Value:").pack(pady=5)
        increment_entry = Entry(dialog)
        increment_entry.pack(pady=5)

        def set_increment():
            try:
                increment_value = float(increment_entry.get())
                self.__spinbox.config(increment=increment_value)
                dialog.destroy()
            except ValueError:
                pass  # Handle invalid input if necessary

        Button(dialog, text="Set", command=set_increment).pack(pady=5)

    @property
    def label(self) -> Label:
        return self.__label

    @property
    def spinbox(self) -> Spinbox:
        return self.__spinbox

    @property
    def label_text(self) -> str:
        return self.__label["text"]

    @label_text.setter
    def label_text(self, text: str) -> None:
        self.__label["text"] = text

    @property
    def label_common_icon(self):
        return self.__image

    @label_common_icon.setter
    def label_common_icon(self, icon):
        tkicon = load_icon(icon, common=True)
        self.__image = tkicon
        self.__label["image"] = tkicon

    @property
    def spinbox_value(self) -> str:
        return self.__spinbox.get()

    @spinbox_value.setter
    def spinbox_value(self, value: str) -> None:
        self.__spinbox.delete(0, "end")
        self.__spinbox.insert(0, value)

    @property
    def spinbox_variable(self):
        return self.__spinbox["textvariable"]

    @spinbox_variable.setter
    def spinbox_variable(self, val) -> None:
        self.__spinbox.config(textvariable=val)

    @property
    def label_width(self):
        return self.__label["width"]

    @label_width.setter
    def label_width(self, width) -> None:
        self.__label["width"] = width

    @property
    def label_compound(self):
        return self.__label["compound"]

    @label_compound.setter
    def label_compound(self, val) -> None:
        self.__label["compound"] = val

    @property
    def spinbox_from(self):
        return self.__spinbox["from_"]

    @spinbox_from.setter
    def spinbox_from(self, val) -> None:
        self.__spinbox["from_"] = val

    @property
    def spinbox_to(self):
        return self.__spinbox["to"]

    @spinbox_to.setter
    def spinbox_to(self, val) -> None:
        self.__spinbox["to"] = val

    @property
    def spinbox_width(self):
        return self.__spinbox["width"]

    @spinbox_width.setter
    def spinbox_width(self, width) -> None:
        self.__spinbox["width"] = width

    def get_int(self) -> int:
        value = self.__spinbox.get()
        return int(value) if value.isdigit() else 0

    def get_float(self) -> float:
        try:
            return float(self.__spinbox.get())
        except ValueError:
            return 0.0