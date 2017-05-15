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
    
    
hit_line = Function(
    func_name = 'hit_line',
    ret_type='float',
    args=[('vec2', 'xy'), ('vec2', 'start'), ('vec2', 'stop'), ('float', 'tol')],
    body='''
    #define PI 3.1415926535897932384626433832795    
    
    vec2 v = {{start}} - {{stop}};    
    vec2 mstart = {{xy}} - {{stop}};
    vec2 nv = normalize(v);
    float astart = acos(dot(normalize(mstart), -nv));
    
    float d = length(mstart)*sin(astart);
    float lv = length(v);
    if (d>{{tol}})
        return 0.0;
    else
        if (distance(xy, start)>lv || distance(xy, stop)>lv)
            return 0.0;
        else
            return ({{tol}}-d)/{{tol}};
''')