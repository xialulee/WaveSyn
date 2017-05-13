# -*- coding: utf-8 -*-
"""
Created on Sat May 13 15:37:20 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

from wavesynlib.languagecenter.glsl import Function


hit_circle = Function(
    func_name='hit_circle',
    ret_type='float',
    args=[('vec2', 'xy'), ('vec2', 'center'), ('float', 'radius'), ('float', 'tol')],
    body='''
    float d = distance({{center}}, {{xy}});
    float lower = {{radius}} - {{tol}};
    float upper = {{radius}} + {{tol}};
    if (lower<=d && d<=upper)
        return (tol-abs(d-{{radius}}))/{{tol}};
    else
        return 0.0;
    ''')