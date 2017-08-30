# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 12:14:21 2015

@author: Feng-cong Li
"""
import json
import subprocess as sp
from wavesynlib.languagecenter.powershell import ExprTranslator
from wavesynlib.languagecenter.wavesynscript import Scripting, ModelNode



def execute(command):
    ps = sp.Popen(
        ['powershell', '-Command', command], 
        stdin=sp.PIPE, 
        stdout=sp.PIPE, 
        stderr=sp.PIPE)
    stdout, stderr  = ps.communicate()
    errorlevel      = ps.wait()
    return (stdout, stderr, errorlevel)



class Command(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with self.attribute_lock:
            self._command_list = []
            
            
    def __call__(self, command, *args):
        del self._command_list[:]
        new_obj = Command()
        new_obj.node_name = self.node_name
        new_obj.parent_node = self.parent_node
        new_obj._command_list.append(('command', command, args))
        return new_obj
    
    
    def __check_command(self):
        if not (self._command_list and self._command_list[0][0]=='command'):
            raise ValueError('Lack a command.')
        
        
    def select(self, expr):
        self.__check_command()
        self._command_list.append(('select', expr))
        return self
        
        
    def where(self, expr, lang='python'):
        self.__check_command()
        self._command_list.append(('where', expr, lang))
        return self
        
        
    @property
    def node_path(self):
        self_path = super().node_path
        temp_list = [self_path]
        if self._command_list[0][2]:
            temp_list.append(f'({repr(self._command_list[0][1])}{Scripting.convert_args_to_str(self._command_list[0][2])})')
        else:
            temp_list.append(f'({repr(self._command_list[0][1])})')
        for item in self._command_list[1:]:
            if item[0] == 'select':
                temp_list.append(f'.select({repr(item[1])})')
            elif item[0] == 'where':
                temp_list.append(f'.where({repr(item[1])}, lang={repr(item[2])})')
        return ''.join(temp_list)
        
        
    @Scripting.printable
    def run(self):
        temp_list = []
        for item in self._command_list:
            if item[0] == 'command':
                com = [item[1]]
                com.extend(item[2])
                com = ' '.join(com)
                temp_list.append(com)
            elif item[0] == 'select':
                if not isinstance(item[1], str):
                    expr = ','.join(item[1])
                else:
                    expr = item[1]
                temp_list.append(f'| select {expr}')
            elif item[0] == 'where':
                if item[2].lower() in ('py', 'python'):
                    expr = ExprTranslator.translate(item[1])
                else:
                    expr = item[1]
                temp_list.append(f'| where{{{expr}}}')
        com = ' '.join(temp_list)
        com = f'{com} | ConvertTo-Json'
        stdout, stderr, errorlevel = execute(com)
        return json.loads(stdout), stderr, errorlevel
    
    
    
class Powershell(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = Command()

