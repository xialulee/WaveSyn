# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 13:01:11 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals


import os
import tempfile
import time
import six.moves.tkinter as tk
import six.moves.tkinter_ttk as ttk
import psd_tools

import numpy as np

from PIL import Image
from PIL import ImageTk

from wavesynlib.guicomponents.tk import ScrolledTree, ScrolledCanvas, json_to_tk
from wavesynlib.toolwindows.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.utils import MethodDelegator
from wavesynlib.languagecenter.wavesynscript import Scripting, code_printer


class LayerTree(object):    
    def __init__(self, *args, **kwargs):
        self.__tree_view = tree_view = ScrolledTree(*args, **kwargs)
        tree_view.tree['columns'] = ('visible', 'opacity', 'blend_mode')
        tree_view.heading('visible', text='Visible')
        tree_view.heading('opacity', text='Opacity')
        tree_view.heading('blend_mode', text='Blend Mode')
        tree_view.bind('<<TreeviewSelect>>', self._on_select_change)
        self.__layer_map = {}        
        self.__psd_image = None
                                
    @property
    def tree_view(self):
        return self.__tree_view
        
    def _add_layer(self, layer, parent=''):
        tree_node = self.__tree_view.insert(
            parent, 
            'end', 
            text=layer.name, 
            values=(str(layer.visible), str(layer.opacity*100//255)+'%', layer.blend_mode))
        self.__layer_map[tree_node] = layer
        
        if hasattr(layer, 'layers'): # if layer is in fact a Group
            for child in layer.layers:
                self._add_layer(child, parent=tree_node)
                
    @property
    def psd_image(self):
        return self.__psd_image
        
    @psd_image.setter
    def psd_image(self, image):
        self.__psd_image = image
        for layer in image.layers:
            self._add_layer(layer)
        
    def _on_select_change(self, event):
        #print(self.__tree_view.selection()[0])
        pass
        
    for method_name in ('pack',):
        locals()[method_name] = MethodDelegator('tree_view', method_name)
                    
                    
class PSDViewer(TkToolWindow):
    window_name = 'WaveSyn-PSDViewer'    

    
    def __init__(self):
        TkToolWindow.__init__(self)
        
        tool_tabs = self._tool_tabs
        
        widgets_desc = [
{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Load'}, 'children':[
    {'class':'Button', 'config':{'text':'Load', 'command':self._on_load_psd}}]
},

{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Export'}, 'children':[
    {'class':'Button', 'config':{'text':'All Layers', 'command':self._on_export_all}, 'pack':{'fill':'x'}},
    {'class':'Button', 'config':{'text':'Selected Layer/Group', 'command':self._on_export_selected}}]
},

{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Resize'}, 'children':[
    {'class':'Scale', 'name':'image_scale', 'config':{'from_':5, 'to':100, 'orient':'horizontal', 'value':100, 'command':self._on_scale}},
    {'class':'Label', 'name':'scale_label', 'config':{'text':'100%'}}]
},

{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Viewer'}, 'children':[
    {'class':'Button', 'config':{'text':'Launch', 'command':self._on_launch_viewer}}]
},

