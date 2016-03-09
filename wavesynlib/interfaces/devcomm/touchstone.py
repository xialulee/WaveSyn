# -*- coding: utf-8 -*-
"""
Created on Wed Mar 09 13:45:18 2016

@author: Feng-cong Li
"""

from skrf.io.touchstone import Touchstone
import csv
import numpy

def s2p_to_csv(s2p_filename, csv_filename, dB=True):
    s2p = Touchstone(s2p_filename)
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