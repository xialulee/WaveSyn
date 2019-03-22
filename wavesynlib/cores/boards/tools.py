# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 17:14:01 2019

@author: Feng-cong Li
"""

import json
from pathlib import Path



class Board:
    def __init__(self, name=None, info_path=None, info_file=None):
        if name:
            info_path = Path(__file__).parent / (name.lower()+".json")
            
        if info_path:
            with open(info_path, 'r') as f:
                self.__info = json.loads(f.read())
        else:
            self.__info = json.loads(info_file.read())
            
        if self.__info['IDE'] == 'Quartus':
            self.__assign_single_pin = self.__quartus_assign_single_pin
            self.__assign_pins = self.__quartus_assign_pins
            
            
    @property
    def info(self):
        return self.__info
    
    
    def __get_pin_records(self, pin_alias):
        return [record 
                    for record in self.__info['pin info'] 
                        if record['alias'] == pin_alias]
    
    
    def __quartus_assign_single_pin(self, pin_alias, port_name):
        pin_records = self.__get_pin_records(pin_alias)
        if len(pin_records) != 1:
            raise ValueError(f'{pin_alias} mismatch.')
        return [f'set_location_assignment {pin_records[0]["name"]} -to {port_name}']
    
    
    def __quartus_assign_pins(self, pin_alias, pin_range, port_name, port_range):
        if len(pin_range) != len(port_range):
            raise ValueError(f'{pin_alias} mismatch.')
            
        pin_records = self.__get_pin_records(pin_alias)
        pin_dict = {record['index'] : record['name'] 
                        for record in pin_records 
                            if record['index'] in pin_range}
        
        result = []
        for pin_idx, port_idx in zip(pin_range, port_range):
            result.append(f'set_location_assignment {pin_dict[pin_idx]} -to {port_name}[{port_idx}]')
        return result
    
    
    def pin_assign(self, assignments, tcl_path=None, tcl_file=None):
        result = []
        for pin_info, port_info in assignments:
            if isinstance(port_info, str):
                result += self.__assign_single_pin(pin_info[0], port_info)
            else:
                result += self.__assign_pins(
                        pin_alias=pin_info[0], 
                        pin_range=pin_info[1], 
                        port_name=port_info[0],
                        port_range=port_info[1])
                
        result = '\n'.join(result)
                
        if tcl_path:
            with open(tcl_path, 'w') as f:
                f.write(result)
        elif tcl_file:
            tcl_file.write(result)
        else:
            return result
