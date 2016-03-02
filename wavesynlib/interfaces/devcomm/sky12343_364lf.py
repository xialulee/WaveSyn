# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 16:08:47 2016

@author: Feng-cong Li

SKY12343-364LF is a digital anttenuator.
"""
from __future__ import print_function, division, unicode_literals

from time import sleep

import RPi.GPIO as GPIO

class SPI(object):
    def __init__(self, clk_pin, data_pin, latch_pin, a0_pin, a1_pin, a2_pin, addr):
        self._clk_pin = clk_pin
        self._data_pin = data_pin
        self._latch_pin = latch_pin
        self._a0_pin = a0_pin
        self._a1_pin = a1_pin
        self._a2_pin = a2_pin
        self._addr = addr
        GPIO.output(latch_pin, GPIO.LOW)
        
    @property
    def _clock(self):
        raise NotImplementedError
        
    @_clock.setter
    def _clock(self, val):
        bit = GPIO.HIGH if val else GPIO.LOW
        GPIO.output(self._clk_pin, bit)
        
    def set_attenuation(self, att):
        att = int(att / 0.25)
        if att > 127:
            raise ValueError('Attenuation out of range.')
        ret = att * 0.25
        
        addr = self._addr
        buf = (addr << 8) + att
        GPIO.output(self._latch_pin, GPIO.LOW)
        
        for k in range(16):
            self._clock = 0
            bit = GPIO.HIGH if buf & 1 else GPIO.LOW
            GPIO.output(self._data_pin, bit)
            sleep(0.0005)
            buf >>= 1
            self._clock = 1
            sleep(0.0005)
            
        GPIO.output(self._latch_pin, GPIO.HIGH)
        sleep(0.001)
        GPIO.output(self._latch_pin, GPIO.LOW)
        
        return ret
