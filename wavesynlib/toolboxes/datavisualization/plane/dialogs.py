import hy

from tkinter import StringVar, Toplevel
from tkinter.colorchooser import askcolor
from tkinter.ttk import Button, Combobox

from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk
from .widgets import drawmode_panel, scatter_panel



def ask_drawmode():
    win = Toplevel()
    win.title("Draw mode")

    widgets_desc = [drawmode_panel]
    widgets = hywidgets_to_tk(win, widgets_desc)

    drawmode = StringVar()
    drawmode.set("plot")
    widgets["drawmode_comb"]["textvariable"] = drawmode
    widgets["ok_btn"]["command"] = win.quit

    win.protocol("WM_DELETE_WINDOW", win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()
    return drawmode.get()


def ask_scatter_properties():
    win = Toplevel()
    win.title("Scatter Properties")

    widgets_desc = [scatter_panel]
    widgets = hywidgets_to_tk(win, widgets_desc)

    color = [None]
    def on_choose_color():
        color[0] = askcolor()[1]
    widgets["color_btn"]["command"] = on_choose_color

    marker = StringVar()
    widgets["marker_lent"].entry["textvariable"] = marker

    widgets["ok_btn"]["command"] = win.quit

    win.protocol("WM_DELETE_WINDOW", win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()

    marker = marker.get()

    return {
        "c":      color[0], 
        "marker": marker if marker else None }