{'class':'Group', 'pack':{'side':'left', 'fill':'y'}, 'setattr':{'name':'Wallpaper'}, 'children':[
    {'class':'Button', 'config':{'text':'Set', 'command':self._on_set_wallpaper}},
    {'class':'Combobox', 'name':'wallpaper_position', 'config':{'stat':'readonly', 'values':['Center', 'Tile', 'Stretch', 'Fit', 'Fill', 'Span']}}]
}
]

        tab = tk.Frame(tool_tabs)
        widgets = json_to_tk(tab, widgets_desc)
        self.__scale_label = widgets['scale_label']
        self.__image_scale = widgets['image_scale']
        self.__wallpaper_position = widgets['wallpaper_position']        
        self.__wallpaper_position.current(0)
        tool_tabs.add(tab, text='PSD Files')
        
        tk_object = self.tk_object
        
        paned = tk.PanedWindow(tk_object)
        paned.config(sashwidth=4, sashrelief='groove', bg='forestgreen')
        paned.pack(expand='yes', fill='both')
                
        image_book = ttk.Notebook(paned)
        paned.add(image_book, stretch='always')
        all_canvas = ScrolledCanvas(image_book)
        image_book.add(all_canvas, text='Merged')
        sel_canvas = ScrolledCanvas(image_book)
        image_book.add(sel_canvas, text='Selected')
        
        self.__layer_tree = layer_tree = LayerTree(paned)
        paned.add(layer_tree.tree_view, stretch='never')        
        
        self._make_window_manager_tab()
        
        self.__psd_image = None
        self.__pil_image = None
        self.__tk_image = None
        self.__image_id = None
        self.__psd_path = ''
        self.__all_canvas = all_canvas

        
    @Scripting.printable
    def load(self, filename):
        filename = self.root_node.dialogs.support_ask_open_filename(
            filename, 
            filetypes=[('PSD Files', '*.psd'), ('All Files', '*.*')])
        if not filename:
            return
        self.__psd_path = filename
        self.__psd_image = psd_tools.PSDImage.load(filename)
        self.__layer_tree.psd_image = self.__psd_image
        self.__pil_image = self.__psd_image.as_PIL()
        self.__tk_image = ImageTk.PhotoImage(image=self.__pil_image)
        if self.__image_id is None:
            self.__image_id = self.__all_canvas.canvas.create_image((0, 0), image=self.__tk_image, anchor='nw')
        else:
            self.__all_canvas.canvas.itemconfig(self.__image_id, image=self.__tk_image)
        width = self.__psd_image.header.width
        height = self.__psd_image.header.height
        self.__all_canvas.canvas.config(scrollregion=(0, 0, width, height))
        self.__image_scale['value'] = 100
        
        
    @Scripting.printable
    def launch_viewer(self):
        rgb_matrix = np.array(self.__pil_image)
        self.root_node.image_display.launch(rgb_matrix)
        

    def _on_load_psd(self):
        with code_printer:
            self.load(self.root_node.lang_center.wavesynscript.constants.ASK_OPEN_FILENAME)

    
    def _on_export_all(self):
        pass

    
    def _on_export_selected(self):
        pass
    
    
    def _on_scale(self, val):
        if self.__pil_image is None:
            return
        val = int(float(val))
        self.__scale_label['text'] = str(val) + '%'
        
        psd = self.__psd_image
        width, height = psd.header.width, psd.header.height
        width = width * val // 100
        height = height * val // 100
        new_tk_image = self.__pil_image.resize((width, height), Image.ANTIALIAS)
        new_tk_image = ImageTk.PhotoImage(new_tk_image)
        self.__tk_image = new_tk_image
        self.__all_canvas.canvas.itemconfig(self.__image_id, image=self.__tk_image)
        
        
    def _on_launch_viewer(self):
        with code_printer:
            self.launch_viewer()
        
        
    def _on_set_wallpaper(self):
        if self.__pil_image is None:
            return
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tfile:
            self.__pil_image.save(tfile, 'jpeg')
        desktop_wallpaper = self.root_node.interfaces.os.desktop_wallpaper
        desktop_wallpaper.set(tfile.name)
        desktop_wallpaper.position = self.__wallpaper_position.current()
        time.sleep(1) # OS need time to set the wallpaper.
        os.remove(tfile.name)
        
        
        
                    
                    
#if __name__ == '__main__':
#    psd_path = r"G:\Warehouse\components\1.psd"
#    psd_image = psd_tools.PSDImage.load(psd_path)
#    root = tix.Tk()
#    ltree = LayerTree(root)
#    ltree.pack(expand='yes', fill='both')
#    ltree.psd_image = psd_image
#    root.mainloop()
    