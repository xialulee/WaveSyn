# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 23:07:59 2016

@author: Feng-cong Li
"""
import sys
from pathlib import Path
from importlib import import_module

import collections

import hy
from hy.contrib.hy_repr import hy_repr

from wavesynlib.languagecenter.utils import MethodLock
from wavesynlib.languagecenter.designpatterns import Observable

from .hydatatypes import Constant, Constants, ModelNode, NodeDict, model_tree_monitor
        

                
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
        filename = dialogs.constant_handler_ASK_OPEN_FILENAME(filename, filetypes=self.filetypes)
        filename = dialogs.constant_handler_ASK_ORDERED_FILES(filename, filetypes=self.filetypes)
        filename = dialogs.constant_handler_ASK_FILES(filename, filetypes=self.filetypes)        
        
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
        


def _print_replacement_of_constant(const, value):
    show_tips = Scripting.root_node.gui.console.show_tips
    show_tips([
        {'type':'text', 'content':f'''\
The actual value of the place where {const.name} holds is
'''}])
    if isinstance(value, Path):
        if value.is_dir():
            show_tips([{'type':'directories', 'content':[str(value)]}], prompt=False)
        else:
            show_tips([{'type':'file_list', 'content':[str(value)]}], prompt=False)
    else:
        show_tips([{'type':'text', 'content':repr(value)}], prompt=False)
    

    
def constant_handler(print_replacement=True, doc=None):
    '''This is a decorator with an argument.
It functionality is help methods handling constants by fill in the actual value
hold by a constant.
'''    
    prefix = 'constant_handler_'

    def _constant_handler(func):
        # Automatic constants generation based on method names. 
        func_name = func.__name__
        if not func_name.startswith(prefix):
            raise NameError(f'The name of a method which handles a constant should starts with {prefix}')
        constant_name = func_name[len(prefix):]
        if constant_name != constant_name.upper():
            raise NameError('The name of a constant should be upper case.')
        
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
        
        

class Scripting(ModelNode):
    _xmlrpcexport_  = []    
    
    root_name = 'wavesyn' # The name of the object model tree's root
    root_node = None
    _namespace = {}
    namespaces = {'locals':_namespace, 'globals':_namespace}
    
    _print_code_flag = False
    _console_call = False

    
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


    @staticmethod
    def hy_convert_args_to_str(*args, **kwargs):
        def arg_to_str(arg):
            if isinstance(arg, ScriptCode):
                # To-Do: Handling ScriptCode correctly.
                return arg.code
            elif isinstance(arg, Constant):
                return f"{Scripting.root_name}.lang_center.wavesynscript.constants.{arg.name}"
            else:
                return hy_repr(arg)
        str_args   = ' '.join([arg_to_str(arg) for arg in args])
        str_kwargs = ' '.join([f":{key} {arg_to_str(kwargs[key])}" for key in kwargs]) if kwargs else ""

        if str_args and str_kwargs:
            result = f"{str_args} {str_kwargs}"
        else:
            result = str_args if str_args else str_kwargs
        return result
    
        
    def __init__(self, root_node):
        super().__init__()
        self.__root_node = root_node
        
            
    def executeFile(self, filename):
        exec(compile(open(filename, "rb").read(), filename, 'exec'), 
             self.namespaces['globals'], 
             self.namespaces['locals'])

        
    @classmethod
    def debug_print(cls, *args, **kwargs):
        cls.root_node.gui.console.debug_window.print(*args, **kwargs)



class WaveSynScriptAPIMethod:
    def __init__(self, obj, original_method, thread_safe):
        self.__original = original_method
        self.__name__ = original_method.__name__
        self.__obj = obj
        self.__thread_safe = thread_safe


    @property
    def original(self): return self.__original

    @property
    def obj(self): return self.__obj


    def __call__(self, *args, **kwargs):
        obj = self.__obj
        root = obj.root_node
        original = self.__original
        name = self.__name__
        if Scripting._print_code_flag:
            try:
                # Set False preventing recursive.
                Scripting._print_code_flag = False
                display_language = root.lang_center.wavesynscript.display_language
                expr_str = f"{obj.node_path}.{name}({Scripting.convert_args_to_str(*args, **kwargs)})"
                if display_language == "python":
                    display_str = expr_str
                elif display_language == "hy":
                    display_str = f"(.{name} {obj.hy_node_path} {Scripting.hy_convert_args_to_str(*args, **kwargs)})"
                ret = root.lang_center.wavesynscript.display_and_eval(expr=expr_str, display=display_str)
            finally:
                # Restore
                Scripting._print_code_flag = True
        else:
            if self.__thread_safe:
                ret = original(obj, *args, **kwargs)
            else:
                ret = root.thread_manager.main_thread_do(lambda:original(obj, *args, **kwargs))
        return ret


    def new_thread_run(self, *args, **kwargs):
        if not self.__thread_safe:
            raise TypeError("This method is not thread-safe and not supports new_thread_run.")
        obj = self.__obj
        root = obj.root_node
        original = self.__original
        name = self.__name__
        if Scripting._print_code_flag:
            try:
                # Set False preventing recursive.
                Scripting._print_code_flag = False
                display_language = root.lang_center.wavesynscript.display_language
                expr_str = f"{obj.node_path}.{name}.new_thread_run({Scripting.convert_args_to_str(*args, **kwargs)})"
                if display_language == "python":
                    display_str = expr_str
                elif display_language == "hy":
                    display_str = f"(.new_thread_run {obj.hy_node_path[:-1]} {name}) {Scripting.hy_convert_args_to_str(*args, **kwargs)})"
                ret = root.lang_center.wavesynscript.display_and_eval(expr=expr_str, display=display_str)
                return ret
            finally:
                # Restore
                Scripting._print_code_flag = True
        else:
            return root.thread_manager.new_thread_do(lambda:original(obj, *args, **kwargs))


    def help(self):
        print(self.__doc__)


    def panel(self):
        caller = sys._getframe(1)
        argmap = self.__obj.root_node.create_arg_panel_for_func(self.__original)
        for name in argmap:
            argmap[name] = eval(argmap[name], caller.f_globals, caller.f_locals)
        with code_printer():
            return self.__call__(**argmap)



class WaveSynScriptAPI:
    def __init__(self, *args, **kwargs):
        if not kwargs and (len(args)==1):
            self.__make_default(args[0])
        elif kwargs:
            if "thread_safe" in kwargs:
                self.__thread_safe = kwargs["thread_safe"]
            else:
                self.__thread_safe = False
            if "silent" in kwargs:
                self.__silent = kwargs["silent"]
            else:
                self.__silent = False


    def __copy_original_info(self):
        self.__doc__  = self.__original.__doc__
        self.__name__ = self.__original.__name__


    def __make_default(self, original):
        self.__original    = original
        self.__copy_original_info()
        self.__thread_safe = False
        self.__silent = False


    def __get__(self, obj, type=None):
        method = WaveSynScriptAPIMethod(obj, self.__original, self.__thread_safe)
        method.__name__ = self.__name__
        method.__doc__  = self.__doc__
        return method


    def __call__(self, original):
        self.__original = original
        self.__copy_original_info()
        return self



class CodePrinter:
    def __init__(self, print_=True):
        self.__print = print_

            
    def __enter__(self):
        Scripting._print_code_flag = self.__print
        if "________wavesyn_console_namespace" in sys._getframe(2).f_locals:
            Scripting._console_call = True
        
        
    def __exit__(self, *dumb):
        Scripting._print_code_flag = False
        Scripting._console_call = False



_code_printer = CodePrinter(True)
_null_printer = CodePrinter(False)

def code_printer(print_=True):
    if print_:
        return _code_printer
    else:
        return _null_printer



# End Scripting Sub-System
        
