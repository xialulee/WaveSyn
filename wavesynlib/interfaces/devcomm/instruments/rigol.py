# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 15:07:51 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import csv
import numpy as np

from wavesynlib.interfaces.devcomm.instruments.visainterface import get_resource_manager


class DSA1030(object):
    def __init__(self, name=None):
        self.__name = name
        self.__instrument = None
        
        
    def connect(self, name=None):
        if name is None:
            name = self.__name
        else:
            self.__name = name
        
        if name is None:
            raise ValueError('The name of the instrument is needed.')
            
        rm = get_resource_manager()
        inst = rm.open_resource(name)
        self.__instrument = inst
    

    @property
    def instrument(self):
        return self.__instrument


    @property
    def frequency_start(self):
        return float(self.__instrument.ask(':SENS:FREQ:STAR?'))
        
        
    @property
    def frequency_stop(self):
        return float(self.__instrument.ask(':SENS:FREQ:STOP?'))
        
    
    @property
    def frequency_span(self):
        return float(self.__instrument.ask(':SENS:FREQ:SPAN?'))
        
    
    @property
    def frequency_center(self):
        return float(self.__instrument.ask(':SENS:FREQ:CENT?'))
        
        
    @property
    def traces(self):
        reader = csv.reader([self.__instrument.ask(':TRAC? '+'TRACE1')])
        data = reader.next()
        data[0] = data[0].split()[-1]
        return [np.array([float(d) for d in data])]
