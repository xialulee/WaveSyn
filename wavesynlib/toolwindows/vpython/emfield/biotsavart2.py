# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 20:00:21 2017

@author: Feng-cong Li
"""

import vpython as vp
from math import pi

vp.scene.width = 1024
vp.scene.height = 768

curelm = vp.arrow(
            shaftwidth=0.05, 
            color=vp.color.cyan,
            axis=vp.vec(0,0,0.5),
            pos = vp.vec(0,0,0),
            visible=True)



shaft = 0.1
for rho in (1, 1.5, 2):
    for z in (-3, -2, -1, 0, 1, 2, 3):
        for theta in (0, 45, 90, 135, 180, 225, 270, 315):
            theta = theta/180*pi
            R = vp.vec(rho, 0, z).rotate(theta)
            # For simplicity, we assume mu_0/4/pi*I*dl=1
            ax = vp.norm(curelm.axis).cross(vp.norm(R))/R.mag2
            vp.arrow(
                shaftwidth=shaft/R.mag2, 
                color=vp.color.yellow, 
                axis=ax, 
                pos=R, 
                visible=True)
