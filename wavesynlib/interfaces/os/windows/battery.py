# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 17:54:13 2017

@author: Feng-cong Li
"""

from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.interfaces.os.windows.wmi import SWbemSink



class EventSink(SWbemSink):
    def on_object_ready(self, wbem_object, context):
        print('on_object_ready')
    
    
    def on_completed(self, hresult, error_object, context):
        pass
    
    
    def on_progress(self, upper_bound, current, message, context):
        pass
    
    
    def on_object_put(self, object_path, context):
        pass



class Battery(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    def on_connect(self):
        self.root_node.interfaces.os.windows.wmi.set_sink(EventSink(), "SELECT * FROM __InstanceModificationEvent WITHIN 1 WHERE TargetInstance ISA 'Win32_Battery'")
        