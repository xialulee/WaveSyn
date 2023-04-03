from tkinter import Toplevel, StringVar 

from wavesynlib.widgets.tk.desctotk import hywidgets_to_tk
from wavesynlib.languagecenter.wavesynscript import Scripting
from .widgets import to_dvplane_frm, ask_export_to_console_frm

from wavesynlib.toolboxes.datavisualization.plane.window import PlaneWindow



def ask_dvplane(window_node):
    win = Toplevel()
    win.title("Select a window")

    root_node = window_node.root_node

    widgets_desc = [to_dvplane_frm]
    widgets = hywidgets_to_tk(win, widgets_desc)

    sel_exist = False

    winid_var = StringVar()
    def on_exist_dvplane():
        nonlocal sel_exist
        sel_exist = True
        win.quit()
    widgets["ok_btn"]["command"] = on_exist_dvplane

    def on_new_dvplane():
        nonlocal sel_exist
        sel_exist = False
        win.quit()
    widgets["new_btn"]["command"] = on_new_dvplane

    dvplanes = [wid \
        for wid, window in root_node.gui.windows.items() \
            if isinstance(window, PlaneWindow)]
    id_cmb = widgets["id_cmb"]
    id_cmb["textvariable"] = winid_var
    id_cmb["value"] = dvplanes
    if dvplanes:
        id_cmb.current(0)
    else:
        widgets["ok_btn"]["state"] = "disabled"

    win.protocol("WM_DELETE_WINDOW", win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()

    return sel_exist, winid_var.get()



def ask_export_to_console():
    win = Toplevel()
    win.title("Export")
    widgets_desc = [ask_export_to_console_frm]
    widgets = hywidgets_to_tk(
        win, 
        widgets_desc, 
        balloon=Scripting.root_node.gui.balloon)
    unit = StringVar(value="rad")
    varname = StringVar(value="")
    rad_btn = widgets["rad_btn"]
    rad_btn["variable"] = unit
    rad_btn["value"] = "rad"
    deg_btn = widgets["deg_btn"]
    deg_btn["variable"] = unit
    deg_btn["value"] = "deg"
    widgets["varname_lent"].entry["textvariable"] = varname
    widgets["ok_btn"]["command"] = win.quit

    win.protocol("WM_DELETE_WINDOW", win.quit)
    win.focus_set()
    win.grab_set()
    win.mainloop()
    win.destroy()
    return varname.get(), unit.get()
