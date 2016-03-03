# -*- coding: utf-8 -*-
"""
Created on Thu Mar 03 11:00:17 2016

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

from time import sleep

import RPi.GPIO as GPIO

class SimpleSPIWriter(object):
    '''At this point we do not have any mechanism for adjusting timing parameters
because Python operations are rather slow compared with many modern chips' interfaces.
'''
    def __init__(self, clk_pin, data_pin, le_pin):
        self.__clk_pin = clk_pin
        self.__data_pin = data_pin
        self.__le_pin = le_pin
        self._le = 0
        self._data = 0
        self._clk = 0
        
    def __write_pin(pin, val):
        bit = GPIO.HIGH if val else GPIO.LOW
        GPIO.output(pin, bit)
        
        
    @property
    def _clk(self):
        raise NotImplementedError
        
    @_clk.setter
    def _clk(self, val):
        self.__write_pin(self.__clk_pin, val)
        
        
    @property
    def _data(self):
        raise NotImplementedError
        
    @_data.setter
    def _data(self, val):
        self.__write_pin(self.__data_pin, val)
        
        
    @property
    def _le(self):
        raise NotImplementedError
        
    @_le.setter
    def _le(self, val):
        self.__write_pin(self.__le_pin, val)
        
        
    def write(self, data, bit_width, msb_first):
        buf = data & ((1 << bit_width-1) - 1)
        mask = 1 << bit_width-1 if msb_first else 1
        
        self._le = 0
        self._clk = 0
        for k in range(bit_width):
            # Prepare data before CLK posedge
            self._data = buf & mask
            # make a posedge of CLK
            self._clk = 1
            
            if msb_first:
                buf <<= 1
            else:
                buf >>= 1
                
            self._clk = 0
            
        # make a posedge of LE
        self._le = 1
        self._le = 0