# -*- coding: utf-8 -*-
"""
Created on Wed Nov 29 20:20:51 2017

@author: Feng-cong Li
"""

import vpython as vp
from math import sin, cos, pi

vp.scene.width = 1024
vp.scene.height = 768

curelm = vp.arrow(
            shaftwidth=0.05, 
            color=vp.color.cyan,
            axis=vp.vec(0,0,0.5),
            pos = vp.vec(0,0,0),
            visible=True)

R = 1

angles = (30, 60, 90, 120, 150)
angles = [angle/180*pi for angle in angles]

rings = [\
    vp.ring(
        pos=vp.vec(0,0,cos(theta)*R), 
        radius=sin(theta)*R, 
        axis=vp.vec(0,0,1), 
        thickness=0.03, 
        color=vp.color.green) 
    for theta in angles]


vp.scene.caption = f'''
μIdl = 5
'''

sph = vp.sphere(pos=vp.vec(0,0,0), radius=R, color=vp.color.white, opacity=0.8, shininess=0)
    
def on_change_radius(s):
    R = s.value
    sph.radius = R
    for idx, ring in enumerate(rings):
        ring.pos = vp.vec(0,0,cos(angles[idx])*R)
        ring.radius = sin(angles[idx])*R

sl_sph = vp.slider(min=1, max=3, value=1, length=360, bind=on_change_radius)