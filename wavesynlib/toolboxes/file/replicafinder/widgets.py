from tkinter import *
from tkinter.ttk import Label

from PIL import ImageTk

from wavesynlib.widgets.tk.group import Group
from wavesynlib.widgets.tk.busylight import BusyLight
from wavesynlib.widgets.tk.wsbutton import WSButton


finder_grp = {'class': Group, 'name': 'finder_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Finder'}, 'children': [{'class': Frame,
    'name': 'grid_frm', 'pack': {'side': LEFT, 'fill': BOTH}, 'children': [
    {'class': WSButton, 'name': 'start_btn', 'setattr': {'common_icon':
    'run20x20.png'}, 'grid': {'row': 0, 'column': 0}}, {'class': WSButton,
    'name': 'stop_btn', 'setattr': {'common_icon': 'stop20x20.psd'}, 'grid':
    {'row': 0, 'column': 1}}]}]}
status_frm = {'class': Frame, 'name': 'status_frm', 'pack': {'fill': X},
    'children': [{'class': BusyLight, 'name': 'light_lbl', 'pack': {'side':
    RIGHT}}, {'class': Label, 'name': 'current_dir_lbl', 'pack': {'side':
    RIGHT}}]}
