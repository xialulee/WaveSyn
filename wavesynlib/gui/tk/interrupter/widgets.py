from __future__ import annotations

from tkinter import Frame, Button
from tkinter.ttk import Label


main_panel = {
    'class': Frame, 
    'name': 'main_panel', 
    'children': [
        {
            'class': Label, 
            'name': 'message_lbl', 
            'init': {
                'text': """\
If you start a time consuming loop in the wavesyn's console,
the GUI components will not response anymore.
If you want to abort this mission, you can click the button below."""
            }
        }, 
        {
            'class': Button, 
            'name': 'abort_btn', 
            'init': {
                'text': 'Abort!',
                'bg': 'red', 
                'fg': 'white'
            }
        }, 
        {
            'class': Label, 
            'name': 'blank_lbl'
        }
    ]
}
