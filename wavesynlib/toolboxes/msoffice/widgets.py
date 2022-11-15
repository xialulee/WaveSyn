from tkinter import *
from tkinter.ttk import Button

from wavesynlib.widgets.tk.group import Group


connect_grp = {'class': Group, 'name': 'connect_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Connect'}, 'children': [{'class':
    Button, 'name': 'get_active_btn', 'init': {'text': 'Get Active'}}, {
    'class': Button, 'name': 'create_btn', 'init': {'text': 'Create'}}]}
window_grp = {'class': Group, 'name': 'window_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Window'}, 'children': [{'class':
    Button, 'name': 'foreground_btn', 'init': {'text': 'Foreround'}}, {
    'class': Button, 'name': 'copypath_btn', 'init': {'text': 'Copy Path'}}]}
utils_grp = {'class': Group, 'name': 'utils_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Utils'}}