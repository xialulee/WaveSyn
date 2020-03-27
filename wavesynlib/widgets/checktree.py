from tkinter import tix
import random

from wavesynlib.languagecenter.utils import MethodDelegator



class CheckTree: 
    class TreeNode:
        __slots__ = ['bind_object', 'children']
        
        def __init__(self, bind_object=None, children=None):
            self.bind_object = bind_object
            self.children = {} if children is None else children
    
    def __init__(self, *args, **kwargs):
        bind_object = kwargs.pop('bind_object', None)        
        tree_view = tix.CheckList(*args, **kwargs)
        tree_view['browsecmd'] = self._on_select
        self.__tree_view = tree_view
        self.__tree_model = self.TreeNode(bind_object)
        
    @property
    def tree_view(self):
        return self.__tree_view
        
    @property
    def tree_model(self):
        return self.__tree_model
        
    def _get_node_dict(self, path):
        path_list = path.split('.')
        tree_model = self.__tree_model
        node = tree_model
        for node_name in path_list:
            node = node.children[node_name]
        return node
        
    def add(self, 
            parent_node=None, node_status=False, bind_object=None, **kwargs):
        parent_node = str(parent_node) if parent_node else None
        node = self.__tree_model        
        if parent_node is not None:
            node = self._get_node_dict(parent_node)
        
        upper_bound = 1000000
        for k in range(upper_bound):
            name = str(random.randint(0, upper_bound))
            if name not in node.children:
                break

        tree_view = self.__tree_view
        if parent_node is not None:
            path = '.'.join((parent_node, name))
        else:
            path = str(name)
        tree_view.hlist.add(path, **kwargs)
        status = 'on' if node_status else 'off'
        tree_view.setstatus(path, status)
        tree_view.autosetmode()
        node.children[name] = self.TreeNode(bind_object)
        return path
        
    def _on_select(self, path):
        tree_view = self.__tree_view
        
        def set_status(path):
            status = tree_view.getstatus(path)
            node = self._get_node_dict(path)
            for child in node.children:
                full_path = '.'.join((path, child))
                tree_view.setstatus(full_path, status)
                set_status(full_path)
                
        set_status(path)
        
    for method_name in ['pack', 'config']:
        locals()[method_name] = MethodDelegator('tree_view', method_name)
        


