# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 15:48:15 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting, code_printer
from wavesynlib.languagecenter.designpatterns import SimpleObserver
from wavesynlib.languagecenter.utils import eval_format
from wavesynlib.interfaces.timer.tk import TkTimer

# To Do: provide a ls command which list all the actions (and can be clicked or changed.)
class ActionManager(ModelNode):
    def __init__(self, *args, **kwargs):
        ModelNode.__init__(self, *args, **kwargs)
        with self.attribute_lock:
            self.current_actions = {}

    def add_action(self, action):
        self.current_actions[id(action)] = action

    @Scripting.printable
    def cancel(self, action_id):
        try:
            action = self.current_actions[action_id]
        except KeyError:
            self.root_node.print_tip([
                {'type':'text', 
                 'content':'This action has already been finished or cancelled.'}])
        else:
            action.cancel()
            del self.current_actions[action_id]
        
    @Scripting.printable
    def cancel_all(self):
        for key in self.current_actions:
            self.cancel(key)
        self.current_actions = {}         
        

class DoNode(ModelNode):
    def __init__(self, *args, **kwargs):
        self.__time_args = index = kwargs.pop('time_args')
        self.__type = type_ = kwargs.pop('type_')
        ModelNode.__init__(self, *args, **kwargs)

        try:                    
            self.__do = {'after':self.__do_once, 
                         'every': self.__repeat}[type_]
        except KeyError:
            raise TypeError('Not supported timer action.')
        
        hours = 0
        minutes = 0
        seconds = 0
        try: # index is a scalar, treat it as seconds.
            seconds = float(index)
        except TypeError:
            if index.step is None: # mm:ss
                minutes = index.start
                seconds = index.stop
            else: # hh:mm:ss
                hours = index.start
                minutes = index.stop
                seconds = index.step            
        duration = int((hours*3600 + minutes*60 + seconds) * 1000) # ms                    
        self.__duration = duration
        self.__hours = hours
        self.__minutes = minutes
        self.__seconds = seconds
        self.__first_call = True 
        
    @property
    def manager(self):
        node = self
        while True:
            node = node.parentNode
            if isinstance(node, ActionManager):
                return node
        
        
    def __do_once(self, func):
        @SimpleObserver
        def callback():
            if self.__first_call:
                self.__first_call = False
                return
            else:
                try:
                    func()
                finally:
                    self.manager.cancel(action_id=id(self))
            
        timer = self.__timer
        timer.counter = 2
        timer.interval = self.__duration
        timer.add_observer(callback)
        timer.active = True        
        
    def __repeat(self, func):
        func = SimpleObserver(func)
        timer = self.__timer
        timer.interval = self.__duration
        timer.add_observer(func)
        timer.active = True
                
    @Scripting.printable
    def do(self, func):
        self.__timer = TkTimer(widget=self.root_node.tk_root)
        self.__do(func)
        root = self.root_node
        type_ = self.__type
        duration = self.__duration
        
        def on_cancel_click(*args, **kwargs):
            with code_printer:
                self.manager.cancel(action_id=id(self))
        
        root.print_tip([
            {'type':'text', 'content': eval_format('\n  {self.node_path}')},
            {'type':'text', 'content': eval_format('  ID: {id(self)}')},
            {'type':'text', 'content': eval_format('  Type: {type_}')},
            {'type':'text', 'content': eval_format('  Duration: {duration}ms')},
            {'type':'link', 'content': 'Click here to Cancel This Action.',
             'command':on_cancel_click}
        ])
        
    @Scripting.printable
    def printf(self, format_, *args):
        string = format_ % args
        func = lambda: print(string)
        self.do(func)
        
    # To Do: implement a MessageBox method
        
    def cancel(self):
        self.__timer.active = False
                
    @property
    def node_path(self):
        hours = self.__hours
        minutes = self.__minutes
        seconds = self.__seconds
        return eval_format('{self.parentNode.node_path}[{hours}:{minutes}:{seconds}]')


class TimerActionNode(ModelNode):    
    def __init__(self, *args, **kwargs):
        self.__type = kwargs.pop('type_')
        ModelNode.__init__(self, *args, **kwargs)
        
    def __getitem__(self, index):
        do_node = DoNode(time_args=index, type_=self.__type)
        object.__setattr__(do_node, 'parentNode', self)
        do_node.lock_attribute('parentNode')
        do_node.manager.add_action(do_node)
        return do_node
       


                
