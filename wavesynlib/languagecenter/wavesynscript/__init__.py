# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 23:07:59 2016

@author: Feng-cong Li
"""
import sys
from importlib import import_module

import collections

from wavesynlib.languagecenter.utils import MethodLock
from wavesynlib.languagecenter.designpatterns import Observable



# Object Model of the Scripting System
# It is a part of the scripting system.

class _ModelTreeMonitor(Observable):
    def __init__(self):
        super().__init__()
        
        
    def _on_add_node(self, node):
        self.notify_observers(node, 'add')
        
        
    def _on_remove_node(self, node):
        self.notify_observers(node, 'remove')
        
        
        
model_tree_monitor = _ModelTreeMonitor()
       
# How to implement a context manager? See:
# http://pypix.com/python/context-managers/        
class AttributeLock(object):
    def __init__(self, node):
        super().__init__()
        if not isinstance(node, ModelNode):
            raise TypeError('Only the instance of ModelNode is accepted.')
        self.node   = node
        
            
    def __enter__(self):
        self.node.attribute_auto_lock = True
        return self.node
    
        
    def __exit__(self, *dumb):
        self.node.attribute_auto_lock = False
        
        
        
# To Do: Implement an on_bind callback which is called when a node is connecting to the tree.    
class ModelNode:
    _xmlrpcexport_  = []    
    
    
    def __init__(self, *args, **kwargs):
        super().__init__()
        node_name = kwargs.get('node_name', '')
        is_root = kwargs.get('is_root', False)
        is_lazy = kwargs.get('is_lazy', False)
        if '_attribute_lock' not in self.__dict__:
            object.__setattr__(self, '_attribute_lock', set())
        self.parent_node = None
        self.__is_root = is_root
        self.__is_lazy = is_lazy
        if is_lazy:
            self.__module_name = kwargs.pop('module_name', None)
            self.__class_name = kwargs.pop('class_name', None)
            self.__class_object = kwargs.pop('class_object', None)
        self.node_name = node_name
        #self.attribute_auto_lock   = False
        
                
    def lock_attribute(self, attribute_name, lock=True):
        '''Lock a specified attribute, i.e. the attribute cannot be re-assigned.
For example:        
node.a = 0
node.lock_attribute("a")
If you try to give node.a a new value
node.a = 1
then an AttributeError will be raised.
'''
        if lock:
            self._attribute_lock.add(attribute_name)
        else:
            if attribute_name in self._attribute_lock:
                self._attribute_lock.remove(attribute_name)

        
    @property
    def attribute_lock(self):
        '''This attribute is in fact a context manager.
if the following statements are executed:
with node.attribute_lock:
  node.a = 0
then node will have a property named 'a', which cannot be re-assigned.
'''
        return AttributeLock(self)        

        
    @property
    def is_root(self):
        return self.__is_root

        
    @property
    def is_lazy(self):
        return self.__is_lazy

        
    def get_real_node(self):
        node = self
        if self.is_lazy:
            if self.__class_object is None:
                #mod = __import__(self.__module_name, globals(), locals(), [self.__class_name], -1)
                mod = import_module(self.__module_name)
                node = getattr(mod, self.__class_name)()
            else:
                node = self.__class_object()
        return node

        
    def __setattr__(self, key, val):
        if '_attribute_lock' not in self.__dict__:
            # This circumstance happens when __setattr__ called before __init__ being called.
            object.__setattr__(self, '_attribute_lock', set())
        if 'attribute_auto_lock' not in self.__dict__:
            object.__setattr__(self, 'attribute_auto_lock', False)
        if key in self._attribute_lock:
            raise AttributeError(f'Attribute "{key}" is unchangeable.')
        if isinstance(val, ModelNode) and not val.is_root and val.parent_node==None:
            val.node_name = val.node_name if val.node_name else key
            object.__setattr__(val, 'parent_node', self)
            
            # The autolock mechanism will lock the node after you attach it to the model tree.
            # A child node cannot change its parent
            val.lock_attribute('parent_node')
            # and the parent node's child node cannot be re-assinged. 
            self.lock_attribute(key)
            model_tree_monitor._on_add_node(val)
                    
        object.__setattr__(self, key, val)
        if self.attribute_auto_lock and key != 'attribute_auto_lock': # attribute_auto_lock cannot be locked
            self.lock_attribute(key)
        
        if isinstance(val, ModelNode):
            val.on_connect()

            
    def __getattribute__(self, attribute_name):
        attr = object.__getattribute__(self, attribute_name)
        if isinstance(attr, ModelNode) and attr.is_lazy:
            # Before replacing, unlock the attribute name.
            self.lock_attribute(attribute_name, lock=False)
            # Get the real node.
            attr = attr.get_real_node()
            # Replace.
            with self.attribute_lock:
                setattr(self, attribute_name, attr)
        return attr
        
        
    def on_connect(self):
        pass

        
    @property
    def node_path(self):
        if self.is_root:
            return self.node_name
        elif isinstance(self.parent_node, dict):
            return f'{self.parent_node.node_path}[{id(self)}]'
        else:
            return '.'.join((self.parent_node.node_path, self.node_name))

            
    @property
    def child_nodes(self):
        return {attribute_name:self.__dict__[attribute_name].node_path 
                for attribute_name in self.__dict__ 
                if isinstance(self.__dict__[attribute_name], ModelNode) 
                and attribute_name != 'parent_node'} 

            
    @property
    def root_node(self):
        node = self
                    
        while not node.is_root:
            node = node.parent_node
        return node
        

                
class Dict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        

# NodeDict
class NodeDict(ModelNode, Dict):
    _xmlrpcexport_  = []
    
    
    def __init__(self, node_name=''):
        super().__init__(node_name=node_name)
        
        
    def __setitem__(self, key, val):
        object.__setattr__(val, 'parent_node', self)
        val.lock_attribute('parent_node')
        model_tree_monitor._on_add_node(val)
        Dict.__setitem__(self, key, val)
        val.on_connect()
        
        
    def __delitem__(self, key):
        model_tree_monitor._on_remove_node(self[key])
        Dict.__delitem__(self, key)
        
        
    def pop(self, key):
        model_tree_monitor._on_remove_node(self[key])
        Dict.pop(self, key)
        


class List(list):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        

# NodeList       
class NodeList(ModelNode, List):
    _xmlrpcexport_  = []
    
    
    def __init__(self, node_name=''):
        super().__init__(node_name=node_name)
        self.__element_lock = True

    
    def lock_elements(self, lock=True):
        self.__element_lock = lock
        
        
    def append(self, val):
        object.__setattr__(val, 'parent_node', self)        
        List.append(self, val)
        val.index   = len(self) - 1
        val.lock_attribute('index')


    @property
    def element_lock(self):
        return self.__element_lock
    
        
    def __update_index(method):
        def func(self, *args, **kwargs):            
            try:
                ret = method(self, *args, **kwargs)
            finally:
                for index, val in enumerate(self):
                    val.lock_attribute('index', lock=False)
                    val.index   = index
                    val.lock_attribute('index', lock=True)
            return ret
        func.__name__   = method.__name__
        func.__doc__    = method.__doc__
        return func

    method_names = ['__delitem__', '__setitem__', 'pop', 'remove', 'reverse', 'sort', 'insert']

    for method_name in method_names:
        locals()[method_name]    = MethodLock(method=__update_index(getattr(list, method_name)), lockName='element_lock')    
# End Object Model
        
        

# More Node Types
# File Manager, Manipulator and List
# To Do: Implement ShortLivedNode, which will not be a former member of the ModelTree
class FileManipulator(ModelNode):
    def __init__(self, *args, **kwargs):
        filename = kwargs.pop('filename')
        ModelNode.__init__(self, *args, **kwargs)
        with self.attribute_lock:
            self.filename = filename
            
            
    @property
    def node_path(self):
        return f'{self.parent_node.node_path}["{self.filename}"]'
    
        
        
class FileList(ModelNode):
    def __init__(self, *args, **kwargs):
        filelist = kwargs.pop('filelist')
        super().__init__(*args, **kwargs)
        with self.attribute_lock:
            self.filelist = filelist
            
            
    @property
    def node_path(self):
        return f'{self.parent_node.node_path}{repr(self.filelist)}'
    
            
            
class FileManager(ModelNode):
    def __init__(self, *args, **kwargs):
        filetypes = kwargs.pop('filetypes')
        self.__manipulator_class = kwargs.pop('manipulator_class', None)        
        self.__list_class = kwargs.pop('list_class', None)
        super().__init__(*args, **kwargs)
        with self.attribute_lock:
            self.filetypes = filetypes
            
        
    def __getitem__(self, filename):
        dialogs = self.root_node.gui.dialogs
        filename = dialogs.ask_open_filename(filename, filetypes=self.filetypes)
        filename = dialogs.ask_ordered_files(filename, filetypes=self.filetypes)
        filename = dialogs.ask_files(filename, filetypes=self.filetypes)        
        
        if not filename:
            return
        if isinstance(filename, str):
            if self.__manipulator_class is None:
                raise NotImplementedError
            else:
                manipulator = self.__manipulator_class(filename=filename)
                object.__setattr__(manipulator, 'parent_node', self)
                manipulator.lock_attribute('parent_node')
                return manipulator
        elif isinstance(filename, collections.Iterable):
            if self.__list_class is None:
                raise NotImplementedError
            else:
                filelist = self.__list_class(filelist=filename)
                object.__setattr__(filelist, 'parent_node', self)
                filelist.lock_attribute('parent_node')
                return filelist
        else:
            raise NotImplementedError
# End More Node Types
        
        
# WaveSyn Script Constants
# To Do: move to datatypes
class Constant:
    __slots__ = ('__name', '__value', '__doc')
    __cache = {}
    
    
    def __new__(cls, name, value=None, doc=None):
        if name in cls.__cache:
            c = cls.__cache[name]
            if value != c.value:
                raise ValueError('Constant has already been initialized with a different value.')
            return c
        else:
            return object.__new__(cls)
        
    
    def __init__(self, name, value=None, doc=None):
        if name not in self.__cache:
            self.__name = name
            self.__value = value
            self.__doc = doc
            self.__cache[name] = self
            
            
    @property
    def name(self):
        return self.__name
    
        
    @property
    def value(self):
        return self.__value
    
    
    @property
    def doc(self):
        return self.__doc
    
    
    def help(self):
        print(self.doc)
        
 
       
constant_names = []


             
class Constants(object): 
    name_value_pairs = (                
        ('KEYSYM_MODIFIERS', {'Alt_L', 'Alt_R', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R'}),
        ('KEYSYM_CURSORKEYS', {
            'KP_Prior', 'KP_Next', 'KP_Home', 'KP_End', 
            'KP_Left', 'KP_Right', 'KP_Up', 'KP_Down', 
            'Left', 'Right', 'Up', 'Down', 
            'Home', 'End', 'Next', 'Prior'                
        })
    )
    
    for name, value in name_value_pairs:
        locals()[name] = Constant(name, value)      
        
    
    @classmethod
    def append_new_constant(cls, name, value=None, doc=None):
        setattr(cls, name, Constant(name, value, doc))
    # End Clipboard Constants
    


def _print_replacement_of_constant(const, value):
    Scripting.root_node.print_tip([{'type':'text', 'content':f'''
The actual value of the place where {const.name} holds is
  {repr(value)}'''}])
    

    
def constant_handler(print_replacement=True, doc=None):
    '''This is a decorator with an argument.
It functionality is help methods handling constants by fill in the actual value
hold by a constant.
'''    
    def _constant_handler(func):
        # Automatic constants generation based on method names. 
        constant_name = func.__name__.upper()
        Constants.append_new_constant(constant_name, doc=doc)
        constant = Constant(constant_name)
        #Wrapper function
        def f(self, arg, **kwargs):
            if arg is constant:
                arg = func(self, arg, **kwargs)
                if print_replacement:
                    _print_replacement_of_constant(constant, arg)
            return arg
        return f    
    return _constant_handler        
# End WaveSyn Script Constants
    


# Scripting Sub-System
class ScriptCode:
    def __init__(self, code):
        self.code = code
        
     
        
class PrintableDescriptor:
    def __init__(self, 
                 func, # The decorated func
                 original # The original method without decoration.
        ):
        self.__func = func
        self.__original = original # the original method without decoration.
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
        
    def __get__(self, obj, type=None):
        class PrintableMethod:
            def __init__(self, obj, func, original):
                self.__original = original
                self.__func = func
                self.__obj = obj
                
                
            def __call__(self, *args, **kwargs):
                return self.__func(self.__obj, *args, **kwargs)
            
            
            @property
            def panel(self):
                caller = sys._getframe(1)
                argmap = obj.root_node.create_arg_panel_for_func(self.__original)
                for name in argmap:
                    argmap[name] = eval(argmap[name], caller.f_globals, caller.f_locals)
                return self.__call__(**argmap)
                
        PrintableMethod.__name__ = self.__func.__name__
        PrintableMethod.__doc__ = self.__func.__doc__            
        m = PrintableMethod(obj, self.__func, self.__original)
        return m
      

        
class Scripting(ModelNode):
    _xmlrpcexport_  = []    
    
    root_name = 'wavesyn' # The name of the object model tree's root
    root_node = None
    namespace = {'locals':{}, 'globals':{}}
    
    _print_code_flag = False
    
    
    @staticmethod
    def convert_args_to_str(*args, **kwargs):
        def paramToStr(param):
            if isinstance(param, ScriptCode):
                return param.code
            elif isinstance(param, Constant):
                return f'{Scripting.root_name}.lang_center.wavesynscript.constants.{param.name}'
            else:
                return repr(param)
                
        strArgs = ', '.join([paramToStr(arg) for arg in args]) if args else ''
        strKwargs = ', '.join([f'{key}={paramToStr(kwargs[key])}' \
            for key in kwargs]) if kwargs else ''    
       
            
        if strArgs and strKwargs:
            params = f'{strArgs}, {strKwargs}'
        else:
            params = strArgs if strArgs else strKwargs
        return params
    
        
    def __init__(self, root_node):
        super().__init__()
        self.__root_node = root_node
        
            
    def executeFile(self, filename):
        exec(compile(open(filename, "rb").read(), filename, 'exec'), 
             self.namespace['globals'], 
             self.namespace['locals'])

        
    @classmethod    
    def printable(cls, method):
        def func(self, *args, **kwargs):
            if cls._print_code_flag:
                try:
                    cls._print_code_flag = False # Prevent recursive.
                    # To Do: 
                    # if current_thread is not main_thread:
                    #   put the node and arguments into a command slot
                    #   and the main thread will check the command queue periodically.
                    # This mechanism will guarentee the thread safety of wavesyn scripting system.
                    ret = cls.root_node.print_and_eval(
                        f'{self.node_path}.{method.__name__}({Scripting.convert_args_to_str(*args, **kwargs)})')
                finally:
                    cls._print_code_flag = True # Restore _print_code_flag settings.
            else:                          
                ret = method(self, *args, **kwargs)
            return ret
        func.__doc__    = method.__doc__
        func.__name__   = method.__name__
        return PrintableDescriptor(func, method)
    
    
    @classmethod
    def debug_print(cls, *args, **kwargs):
        cls.root_node.gui.console.debug_window.print(*args, **kwargs)
    


class CodePrinter:
    def __init__(self, print_=True):
        self.__print = print_

            
    def __enter__(self):
        Scripting._print_code_flag = self.__print
        
        
    def __exit__(self, *dumb):
        Scripting._print_code_flag = False



_code_printer = CodePrinter(True)
_null_printer = CodePrinter(False)

def code_printer(print_=True):
    if print_:
        return _code_printer
    else:
        return _null_printer



# End Scripting Sub-System
        
