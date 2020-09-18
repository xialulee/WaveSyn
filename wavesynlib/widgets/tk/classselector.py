# -*- coding: utf-8 -*-
"""
Created on Sat Apr 04 10:03:17 2015

@author: Feng-cong Li
"""
import os
import sys
import importlib
import subprocess as sp
import multiprocessing as mp

import inspect
from tkinter import Toplevel, Tk
from tkinter.ttk import Button
from six.moves.tkinter import Frame

import hy

# Should not use relative import.
# Because ask_class_name will call this file in a new process.
from wavesynlib.widgets.tk.scrolledtree import ScrolledTree
from wavesynlib.stdstream import dumb_stream



class ClassSelector:
    def __init__(self, package_name, base_class, display_base_class=False):
        self.__package_name = package_name
        self.__base_class = base_class
        self.__display_base_class = display_base_class
        self.__window = window = Toplevel()
        window.title('Class Selector')
        self.__selected_class_name = ''
        self.__selected_module_name = ''
        
        self.__tree = tree = ScrolledTree(window)
        tree.pack()
        # If a module print something while being loaded, the stdout of this
        # script will be contaminated. 
        # The dumb_stream prevents the contamination. 
        with dumb_stream():
            classes = self.load_modules()
        for package in classes:
            packageNode = tree.insert('', 'end', text=package)
            for class_name in classes[package]:
                tree.insert(packageNode, 'end', text=class_name, values=package)
                
        button_frame = Frame(window)
        button_frame.pack()
        def _on_click(module_name, class_name):
            self.__selected_module_name   = module_name
            self.__selected_class_name    = class_name
            window.destroy()
        cancel_button = Button(button_frame, text='Cancel', command=lambda: _on_click('', ''))
        cancel_button.pack(side='right')
        ok_button     = Button(
            button_frame, 
            text='OK', 
            command=lambda: _on_click(
                tree.item(tree.selection(), 'values')[0],
                tree.item(tree.selection(), 'text')
            )
        )
        ok_button.pack(side='right')
        
        
    def do_model(self):
        win = self.__window
        win.focus_set()
        win.grab_set()
        win.wait_window() 
        return self.__selected_module_name, self.__selected_class_name
    
        
    def load_modules(self):
        retval = {}
        package = importlib.import_module(self.__package_name)
        package_path = os.path.split(package.__file__)[0]
        for item in os.listdir(package_path):
            filename = item.split('.')            
            if filename[-1] == 'py':
                try:
                    mod = importlib.import_module('.'.join((self.__package_name, filename[0])))
                except ImportError as err:
                    # To Do: print information on the console
                    continue
                mod_item_names = dir(mod)
                for mod_item_name in mod_item_names:
                    mod_item = getattr(mod, mod_item_name)
                    if isinstance(mod_item, type) and issubclass(mod_item, self.__base_class):
                        if not self.__display_base_class and mod_item is self.__base_class:
                            continue
                        if mod.__name__ not in retval:
                            retval[mod.__name__] = []
                        retval[mod.__name__].append(mod_item_name)
        return retval
                


def ask_class_name(package_name, base_class):
    file_path = inspect.getsourcefile(ClassSelector)
    p = sp.Popen(['python', file_path, package_name, base_class.__module__, base_class.__name__], stdout=sp.PIPE);
    stdout, stderr  = p.communicate()
    return stdout.strip().split()
    


# Use multiprocessing for creating nonblocking ClassSelector dialog.
# However, it seems that multiprocessing will copy the parent process (not only the selector poped out, but also another a new wavesyn console came out).
# Hence, create_process is not used.
# Maybe later I'll figure out how to solve this problem.
class ClassSelectorProcess:
    def __init__(self, process, parent_conn):
        self.process = process
        self.parent_conn = parent_conn
        
        
    def start(self):
        return self.process.start()
    
        
    def is_alive(self):
        return self.process.is_alive()
    
    
    @property    
    def return_value(self):
        if self.is_alive():
            raise Exception('ClassSelector process is still running.')
        return self.parent_conn.recv()
    
    

def selector_procedure(conn, args, kwargs):
    conn.send(ClassSelector(*args, **kwargs).do_model())
    
    
    
def create_process(*args, **kwargs): 
    parent_conn, child_conn   = mp.Pipe()
    process     = mp.Process(target=selector_procedure, args=(child_conn, args, kwargs))        
    return ClassSelectorProcess(process, parent_conn)
# End

        
        
if __name__ == '__main__':
    package_name        = sys.argv[1]
    module_name         = sys.argv[2]
    base_class_name     = sys.argv[3]
    mod                 = importlib.import_module(module_name)
    base_class_object   = getattr(mod, base_class_name)
    root = Tk()
    root.withdraw()
    class_selector = ClassSelector(package_name, base_class_object) 
    for s in class_selector.do_model():
        print(s)
    
        
    