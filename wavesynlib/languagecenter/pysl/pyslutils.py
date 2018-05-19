# -*- coding: utf-8 -*-
"""
Created on Wed May 16 21:58:34 2018

@author: Feng-cong Li
"""


def hit_circle(xy:vec2, center:vec2, radius:float, tol:float)->float:
    d:float = distance(center, xy)
    lower:float = radius - tol
    upper:float = radius + tol
    if lower <= d <= upper:
        return (tol-abs(d-radius))/tol
    else:
        return 0.0
    
    
    
def hit_line(xy:vec2, start:vec2, stop:vec2, tol:float)->float:
    v:vec2 = start - stop
    mstart:vec2 = xy - stop
    nv:vec2 = normalize(v)
    astart:float = acos(normalize(mstart)@(-nv))
    
    d:float = length(mstart)*sin(astart)
    lv:float = length(v)
    if d > tol:
        return 0.0
    else:
        if distance(xy, start)>lv or distance(xy, stop)>lv:
            return 0.0
        else:
            return (tol-d)/tol
        
        
        
def ppi_vertex(position:vec2)->vec2:
    gl_Position = vec4(position, 0.0, 1.0)
    return position



def ppi_fragment(texcoord)->vec3:
    angle:float = 0
    len_:float = 0
    hit:float = 0
    
    for i in range(1,4):
        hit = hit_circle(texcoord, 1.0/3.0*i, 0.005)
        if hit>0:
            break
        
    if hit == 0.0:
        hit = hit_line(texcoord, vec2(-1.0, 0.0), vec2(1.0, 0.0), 0.005)
        hit += hit_line(texcoord, vec2(0.0, -1.0), vec2(0.0, 1.0), 0.005)
        
    color:vec3 = vec3(0.0, 0.0, 0.0)
    if length(texcoord)<=1:
        angle = 2*PI - (atan(texcoord.y, texcoord.x) + PI)
        len_ = length(texcoord)
        color.g = (texture(image, vec2(angle / TWO_PI, len)) 
            * max(1 - mod(angle+current_angle, TWO_PI) / TWO_PI * 3, 0)).g
        color.rb = vec2(0.0, 0.0)
        
    if hit > 0.0:
        return mix(color, vec3(0.0, 1.0, 0.0)*hit*0.5, 0.35)
    else:
        return color
        
        

def display_vertex(position:vec2, texcoord:vec2)->vec2:
    gl_Position = vec4(position, 0.0, 1.0)
    return texcoord



def display_fragment(v_texcoord:vec2)->vec4:
    return texture(image, v_texcoord)