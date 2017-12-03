# -*- coding: utf-8 -*-
"""
Created on Sun Dec  3 23:40:28 2017

@author: Feng-cong Li
"""

import vpython as vp

length = 10
r_min = 1
r_max = 5

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


rings = []

level = 10
delta_z = length/10
for m in range(level):
    z = m*delta_z + delta_z/2    
    ring = vp.ring(
        pos=vp.vec(0,0,z),
        radius=surface.radius,
        axis=vp.vec(0,0,1),
        thickness=0.05,
        color=vp.color.cyan)
    rings.append(ring)
        
        
def on_change_radius(s):
    surface.radius = s.value
    for ring in rings:
        ring.radius = s.value
    
    
sl_surface = vp.slider(
    min=r_min, 
    max=r_max, 
    value=r_min, 
    length=360, 
    bind=on_change_radius)