# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 19:19:48 2018

@author: Feng-cong Li
"""

import numpy as np
from reikna.core import Transformation, Parameter, Annotation, Type
from reikna.cluda import functions



def unimod_gen(size, single=True):
    '''Generate a reikna transform which unimodularize a complex number.'''
    if single:
        dtype = np.complex64
    else:
        dtype = np.complex128
    unimod = Transformation(
        [
             Parameter('output', Annotation(Type(dtype, size), 'o')),
             Parameter('input', Annotation(Type(dtype, size), 'i'))
        ],
        '''
        ${input.ctype} val = ${input.load_same};       
        ${output.store_same}(${polar_unit}(atan2(val.y, val.x)));
        ''',
        render_kwds=dict(polar_unit=functions.polar_unit(
                dtype=np.float32 if single else np.double))
    )
    return unimod