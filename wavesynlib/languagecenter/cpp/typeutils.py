from __future__ import annotations

from typing import get_type_hints
import ctypes



class Field:
    pass


def field(type_: type, anonymous:bool = False):
    # Todo: support bit field
    class TheField(Field):
        _type = type_
        _anonymous = anonymous
    return TheField



def ctype_build(type_, doc=''):
    '''\
This decorator is a helper for defining C struct/union datatypes.

An example:
@ctype_build('struct')
class XINPUT_GAMEPAD:
    wButtons: WORD
    bLeftTrigger: BYTE
    bRightTrigger: BYTE
    sThumbLX: SHORT
    sThumbLY: SHORT
    sThumbRX: SHORT
    sThumbRY: SHORT
'''
    type_ = type_.lower()
    
    def the_decorator(cls):
        field_desc = []
        anonymous = []
        for name, type_desc in get_type_hints(cls).items():
            if issubclass(type_desc, Field):
                if type_desc._anonymous:
                    anonymous.append(name)
                type_desc = type_desc._type
            field_desc.append((name, type_desc))
            
        if type_ in ('struct', 'structure'):
            base_class = ctypes.Structure
        elif type_ == 'union':
            base_class = ctypes.Union
        else:
            raise TypeError('Not supported type.')
        
        class TheType(base_class):
            if doc:
                __doc__ = doc
            if anonymous:
                _anonymous_ = anonymous
            _fields_ = field_desc
        return TheType    

    return the_decorator



class StructReader:
    """\
An util for reading struct data in a binary file. 
Not thread-safe. 
"""
    def __init__(self, struct_type):
        size = ctypes.sizeof(struct_type)
        arr  = ctypes.c_uint8 * size

        @ctype_build("union")
        class Helper:
            struct:   struct_type
            byte_arr: arr

        self.__helper = Helper()
        self.__size   = size


    def read(self, io_obj):
        self.__helper.byte_arr[:] = io_obj.read(self.__size)
        return self.__helper.struct
