from tkinter import *
from tkinter.ttk import Button
from wavesynlib.widgets.tk.group import Group



source_grp = {
    'class': Group, 
    'name': 'source_grp', 
    'pack': {
        'side': LEFT,
        'fill': Y
    }, 
    'setattr': {
        'name': 'Source'
    }, 
    'children': [
        {
            'class': Button, 
            'name': 'parse_btn', 
            'init': {
                'text': 'Parse'
            }
        }
    ]
}
