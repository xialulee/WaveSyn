from tkinter import Label
from PIL import ImageTk
from pathlib import Path

_image_path = Path(__file__).parent / "images"
_busy_icon_path      = _image_path / "busy.png"
_available_icon_path = _image_path / "available.png"



class BusyLight(Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__busy = False
        self._busy_icon      = ImageTk.PhotoImage(file=_busy_icon_path)
        self._available_icon = ImageTk.PhotoImage(file=_available_icon_path)
        self["image"] = self._available_icon


    @property
    def busy(self):
        return self.__busy

    @busy.setter
    def busy(self, val):
        if val != self.__busy:
            self.__busy = val
            self["image"] = self._busy_icon if val else self._available_icon
            self.update()
