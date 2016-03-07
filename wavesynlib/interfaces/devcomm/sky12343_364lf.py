# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 16:08:47 2016

@author: Feng-cong Li

SKY12343-364LF is a digital anttenuator.
"""
from __future__ import print_function, division, unicode_literals

from time import sleep

import RPi.GPIO as GPIO

from wavesynlib.interfaces.devcomm.raspberrypi import SimpleSPIWriter

class SPI(object):
    def __init__(self, clk_pin, data_pin, latch_pin, addr):
        self._clk_pin = clk_pin
        self._data_pin = data_pin
        self._latch_pin = latch_pin
        self._addr = addr
        self._writer = SimpleSPIWriter(clk_pin, data_pin, latch_pin)
        GPIO.output(latch_pin, GPIO.LOW)
        
    @property
    def _clock(self):
        raise NotImplementedError
        
    @_clock.setter
    def _clock(self, val):
        bit = GPIO.HIGH if val else GPIO.LOW
        GPIO.output(self._clk_pin, bit)
        
    def set_attenuation(self, att):
        att = int(att / 0.25 + 0.5)
        if att > 127:
            raise ValueError('Attenuation out of range.')
        ret = att * 0.25
        
        addr = self._addr
        buf = (addr << 8) + att

        self._writer.write(buf, bit_width=16, msb_first=False)
        
        return ret
