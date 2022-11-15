from tkinter import Frame
from tkinter.ttk import Button, Combobox, Radiobutton

from wavesynlib.widgets.tk.group import Group
from wavesynlib.widgets.tk.wsbutton import WSButton
from wavesynlib.widgets.tk.labeledentry import LabeledEntry
from wavesynlib.languagecenter.wavesynscript import Scripting

to_dvplane_frm = {'class': Frame, 'name': 'to_dvplane_frm', 'pack': {'fill':
    'both'}, 'children': [{'class': Button, 'name': 'new_btn', 'init': {
    'text': 'New'}, 'pack': {'fill': 'x'}}, {'class': Frame, 'name':
    'exist_frm', 'pack': {'fill': 'x'}, 'children': [{'class': Combobox,
    'name': 'id_cmb', 'pack': {'side': 'left', 'fill': 'x'}}, {'class':
    Button, 'name': 'ok_btn', 'init': {'text': 'Ok'}}]}]}
ask_export_to_console_frm = {'class': Frame, 'name':
    'ask_export_to_console_frm', 'pack': {'fill': 'both'}, 'children': [{
    'class': Radiobutton, 'name': 'rad_btn', 'init': {'text': 'rad'},
    'pack': {'anchor': 'nw'}}, {'class': Radiobutton, 'name': 'deg_btn',
    'init': {'text': 'deg'}, 'pack': {'anchor': 'nw'}}, {'class':
    LabeledEntry, 'name': 'varname_lent', 'setattr': {'label_text':
    'var name:'}, 'pack': {'anchor': 'nw'}, 'balloonmsg':
    'Input variable name here. '}, {'class': Button, 'name': 'ok_btn',
    'init': {'text': 'Ok'}}]}
parameter_grp = {'class': Group, 'name': 'parameter_grp', 'pack': {'side':
    'left', 'fill': 'y'}, 'setattr': {'name': 'Parameters'}, 'children': [{
    'class': LabeledEntry, 'name': 'num_elem_lent', 'setattr': {
    'label_compound': 'left', 'label_common_icon': 'arrayelemnum20x20.png',
    'label_text': 'M', 'label_width': 4, 'entry_width': 6, 'entry_text': 16,
    'checker_function': Scripting.root_node.gui.value_checker.check_int},
    'balloonmsg': 'The number of the array elements.'}, {'class':
    LabeledEntry, 'name': 'dist_elem_lent', 'setattr': {'label_compound':
    'left', 'label_common_icon': 'arrayelemdist20x20.png', 'label_text':
    'd/λ', 'label_width': 4, 'entry_width': 6, 'entry_text': 0.5,
    'checker_function': Scripting.root_node.gui.value_checker.
    check_positive_float}, 'balloonmsg':
    'The space between elements (with respect to wavelength).'}, {'class':
    WSButton, 'name': 'run_btn', 'init': {'compound': 'left'}, 'setattr': {
    'common_icon': 'run20x20.png'}}]}
export_data_grp = {'class': Group, 'name': 'export_data_grp', 'pack': {
    'side': 'left', 'fill': 'y'}, 'setattr': {'name': 'Data'}, 'children':
    [{'class': Frame, 'name': 'export_button_frame', 'children': [{'class':
    WSButton, 'name': 'export_to_console_btn', 'setattr': {'common_icon':
    'console20x20.psd'}, 'grid': {'row': 0, 'column': 0}, 'balloonmsg':
    'Export data to the console.'}, {'class': WSButton, 'name':
    'export_to_dvplane_btn', 'setattr': {'common_icon':
    'figurewindow20x20.psd'}, 'grid': {'row': 0, 'column': 1}, 'balloonmsg':
    'Export data to a data visualization plane window.'}]}]}