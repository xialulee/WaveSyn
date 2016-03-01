# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 18:33:22 2016

@author: Feng-cong Li

MAPS-010164 is a Digital Shifter and its typical applications include communications and phased array radar.
"""
from __future__ import print_function, division, unicode_literals

from math import pi
from time import sleep

import RPi.GPIO as GPIO


class SPI(object):
    def __init__(self, clk_pin, data_pin, le_pin):
        self._clk_pin = clk_pin
        self._data_pin = data_pin
        self._le_pin = le_pin
        
    @property
    def _clock(self):
        raise NotImplementedError
        
    @_clock.setter
    def _clock(self, val):
        bit = GPIO.HIGH if val else GPIO.LOW
        GPIO.output(self._clk_pin, bit)
        
    def set_angle(self, angle, unit='deg'):
        if unit == 'rad':
            angle = angle / pi * 180
        elif unit == 'deg':
            pass
        else:
            raise NotImplementedError
            
        bits = int(angle / 5.6) 
        ret = bits * 5.6
        mask = 0x20
        
        GPIO.output(self._le_pin, GPIO.LOW)        
        
        for k in range(6):
            self._clock = 0
            bit = GPIO.HIGH if bits & mask else GPIO.LOW
            GPIO.output(self._data_pin, bit)
            sleep(0.0005)
            mask >>= 1
            self._clock = 1
            sleep(0.0005) # Hold for a while
            
        GPIO.output(self._le_pin, GPIO.HIGH)
        sleep(0.001)
        GPIO.output(self._le_pin, GPIO.LOW)
        
        return ret