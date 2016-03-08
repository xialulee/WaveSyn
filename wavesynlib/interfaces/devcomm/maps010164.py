# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 18:33:22 2016

@author: Feng-cong Li

MAPS-010164 is a Digital Shifter and its typical applications include communications and phased array radar.
"""
from __future__ import print_function, division, unicode_literals

from math import pi

import RPi.GPIO as GPIO

from wavesynlib.interfaces.devcomm.raspberrypi import SimpleSPIWriter


class SPI(object):
    def __init__(self, clk_pin, data_pin, le_pin, chip_num=1):
        self._clk_pin = clk_pin
        self._data_pin = data_pin
        self._le_pin = le_pin
        self._chip_num = chip_num
        self._angles = [0] * chip_num
        self._writer = SimpleSPIWriter(clk_pin, data_pin, le_pin)
        
    @property
    def _clock(self):
        raise NotImplementedError
        
    @_clock.setter
    def _clock(self, val):
        bit = GPIO.HIGH if val else GPIO.LOW
        GPIO.output(self._clk_pin, bit)
        
    def set_angle(self, angle, unit='deg', chip_index=0):
        if unit == 'rad':
            angle = angle / pi * 180
        elif unit == 'deg':
            pass
        else:
            raise NotImplementedError
            
        bits = int(angle / 5.6 + 0.5) 
        ret = bits * 5.6
        self._angles[chip_index] = bits

        # For multiple phase shifters connected via daisy chain.
        with self._writer.latch_enable:
            for k in range(self._chip_num):
                self._writer.write_without_latch(self._angles[k], bit_width=6, msb_first=True)
        
        return ret
