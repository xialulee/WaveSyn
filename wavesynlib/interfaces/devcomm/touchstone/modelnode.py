# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 13:45:18 2016

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import os
import csv
import numpy
from skrf.io.touchstone import Touchstone

from wavesynlib.languagecenter.wavesynscript import Scripting, FileManipulator, FileManager


class TouchstoneFileManipulator(FileManipulator):
    def __init__(self, *args, **kwargs):
        FileManipulator.__init__(self, *args, **kwargs)
                    
    @Scripting.printable
    def to_csv(self, csv_filename, dB=True, angle='rad', unwrap=False):
        csv_filename = self.root_node.dialogs.support_ask_saveas_filename(
            csv_filename, 
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')],
            defaultextension='.csv',
            initialdir=os.path.split(self.filename)[0]
        )        
        
        s2p = Touchstone(str(self.filename))
        f, s = s2p.get_sparameter_arrays()
        
        if angle == 'rad':            
            convert_unit = lambda x: x
        elif angle in ('deg', 'degree'):
            convert_unit = numpy.rad2deg
        else:
            raise TypeError('Angle unit not supported.')
            
        if dB:
            get_mag = lambda x: 20*numpy.log10(numpy.abs(x))
        else:
            get_mag = numpy.abs
            
        if unwrap:
            get_unwrap = numpy.unwrap
        else:
            get_unwrap = lambda x: x
            
        X, Y, Z = s.shape
        
        data_list = []
        
        for z in range(Z):
            for y in range(Y):
                data_list.append((get_mag(s[:, y, z]), convert_unit(get_unwrap(numpy.angle(s[:, y, z])))))
        
        with open(csv_filename, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Freq'] + ['Abs', 'Angle']*len(data_list))
            for index, freq in enumerate(f):
                row = [freq]
                for item in data_list:
                    row.append(item[0][index])
                    row.append(item[1][index])
                writer.writerow(row)        


class TouchstoneFileManager(FileManager):
    def __init__(self, *args, **kwargs):
        kwargs['filetypes'] = [('Touchstone Files', '*.s2p'), ('All Files', '*.*')]
        kwargs['manipulator_class'] = TouchstoneFileManipulator
        FileManager.__init__(self, *args, **kwargs)
        
