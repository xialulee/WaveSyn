# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 15:36:46 2017

@author: Feng-cong Li
"""

import vpython as vp
from math import pi


global q

v = vp.arrow(shaftwidth=0.05, color=vp.vec(1,1,0), visible=True)
v.pos = vp.vec(0, 0, 0)
v.axis = vp.vec(0.5, 0, 0)
t_v = vp.text(text='v', pos=v.axis, height=0.1, color=v.color, billboard=True, emissive=True)

B = vp.arrow(shaftwidth=0.05, color=vp.color.cyan, visible=True)
B.pos = vp.vec(0, 0, 0)
B.axis = vp.vec(0.5, 0, 0)
t_B = vp.text(text='B', pos=B.axis, height=0.1, color=B.color, billboard=True, emissive=True)

q = 0.5

F = vp.arrow(shaftwidth=0.05, color=vp.color.green, visible=True)
F.pos = vp.vec(0, 0, 0)
F.axis = vp.vec(0, 0, 0)
t_F = vp.text(text='F', pos=F.axis, height=0.1, color=F.color, billboard=True, emissive=True)



def calc_F():
    F.axis = q*v.axis.cross(B.axis)
    text_F.text = f' = <b>e</b><sub><b>v</b>×<b>B</b></sub> {F.axis.mag:.3} (N)'
    t_F.pos = F.axis


def on_B_change(s):
    B.axis.mag = s.value
    text_B.text = f'B = {s.value} (T)'
    t_B.pos = B.axis
    calc_F()
    
    
def on_v_change(s):
    v.axis.mag = s.value
    text_v.text = f'v = {s.value} (m/s)'
    t_v.pos = v.axis
    calc_F()
    
    
def on_q_change(s):
    global q
    q = s.value
    text_q.text = f'q = {s.value} (C)'
    calc_F()


def on_theta_change(s):
    temp = vp.vec(1, 0, 0)
    temp = temp * v.axis.mag
    v.axis = temp.rotate(s.value/180*pi)
    text_theta.text = f'θ = {s.value}°'
    t_v.pos = v.axis
    calc_F()


vp.scene.width = 800
vp.scene.height= 600

vp.scene.caption = '<b>F</b> = q<b>v</b> × <b>B</b>'
text_F = vp.wtext(text=' = <b>e</b><sub><b>v</b>×<b>B</b></sub> 0 (N)')
vp.scene.append_to_caption('\n')

sl_B = vp.slider(min=0, max=1, value=0.5, length=360, bind=on_B_change, right=15)
text_B = vp.wtext(text=f'B = {sl_B.value} (T)')
vp.scene.append_to_caption('\n')

sl_v = vp.slider(min=0, max=1, value=0.5, length=360, bind=on_v_change, right=15)
text_v = vp.wtext(text=f'v = {sl_v.value} (m/s)')
vp.scene.append_to_caption('\n')

sl_theta = vp.slider(min=0, max=360, value=0, length=360, bind=on_theta_change, right=15)
text_theta = vp.wtext(text=f'θ = {sl_theta.value/pi*180}°')
vp.scene.append_to_caption('\n')

sl_q = vp.slider(min=0, max=1, value=0.5, length=360, bind=on_q_change, right=15)
text_q = vp.wtext(text=f'q = {sl_q.value} (C)')
vp.scene.append_to_caption('\n')

