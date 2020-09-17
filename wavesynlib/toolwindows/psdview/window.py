# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 13:01:11 2016

@author: Feng-cong Li
"""
import os
from pathlib import Path
import tempfile
import time
import tkinter as tk
from tkinter import ttk
import psd_tools

from PIL import Image
from PIL import ImageTk

import hy
from wavesynlib.widgets.tk.scrolledtree import ScrolledTree
from wavesynlib.widgets.tk.desctotk import json_to_tk
from wavesynlib.widgets.tk.scrolledcanvas import ScrolledCanvas
from wavesynlib.interfaces.timer.tk import TkTimer
from wavesynlib.widgets.tk.tkbasewindow import TkToolWindow
from wavesynlib.languagecenter.utils import MethodDelegator
from wavesynlib.languagecenter.wavesynscript import Scripting, WaveSynScriptAPI, code_printer
from wavesynlib.languagecenter.datatypes.treetype import AbstractTreeNode, tree_trans
from wavesynlib.toolwindows.psdview.widgets import (
        load_grp, export_grp, resize_grp,
        external_viewer_grp, wallpaper_grp)



class TreeViewNode(AbstractTreeNode):
    def __init__(self, tree, node=''):
        self.control = tree.tree_view
        self.tree = tree
        self.node = node


    def __iter__(self):
        raise NotImplementedError()

    
    def is_group(self):
        raise NotImplementedError()


    def make_node(self, node_info):
        new_node = self.control.insert(
            self.node,
            '0',
            text=node_info.name,
            values=(
                str(node_info.visible), 
                f'{str(node_info.opacity*100//255)}%', 
                node_info.blend_mode))
        return TreeViewNode(self.tree, new_node)


    def make_group(self, group_info):
        return self.make_node(group_info)


    def make_leaf(self, leaf_info):
        self.make_node(leaf_info)



class LayerTree:
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


    def _make_layer_tree(self, image):
        dest_root = TreeViewNode(self)
        tree_trans(source=image, dest=dest_root)
    
        
    def clear(self):
        self.__tree_view.clear()
                
                
    @property
    def psd_image(self):
        return self.__psd_image
    
        
    @psd_image.setter
    def psd_image(self, image):
        self.__psd_image = image
        self.clear()
        self._make_layer_tree(image)
        #for layer in image:
            #self._add_layer(layer)
            
        
    def _on_select_change(self, event):
        #print(self.__tree_view.selection()[0])
        pass
    
        
    for method_name in ('pack',):
        locals()[method_name] = MethodDelegator('tree_view', method_name)
        
                    
                    
class PSDViewer(TkToolWindow):
    window_name = 'WaveSyn-PSDViewer'    

    
    def __init__(self):
        super().__init__()
        
        tool_tabs = self._tool_tabs
        
        widgets_desc = [
load_grp, export_grp, resize_grp, external_viewer_grp, wallpaper_grp]

        tab = tk.Frame(tool_tabs)
        widgets = json_to_tk(tab, widgets_desc)
        self.__scale_label = widgets['scale_label']
        self.__image_scale = widgets['image_scale']
        self.__image_scale['command'] = self._on_scale
        self.__wallpaper_position = widgets['wallpaper_position_combo']        
        self.__wallpaper_position.current(0)
        
        widgets['load_btn']['command'] =self._on_load_psd
        
        widgets['export_all_btn']['command'] = self._on_export_selected
        widgets['export_selected_btn']['command'] = self._on_export_selected
        
        widgets['launch_viewer_btn']['command'] = self._on_launch_viewer
        
        widgets['set_wallpaper_btn']['command'] = self._on_set_wallpaper
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
        self.__mtime = 0.0
        self.__scale = 100
        self.__all_canvas = all_canvas
        
        self.__timer = TkTimer(widget=self.tk_object)
        @self.__timer.add_observer
        def watch():
            if self.__psd_path:
                mtime = self.__psd_path.stat().st_mtime
                if mtime > self.__mtime:
                    with code_printer(False):
                        self.load(self.__psd_path)

        
    @WaveSynScriptAPI
    def load(self, filename):
        self.__timer.active = False
        
        filename = self.root_node.gui.dialogs.constant_handler_ASK_OPEN_FILENAME(
            filename, 
            filetypes=[('PSD Files', '*.psd'), ('All Files', '*.*')])
        if not filename:
            return
        
        filename = Path(filename)
        if not filename.exists():
            raise ValueError(f'Path {filename} does not exists.')
        self.__psd_path = filename
        #self.__scale = 100
        self.__mtime = Path(filename).stat().st_mtime
        self.__psd_image = psd_tools.PSDImage.open(filename)
                
        self.__layer_tree.psd_image = self.__psd_image
        self.__pil_image = self.__psd_image.composite()
        self.__tk_image = ImageTk.PhotoImage(image=self.__pil_image)
        if self.__image_id is None:
            self.__image_id = self.__all_canvas.canvas.create_image((0, 0), image=self.__tk_image, anchor='nw')
        else:
            self.__all_canvas.canvas.itemconfig(self.__image_id, image=self.__tk_image)
        width = self.__psd_image.width
        height = self.__psd_image.height
        self.__all_canvas.canvas.config(scrollregion=(0, 0, width, height))
        #self.__image_scale['value'] = 100
        self._on_scale(self.__scale)
        
        self.__timer.active = True
        
        
    @WaveSynScriptAPI
    def launch_viewer(self):
        self.root_node.gadgets.display_image(self.__pil_image)
        

    def _on_load_psd(self):
        with code_printer():
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
        self.__scale = val
        
        psd = self.__psd_image
        width, height = psd.width, psd.height
        width = width * val // 100
        height = height * val // 100
        new_tk_image = self.__pil_image.resize((width, height), Image.ANTIALIAS)
        new_tk_image = ImageTk.PhotoImage(new_tk_image)
        self.__tk_image = new_tk_image
        self.__all_canvas.canvas.itemconfig(self.__image_id, image=self.__tk_image)
        
        
    def _on_launch_viewer(self):
        with code_printer():
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
        
        
    def _close_callback(self):
        self.__timer.active = False
        super()._close_callback()
        
        
        
                    
                    
#if __name__ == '__main__':
#    psd_path = r"G:\Warehouse\components\1.psd"
#    psd_image = psd_tools.PSDImage.load(psd_path)
#    root = tix.Tk()
#    ltree = LayerTree(root)
#    ltree.pack(expand='yes', fill='both')
#    ltree.psd_image = psd_image
#    root.mainloop()
    