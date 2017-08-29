# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 17:54:13 2017

@author: Feng-cong Li
"""
from wavesynlib.languagecenter.wavesynscript import ModelNode
from wavesynlib.interfaces.os.windows.wmi import SWbemSink



class EventSink(SWbemSink):    
    def on_object_ready(self, wbem_object, context):
        status = wbem_object.Properties_['TargetInstance'].Value.Properties_['BatteryStatus'].Value
        print(
            {
                1: 'Discharging',
                2: 'Connected to AC',
                3: 'Fully charged',
                4: 'Currently low',
                5: 'Currently critically low',
                6: 'Currently charging',
                7: 'Currently charging and has high charge',
                8: 'Currently charging and has low charge',
                9: 'Currently charging and has critically low charge',
                10: 'Unknown',
                11: 'Partially charged'
            }[status]
        )
    
    
    def on_completed(self, hresult, error_object, context):
        pass
    
    
    def on_progress(self, upper_bound, current, message, context):
        pass
    
    
    def on_object_put(self, object_path, context):
        pass



class Battery(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__event_sink = None
        
        
    def on_connect(self):
        self.__event_sink = EventSink()
        self.root_node.interfaces.os.windows.wmi.set_sink(
            self.__event_sink, 
            "SELECT * FROM __InstanceModificationEvent WITHIN 30 WHERE TargetInstance ISA 'Win32_Battery'")
        