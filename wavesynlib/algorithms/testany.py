# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 17:35:21 2018

@author: Feng-cong Li
"""

import numpy as np

from reikna.fft import FFT
from reikna import cluda
from reikna.cluda import functions
from reikna.core import Transformation, Parameter, Annotation, Type


api = cluda.any_api()
thr = api.Thread.create()

size = 4





def unimod_gen(size, single=True):
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
        render_kwds=dict(polar_unit=functions.polar_unit(dtype=np.float32 if single else np.double))
    )
    return unimod

unimod = unimod_gen(size)

ffts = FFT(thr.array(size, dtype=np.complex64))
ffts.parameter.output.connect(unimod, unimod.input, uni=unimod.output)
ffts_unimod = ffts.compile(thr)

x = np.arange(size, dtype=np.complex64)
x = thr.to_device(x)
X = thr.array((size,), dtype=np.complex64)
ffts_unimod(X, x)
print(X)


unimod = unimod_gen(size, single=False)
fftd = FFT(thr.array(size, dtype=np.complex128))
fftd.parameter.output.connect(unimod, unimod.input, uni=unimod.output)
fftd_unimod = fftd.compile(thr)
x = np.arange(size, dtype=np.complex128)
x = thr.to_device(x)
X = thr.array((size,), dtype=np.complex128)
fftd_unimod(X, x)
print(X)
