# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 19:35:46 2017

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


colormap = {1:vp.color.green, 2:vp.color.yellow, 3:vp.color.white}
for R in (1, 2, 3):
    for theta in (30, 60, 90, 120, 150):
        theta = theta/180*pi
        vp.ring(pos=vp.vec(0,0,cos(theta)*R), radius=sin(theta)*R, axis=vp.vec(0,0,1), thickness=0.03, color=colormap[R])