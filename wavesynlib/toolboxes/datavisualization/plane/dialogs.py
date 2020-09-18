import hy

from tkinter import DoubleVar, StringVar, Toplevel
from tkinter.colorchooser import askcolor
from tkinter.ttk import Button, Combobox, Label, Radiobutton

from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk
from .widgets import (
    common_prop_panel,
    plot_prop_panel, 
    stem_prop_panel,
    scatter_prop_panel)



def ask_drawmode():
    win = Toplevel()
    win.title("Draw mode")
    Label(win, text="Select draw mode:").pack()
    drawmode = StringVar()
    drawmode.set("plot")
    modes = ["plot", "stem", "scatter"]
    for mode in modes:
        Radiobutton(win, text=mode, value=mode, variable=drawmode).pack(anchor="nw")
    Button(win, text="OK", command=win.quit).pack()

    win.protocol("WM_DELETE_WINDOW", win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()
    return drawmode.get()



def handle_common_properties(widgets):
    color = [None]
    def on_choose_color():
        color[0] = askcolor()[1]
    widgets["color_btn"]["command"] = on_choose_color
    marker = StringVar()
    widgets["marker_lent"].entry["textvariable"] = marker
    alpha = DoubleVar()
    alpha.set(1.0)
    widgets["alpha_scale"].scale["variable"] = alpha
    return color, marker, alpha




def ask_plot_properties():
    win = Toplevel()
    win.title("Plot Properties")

    widgets_desc = [common_prop_panel, plot_prop_panel]
    widgets = hywidgets_to_tk(win, widgets_desc)

    color, marker, alpha = handle_common_properties(widgets)

    linestyle = StringVar(value='"-"')
    widgets["linestyle_lent"].entry["textvariable"] = linestyle

    linewidth = StringVar(value="1.0")
    widgets["linewidth_lent"].entry["textvariable"] = linewidth

    widgets["ok_btn"]["command"] = win.quit

    win.protocol("WM_DELETE_WINDOW", win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()

    marker = marker.get()
    linestyle = linestyle.get()
    linestyle = None if not linestyle else eval(linestyle)
    linewidth = linewidth.get()
    linewidth = None if not linewidth else float(linewidth)

    return {
        "color":     color[0], 
        "marker":    marker if marker else None,
        "alpha":     alpha.get(),
        "linestyle": linestyle,
        "linewidth": linewidth}



def ask_stem_properties():
    win = Toplevel()
    win.title("Stem Properties")
    widgets_desc = [common_prop_panel, stem_prop_panel]
    widgets = hywidgets_to_tk(win, widgets_desc)
    color, marker, alpha = handle_common_properties(widgets)
    marker.set("o")
    widgets["alpha_scale"].pack_forget()
    widgets["ok_btn"]["command"] = win.quit

    win.protocol("WM_DELETE_WINDOW", win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()

    marker = marker.get()

    return {
        "color":  color[0], 
        "markerfmt": marker if marker else None}



def ask_scatter_properties():
    win = Toplevel()
    win.title("Scatter Properties")

    widgets_desc = [common_prop_panel, scatter_prop_panel]
    widgets = hywidgets_to_tk(win, widgets_desc)

    color, marker, alpha = handle_common_properties(widgets)
    marker.set("o")

    widgets["ok_btn"]["command"] = win.quit

    win.protocol("WM_DELETE_WINDOW", win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()

    marker = marker.get()

    return {
        "color":  color[0], 
        "marker": marker if marker else None, 
        "alpha":  alpha.get()}



