from tkinter import *
from tkinter.ttk import Button
from wavesynlib.widgets.tk.group import Group

load_grp = {'class': Group, 'name': 'load_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Load'}, 'children': [{'class': Button,
    'name': 'load_btn', 'init': {'text': 'Load'}}]}
unpack_grp = {'class': Group, 'name': 'unpack_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Unpack'}, 'children': [{'class':
    Button, 'name': 'unpack_btn', 'init': {'text': 'Unpack'}}]}