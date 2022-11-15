from tkinter import *
from tkinter.ttk import Button, Combobox

from wavesynlib.widgets.tk.group import Group
from wavesynlib.widgets.tk.wsbutton import WSButton
from wavesynlib.widgets.tk.labeledentry import LabeledEntry
from wavesynlib.widgets.tk.labeledscale import LabeledScale
from wavesynlib.languagecenter.wavesynscript import Scripting

load_grp = {'class': Group, 'name': 'load_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Load'}, 'children': [{'class': Frame,
    'name': 'grid_frm', 'pack': {'side': LEFT, 'fill': BOTH}, 'children': [
    {'class': WSButton, 'name': 'loadvar_btn', 'setattr': {'common_icon':
    'console20x20.psd'}, 'balloonmsg': 'Load a variable from console.',
    'grid': {'row': 0, 'column': 0}}, {'class': WSButton, 'name':
    'loadpkl_btn', 'setattr': {'common_icon': 'pickle20x20.psd'},
    'balloonmsg': 'Load a pickle file.', 'grid': {'row': 0, 'column': 1}},
    {'class': WSButton, 'name': 'runexpr_btn', 'setattr': {'common_icon':
    'python20x20.psd'}, 'balloonmsg': 'Run a python expression.', 'grid': {
    'row': 0, 'column': 2}}]}]}
common_prop_panel = {'class': Frame, 'name': 'common_prop_panel',
    'children': [{'class': WSButton, 'name': 'color_btn', 'init': {'text':
    'color', 'compound': LEFT}, 'setattr': {'common_icon': 'color20x20.psd'
    }, 'balloonmsg': 'Choose color.', 'pack': {'fill': X}}, {'class':
    LabeledEntry, 'name': 'marker_lent', 'setattr': {'label_text': 'marker'
    }}, {'class': LabeledScale, 'name': 'alpha_scale', 'init': {'from_':
    0.0, 'to': 1.0}, 'setattr': {'value_formatter': lambda val:
    f'{float(val):.2f}', 'name': 'alpha', 'scale_value': 1.0}, 'pack': {
    'fill': X}}]}
plot_prop_panel = {'class': Frame, 'name': 'plot_prop_panel', 'children': [
    {'class': LabeledEntry, 'name': 'linestyle_lent', 'setattr': {
    'label_text': 'linestyle'}}, {'class': LabeledEntry, 'name':
    'linewidth_lent', 'setattr': {'label_text': 'linewidth',
    'checker_function': Scripting.root_node.gui.value_checker.
    check_nonnegative_float}}, {'class': Button, 'name': 'ok_btn', 'init':
    {'text': 'OK'}}]}
scatter_prop_panel = {'class': Frame, 'name': 'scatter_prop_panel',
    'children': [{'class': Button, 'name': 'ok_btn', 'init': {'text': 'OK'}}]}
stem_prop_panel = {'class': Frame, 'name': 'stem_prop_panel', 'children': [
    {'class': Button, 'name': 'ok_btn', 'init': {'text': 'OK'}}]}
