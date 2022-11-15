from tkinter import Toplevel
from tkinter.ttk import Label


class Balloon:
    """\
Balloon implementation which is compatible with the original Tix one.
Based on this post: http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml."""

    class Tip:
        def __init__(self, parent, text):
            self.tip_widget = None
            self.parent = parent
            self.text = text
            self.__show_callback = lambda : ""

        @property
        def show_callback(self):
            return self.__show_callback

        @show_callback.setter
        def show_callback(self, func):
            if not callable(func):
                raise 'show_callback should be callable.'
            self.__show_callback = func

        def show(self) -> None:
            parent = self.parent
            text = self.text + self.show_callback()
            [x, y, cx, cy] = parent.bbox("insert")
            x = x + parent.winfo_rootx() + 27
            y = y + cy + parent.winfo_rooty() + 27
            tipw = Toplevel(self.parent)
            self.tip_widget = tipw
            tipw.wm_overrideredirect(1)
            tipw.wm_geometry(f"+{x}+{y}")
            Label(
                tipw,
                text = text,
                justify = "left",
                background = "#ffffe0",
                relief = "solid",
                borderwidth = 1,
                font = (
                    "tahoma",
                    "8",
                    "normal"
                )
            ).pack(ipadx=1)

        def hide(self) -> None:
            tipw = self.tip_widget
            self.tip_widget = None
            if tipw:
                tipw.destroy()

    def __init__(self, *args, **kwargs):
        pass

    def bind_widget(self, widget, balloonmsg):
        tip = self.Tip(widget, balloonmsg)
        widget.bind("<Enter>", lambda event: tip.show())
        widget.bind("<Leave>", lambda event: tip.hide())
        return tip