# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 23:19:45 2017

@author: Feng-cong Li
"""

import vpython as vp
from math import pi

length = 10
r_min = 1
r_max = 5
arrow_sw = 0.1

vp.scene.width = 1024
vp.scene.height = 768

wire = vp.cylinder(
    pos=vp.vec(0,0,0), 
    axis=vp.vec(0,0,length), 
    radius=length/50,
    color=vp.color.yellow)

surface = vp.cylinder(
    pos=wire.pos,
    axis=wire.axis,
    radius= r_min,
    opacity=0.5,
    shininess=0)

level = 10
rad = 12
delta_theta = 2*pi/rad
delta_z = length/10
for m in range(level):
    z = m*delta_z + delta_z/2    
    for n in range(rad):
        vp.arrow(
            shaftwidth=arrow_sw,
            color=vp.color.cyan,
            pos=vp.vec(0,0,z),
            axis=vp.vec(r_max*1.2,0,0).rotate(n*delta_theta))
        
        
def on_change_radius(s):
    surface.radius = s.value
    
    
sl_surface = vp.slider(
    min=r_min, 
    max=r_max, 
    value=r_min, 
    length=360, 
    bind=on_change_radius)
        