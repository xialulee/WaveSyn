# -*- coding: utf-8 -*-
"""
Created on Tue Dec 29 12:14:21 2015

@author: Feng-cong Li
"""
import json
import chardet
import subprocess as sp
from wavesynlib.languagecenter.powershell import ExprTranslator
from wavesynlib.languagecenter.wavesynscript import (
    Scripting, WaveSynScriptAPI, ModelNode, code_printer)



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
            
            
    def __call__(self, command, *args, **kwargs):
        del self._command_list[:]
        new_obj = Command()
        new_obj.node_name = self.node_name
        new_obj.parent_node = self.parent_node
        new_obj._command_list.append(('command', command, args, kwargs))
        return new_obj
    
    
    def __check_command(self):
        if not (self._command_list and self._command_list[0][0]=='command'):
            raise ValueError('Lack a command.')
            
            
    def pipe(self, command, *args, **kwargs):
        self.__check_command()
        self._command_list.append(('pipe', command, args, kwargs))
        return self            
        
        
    def select(self, expr):
        self.__check_command()
        self._command_list.append(('select', expr))
        return self
        
        
    def where(self, expr, lang='python'):
        self.__check_command()
        self._command_list.append(('where', expr, lang))
        return self
    
    
    def sort(self, *args, **kwargs):
        '''sort(
    ["casesensitive"],
    ["descending"],
    ["unique"],
    [property="name"],
    [culture="string"]
)
'''
        self.__check_command()
        self._command_list.append(('sort', args, kwargs))
        return self
    
    
    def map(self, expr, lang='python'):
        self.__check_command()
        self._command_list.append(('map', expr, lang))
        return self
        
        
    @property
    def node_path(self):
        self_path = super().node_path
        temp_list = [self_path]
        if self._command_list[0][2]:
            temp_list.append(f'({repr(self._command_list[0][1])}, {Scripting.convert_args_to_str(*self._command_list[0][2], **self._command_list[0][3])})')
        else:
            temp_list.append(f'({repr(self._command_list[0][1])})')
        for item in self._command_list[1:]:
            if item[0] == 'select':
                temp_list.append(f'.select({repr(item[1])})')
            elif item[0] == 'where':
                temp_list.append(f'.where({repr(item[1])}, lang={repr(item[2])})')
            elif item[0] == 'map':
                temp_list.append(f'.map({repr(item[1])}, lang={repr(item[2])})')
            elif item[0] == 'pipe':
                temp_list.append(f'.pipe({repr(item[1])}, {Scripting.convert_args_to_str(*item[2], **item[3])})')
            elif item[0] == 'sort':
                temp_list.append(f'.sort({Scripting.convert_args_to_str(*item[1], **item[2])})')
        return ''.join(temp_list)
    
    
    @WaveSynScriptAPI
    def get_command_string(self):
        temp_list = []
        for item in self._command_list:
            if item[0] in ('command', 'pipe'):
                com = [item[1]]
                com.extend(item[2])
                com = ' '.join(com)
                if item[0] == 'pipe':
                    com = '| '+com
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
            elif item[0] == 'sort':
                args = ' '.join([f'-{arg}' for arg in item[1]])
                kwargs = ' '.join([f'-{key} {item[2][key]}' for key in item[2]])
                temp_list.append(f'| sort {args} {kwargs}')
            elif item[0] == 'map':
                if item[2].lower() in ('py', 'python'):
                    expr = ExprTranslator.translate(item[1])
                else:
                    expr = item[1]
                temp_list.append(f'| foreach{{{expr}}}')
        com = ' '.join(temp_list)
        com = f'{com} | ConvertTo-Json'  
        return com
        
        
    @WaveSynScriptAPI
    def run(self):
        with code_printer(print_=False):
            com = self.get_command_string()
        stdout, stderr, errorlevel = execute(com)
        coding = chardet.detect(stdout)['encoding']
        stdout = stdout.decode(coding)
        stderr = stderr.decode(coding)
        return {'stdout':json.loads(stdout), 'stderr':stderr, 'errorlevel':errorlevel}
    
    
    
class Powershell(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command = Command()

