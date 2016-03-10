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
    def to_csv(self, csv_filename, dB=True):
        csv_filename = self.root_node.dialogs.support_ask_saveas_filename(
            csv_filename, 
            filetypes=[('CSV Files', '*.csv'), ('All Files', '*.*')],
            defaultextension='.csv',
            initialdir=os.path.split(self.filename)[0]
        )        
        
        s2p = Touchstone(str(self.filename))
        f, s = s2p.get_sparameter_arrays()
        with open(csv_filename, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            num_elements = len(s[0].flatten())
            writer.writerow(['Freq'] + ['Abs', 'Angle']*num_elements)
            for index, freq in enumerate(f):
                row = [freq]
                s_row = s[index].T.flatten()
                for s_item in s_row:
                    mag = numpy.abs(s_item)
                    if dB:
                        mag = 20 * numpy.log10(mag)
                    row.append(mag)
                    row.append(numpy.angle(s_item))
                writer.writerow(row)        


class TouchstoneFileManager(FileManager):
    def __init__(self, *args, **kwargs):
        kwargs['filetypes'] = [('Touchstone Files', '*.s2p'), ('All Files', '*.*')]
        kwargs['manipulator_class'] = TouchstoneFileManipulator
        FileManager.__init__(self, *args, **kwargs)
        
