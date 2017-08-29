# -*- coding: utf-8 -*-
"""
Created on Thu Sep 01 13:41:37 2016

@author: Feng-cong Li
"""
from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting



class ModeInfo:
    __slot__ = ('name', 'multiline', 'mode_object')
    
    def __init__(self, name, multiline, mode_object):
        self.name = name
        self.multiline = multiline
        self.mode_object = mode_object
        
        
    
class CodeInfo:
    __slot__ = ('mode_info', 'code')
    
    

# single line modes
class SystemShell(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with self.attribute_lock:
            self.info = ModeInfo('system_shell', False, self)
            
    
    def test(self, code):
        code = code.strip()
        if code and code[0]=='!':
            return self.info
        else:
            return False
        
            
    def run(self, code):
        Scripting.root_node.execute(code)
        
        
    def translate(self, code):
        if not self.test(code):
            raise TypeError('Code is not in mode SystemShell.')
        node_path = self.node_path
        return f'{node_path}.run({repr(code)})'
# end single line modes


# multiline modes
# end multiline modes


class ModesNode(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        mode_classes = [SystemShell]
        self.__modes = []
        for mode_class in mode_classes:
            mode_object = mode_class()
            setattr(self, mode_object.info.name, mode_object)
            self.__modes.append(mode_object)
            
            
    @Scripting.printable
    def run(self, code):
        right_mode = None
        for mode in self.__modes:
            if mode.test(code):
                right_mode= mode
                break
        
        if right_mode:
            Scripting.root_node.print_tip([{'type':'text', 'content':\
f'''The mode of the code is recognized as {right_mode.info.name}. 
The actual code executed is listed as follows:

{right_mode.translate(code)}

'''}]) # To Do: The output is stored in ...
            right_mode.run(code)
        else:
            raise TypeError('The mode of the code is unrecognizable.')
        
        