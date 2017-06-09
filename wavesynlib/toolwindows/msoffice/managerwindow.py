# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:33:03 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk

from wavesynlib.guicomponents.tk import ScrolledTree, Group, json_to_tk
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.wavesynscript import code_printer



class AppTreeview(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self._make_widgets()
        
        
    def _make_widgets(self):
        tree_container = ScrolledTree(self)
        tree_container.pack(expand='yes', fill='both')
        self.__tree = tree = tree_container.tree
        tree['columns'] = ['app', 'id']
        tree.heading('app', text='App')
        tree.heading('id', text='ID')
        self._tree = tree
        
        
    def update(self, app_dict):
        self.clear()
        for id_ in app_dict:
            obj = app_dict[id_]
            node = self.__tree.insert('', 'end', text=obj.caption, values=(obj.name, id_))
            if obj.name.lower() == 'word':
                for window in obj.windows:
                    self.__tree.insert(node, 'end', text=window.Caption, values=('Word', ''))
            
            
    def clear(self):
        tree = self.__tree
        for row in tree.get_children():
            tree.delete(row)
            
            
            
class OfficeController(TkToolWindow):
    window_name = 'WaveSyn-MSOfficeController'
    
    
    def __init__(self):
        TkToolWindow.__init__(self)
        self._gui_images = []
        tool_tabs = self._tool_tabs
        
        widgets_desc = [
{'class':'Group', 
     'pack':{'side':'left', 'fill':'y'},
    'setattr':{'name':'Connect'},
    'children':[
        {'class':'Button',
             'config':{'text':'Get Active', 'command':self.__on_get_active}
        },
        {'class':'Button',
             'config':{'text':'Create', 'command':self.__on_create}
        }
    ]
},

{'class':'Group',
    'pack':{'side':'left', 'fill':'y'},
    'setattr':{'name':'Window'},
    'children':[
        {'class':'Button',
             'config':{'text':'Foreground', 'command':self.__on_foreground}
        }
    ]
},

{'class':'Group',
    'name':'utils_group',
    'pack':{'side':'left', 'fill':'y'},
    'setattr':{'name':'Utils'}
}
]
        
        tab = tk.Frame(tool_tabs)
        widgets = json_to_tk(tab, widgets_desc)

        self.__utils_group = utils_group = widgets['utils_group']
        # Utils panel if no item is selected.
        self.__null_utils_frame = null_utils_frame = tk.Frame(utils_group)
        null_utils_frame.pack(fill='both')
        tk.Label(null_utils_frame, text='No Utils Available').pack(fill='both')
        self.__current_utils_frame = null_utils_frame
        # Utils panel if a Word instance is selected.
        self.__word_utils_frame = word_utils_frame = tk.Frame(utils_group)
        ttk.Button(word_utils_frame, text='Insert PSD', command=self.__on_insert_psd).pack(fill='x')
        ttk.Button(word_utils_frame, text='Update PSD', command=self.__on_update_psd).pack(fill='x')
        # Utils panel if an Excel instance is selected.
        self.__excel_utils_frame = excel_utils_frame = tk.Frame(utils_group)
        tk.Label(excel_utils_frame, text='Excel Utils').pack(fill='both')
        
        tool_tabs.add(tab, text='Office')
        
        self._make_window_manager_tab()
        self.__treeview = treeview = AppTreeview(self.tk_object)
        treeview.pack(expand='yes', fill='both')
        treeview._tree.bind('<<TreeviewSelect>>', self.__on_select)
        app_dict = self.root_node.interfaces.msoffice
        treeview.update(app_dict)
        
        
    def __connect_app(self, app_name=None, get_active=True):
        if app_name is None:
            app_name = self.root_node.lang_center.wavesynscript.constants.ASK_LIST_ITEM

        msoffice = self.root_node.interfaces.msoffice
        
        with code_printer:
            if get_active:
                msoffice.get_active(app_name=app_name)
            else:
                msoffice.create(app_name=app_name)
        self.__treeview.update(msoffice)        
        
        
    def __on_get_active(self, app_name=None):
        self.__connect_app(app_name)
        
        
    def __on_create(self, app_name=None):
        self.__connect_app(app_name, get_active=False)
        
        
    def __on_foreground(self):
        office = self.root_node.interfaces.msoffice
        tree = self.__treeview._tree
        iid = tree.selection()[0]
        cur = tree.item(iid)
        app_name = cur['values'][0].lower()
        id_ = cur['values'][1]
        if app_name == 'excel':
            office[id_].set_foreground()
        elif app_name == 'word':
            if id_:
                office[id_].set_foreground()
            else:
                piid = tree.parent(iid)
                pcontent = tree.item(piid)
                app_id = pcontent['values'][1]
                office[app_id].set_foreground(index=cur['text'])
                
                
    def __on_select(self, event):
        tree = self.__treeview._tree
        cur = tree.item(tree.selection())
        app_name = cur['values'][0].lower()
        if app_name == 'word':
            if self.__current_utils_frame is not self.__word_utils_frame:
                self.__current_utils_frame.pack_forget()
                self.__word_utils_frame.pack(fill='both')
                self.__current_utils_frame = self.__word_utils_frame
        elif app_name == 'excel':
            if self.__current_utils_frame is not self.__excel_utils_frame:
                self.__current_utils_frame.pack_forget()
                self.__excel_utils_frame.pack(fill='both')
                self.__current_utils_frame = self.__excel_utils_frame
    
    
    def __on_insert_psd(self):
        pass
    
    
    def __on_update_psd(self):
        pass
