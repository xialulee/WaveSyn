# -*- coding: utf-8 -*-
"""
Created on Sat May 13 13:46:19 2017

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

from jinja2 import Template


class Function(object):
    def __init__(self, func_name, ret_type, args, body):
        self.__func_name = func_name
        self.__ret_type = ret_type
        self.__args = args
        self.__body = Template(body)
        
        
    @property
    def args(self):
        return self.__args
        
        
    @property
    def func_name(self):
        return self.__func_name
        
        
    @property
    def ret_type(self):
        return self.__ret_type
        
        
    @property
    def body(self):
        return self.__body
        
        
    def to_code(self):
        body = self.__body.render(**{arg[1]:arg[1] for arg in self.__args}) 
        
        template = Template('''
{{ret_type}} {{func_name}}({{args}}){
    {{body}}
}
''')
        return template.render(
            func_name=self.__func_name,
            ret_type=self.__ret_type,
            args=', '.join(['{} {}'.format(*arg) for arg in self.__args]),
            body=body)
            
            
    def partial(self, func_name, **kwargs):
        remove_list = []
        for name in kwargs:
            for idx, n in enumerate(self.__args):
                if name == n[1]:
                    remove_list.append(idx)
                    break
            else:
                raise TypeError('Unexpected argument {}'.format(name))
                                
        render_args = {}
        for idx, a in enumerate(self.__args):
            if idx not in remove_list:
                render_args[a[1]] = '{{%s}}' % (a[1],)
            else:
                render_args[a[1]] = kwargs[a[1]]
        body = self.__body.render(render_args)        
        args = [arg for idx, arg in enumerate(self.__args) if idx not in remove_list]
        
        return Function(func_name, self.__ret_type, args, body)
        