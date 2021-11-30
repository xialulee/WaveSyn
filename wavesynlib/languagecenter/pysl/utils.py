# -*- coding: utf-8 -*-
"""
Created on Sat May 13 15:37:20 2017

@author: Feng-cong Li
"""
from wavesynlib.languagecenter.pysl import Function


hit_circle = Function(
    func_name='hit_circle',
    ret_type='float',
    args=[('vec2', 'xy'), ('vec2', 'center'), ('float', 'radius'), ('float', 'tol')],
    body='''
    float d = distance({{center}}, {{xy}});
    float lower = {{radius}} - {{tol}};
    float upper = {{radius}} + {{tol}};
    if (lower<=d && d<=upper) {
        return (tol-abs(d-{{radius}}))/{{tol}};
    } else {
        return 0.0f;
    }
''')
    
    
hit_line = Function(
    func_name = 'hit_line',
    ret_type='float',
    args=[('vec2', 'xy'), ('vec2', 'start'), ('vec2', 'stop'), ('float', 'tol')],
    body='''
    vec2 v = {{start}} - {{stop}};    
    vec2 mstart = {{xy}} - {{stop}};
    vec2 nv = normalize(v);
    float astart = acos(dot(normalize(mstart), -nv));
    float d = length(mstart)*sin(astart);
    float lv = length(v);
    if (d>{{tol}}) {
        return 0.0f;
    } else {
        if (distance({{xy}}, {{start}})>lv || distance({{xy}}, {{stop}})>lv) {
            return 0.0f;
        } else {
            return ({{tol}}-d)/{{tol}};
        }
    }
''')
