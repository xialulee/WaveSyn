from wavesynlib.widgets.tk.desctotk import Bind as bind
from tkinter import *
from tkinter.ttk import Button, Progressbar
from pathlib import Path
from wavesynlib.widgets.tk.wsbutton import WSButton
from wavesynlib.widgets.tk.labeledentry import LabeledEntry
from wavesynlib.widgets.tk.scrolledlist import ScrolledList
from wavesynlib.widgets.tk.group import Group

_res_dir = Path(__file__).parent / 'resources'

clipb_grp = {'class': Group, 'name': 'clipb_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Clipboard'}, 'children': [{'class':
    Frame, 'name': 'clipb_grid_frm', 'children': [{'class': WSButton,
    'name': 'read_clipb_btn', 'grid': {'row': 0, 'column': 0}, 'init': {
    'image': _res_dir / 'readclipb.png', 'command_object': bind(
    'read_clipb')}, 'balloonmsg':
    'Read the clipboard of an Android device.'}, {'class': WSButton, 'name':
    'write_clipb_btn', 'grid': {'row': 0, 'column': 1}, 'init': {'image': 
    _res_dir / 'writeclipb.png', 'command_object': bind('write_clipb')},
    'balloonmsg': 'Write the clipboard of an Android device.'}, {'class':
    WSButton, 'name': 'send_clipb_image_btn', 'grid': {'row': 0, 'column': 
    2}, 'init': {'image': _res_dir / 'sendclipbimage.png'}, 'balloonmsg':
    'Send image in clipboard to the Android device.'}]}]}

storage_grp = {'class': Group, 'name': 'storage_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Storage'}, 'children': [{'class':
    Frame, 'name': 'storage_grid_frm', 'children': [{'class': WSButton,
    'name': 'get_image_btn', 'grid': {'row': 0, 'column': 0}, 'balloonmsg':
    'Get gallery photos.', 'init': {'image': _res_dir / 'getimage.png'}}, {
    'class': WSButton, 'name': 'get_file_btn', 'grid': {'row': 0, 'column':
    1}, 'balloonmsg': 'Get File', 'init': {'image': _res_dir /
    'getfile.png'}}, {'class': WSButton, 'name': 'send_image_btn', 'grid':
    {'row': 1, 'column': 0}, 'balloonmsg': 'Send a picture to the device.',
    'init': {'image': _res_dir / 'sendclipbimage.png'}}, {'class': WSButton,
    'name': 'send_file_btn', 'grid': {'row': 1, 'column': 1}, 'balloonmsg':
    'Send a file to the device.', 'init': {'image': _res_dir /
    'sendfile.png'}}, {'class': Progressbar, 'name': 'transfer_progressbar',
    'grid': {'row': 2, 'columnspan': 2}, 'balloonmsg':
    'Data transfer progress', 'init': {'length': 60, 'maximum': 100,
    'variable': bind('transfer_progress')}}]}]}

sensors_grp = {'class': Group, 'name': 'sensors_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Sensors'}, 'children': [{'class':
    Frame, 'name': 'sensors_grid_frm', 'children': [{'class': WSButton,
    'name': 'read_gps_btn', 'balloonmsg':
    'Read the AGPS sensor of the Android device.', 'init': {'text':
    'Location', 'image': _res_dir / 'locationsensor.png', 'compound': LEFT}}]}]
    }

manage_grp = {'class': Group, 'name': 'manage_grp', 'pack': {'side': LEFT,
    'fill': Y}, 'setattr': {'name': 'Manager'}, 'children': [{'class':
    Frame, 'name': 'manage_left_frm', 'pack': {'side': LEFT, 'fill': Y},
    'children': [{'class': LabeledEntry, 'name': 'qr_size_lent',
    'balloonmsg': 'Size (pixels) of the generated QR code.', 'setattr': {
    'label_text': 'QR Size', 'label_width': 7, 'entry_width': 4,
    'entry_text': 200}}, {'class': Button, 'name': 'qr_size_ok_btn', 'init':
    {'text': 'Ok'}}, {'class': Button, 'name': 'misson_abort_btn', 'init':
    {'text': 'Abort'}}]}, {'class': Frame, 'name': 'manage_right_frm',
    'pack': {'side': LEFT, 'fill': Y}, 'children': [{'class': ScrolledList,
    'name': 'ip_list', 'pack': {'fill': Y}}]}]}