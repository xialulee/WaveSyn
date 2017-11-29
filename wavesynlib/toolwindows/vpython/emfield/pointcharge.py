# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 19:34:43 2017

@author: Feng-cong Li
"""

import vpython as vp
from math import pi


# Point charge
vp.sphere(pos=vp.vec(0,0,0), radius=0.1, color=vp.color.yellow)

arrow_posx = vp.arrow(
    shaftwidth=0.02,
    color=vp.color.cyan,
    axis=vp.vec(1,0,0),
    pos=vp.vec(0,0,0))

arrow_posy = vp.arrow(
    shaftwidth=arrow_posx.shaftwidth,
    color=arrow_posx.color,
    axis=-arrow_posx.axis,
    pos=vp.vec(0,0,0))


k = 8
# q/epsilon
q_e = k*(k//2-1)+2

# angle between two vectors
da = 2*pi/k

# Not correct, need modification. 
for m in range(k):
    for n in range(k//2-1):
        vp.arrow(
            shaftwidth=arrow_posx.shaftwidth,
            color=arrow_posx.color,
            axis=arrow_posx.axis.rotate((n+1)*da).rotate((m+1)*da, axis=vp.vec(1,0,0)),
            pos=vp.vec(0,0,0))
        
        
vp.scene.width = 1024
vp.scene.height = 768

vp.scene.caption = f'''
q/ε = {q_e}<br/>
'''


sph = vp.sphere(pos=vp.vec(0,0,0), radius=0.4, color=vp.color.white, opacity=0.8, shininess=0)

def on_change_radius(s):
    sph.radius = s.value


sl_sph = vp.slider(min=0.15, max=0.8, value=0.4, length=360, bind=on_change_radius)