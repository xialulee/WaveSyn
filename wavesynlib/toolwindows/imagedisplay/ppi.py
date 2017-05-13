# -*- coding: utf-8 -*-
"""
Created on Mon May 08 22:17:47 2017

@author: Feng-cong Li
"""
from __future__ import division, print_function

__DEBUG__ = False


from math import pi
from scipy.ndimage import imread
from vispy import app
from vispy.gloo import clear, set_clear_color, set_viewport, Program

from jinja2 import Template
from wavesynlib.languagecenter.glsl.utils import hit_circle
from wavesynlib.languagecenter.glsl.constants import pi as PI_STR
from six import binary_type


vertex = """
#version 420

attribute vec2 position;
out vec2 texcoord;


void main(){
    gl_Position = vec4(position, 0.0, 1.0 );
    texcoord = position;
}
"""


fragment = binary_type(Template("""
#version 420

#define PI {{pi}}
#define TWO_PI (2*PI)

uniform sampler2D image;
uniform float current_angle;
in vec2 texcoord;
out vec3 frag_color;

{{hit_circle}}

void main(){
    float angle;    
    float len;
    float hit;

    for (int i=1; i<=3; ++i){    
        hit = hit_circle(texcoord, 1.0/3.0*i, 0.005);
        if (hit>0) break;
    }
        
    vec3 color = vec3(0.0, 0.0, 0.0);        
    if (length(texcoord)<=1){
        angle = 2*PI-(atan(texcoord.y, texcoord.x) + PI);
        len = length(texcoord);      
        color.g = (texture(image, vec2(angle / TWO_PI, len)) 
            * max(1 - mod(angle+current_angle, TWO_PI) / TWO_PI * 3, 0)).g;
        color.rb = vec2(0.0, 0.0);
    }
            
    if (hit>0.0)
        frag_color = mix(color, vec3(0.0, 1.0, 0.0)*hit*0.5, 0.35);
    else
        frag_color = color;
}
""").render(
    pi=PI_STR,
    hit_circle=hit_circle.partial('hit_circle', center='vec2(0.0,0.0)').to_code()))



class Canvas(app.Canvas):
    def __init__(self, image):
        app.Canvas.__init__(self, title='WaveSyn-ImageViewer', size=(512, 512),
                            keys='interactive')

        height, width, dumb = image.shape        
        self.__image_ratio = 1
        self.__image_size = width + 1j*height

        self.program = Program(vertex, fragment, 4)
        self.program['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)

        self.program['image'] = image
        self.program['image'].interpolation = 'linear'
        self.program['current_angle'] = 0.0

        set_clear_color('black')
        self.__scale = 1
        self.__last_pos = 0+1j*0
        self.__offset = 0+1j*0
        
        self._timer = app.Timer(1/60, connect=self._on_timer, start=True)

        self.show()
        
        
    @property
    def scale(self):
        return self.__scale

    
    @scale.setter
    def scale(self, val):
        if val > 0:
            self.__scale = val
        

    def on_resize(self, event):
        self.__offset = 0+1j*0
        self._set_viewport()
        
        
    def on_mouse_wheel(self, event):
        original_scale = self.scale
        delta_scale = 0.1*event.delta[1]
        self.scale += delta_scale 
        
        mouse_pos = event.pos[0] + 1j*(self.size[1]-event.pos[1])
        mouse_pos -= self.__offset
        mouse_pos /= original_scale
        self.__offset -= mouse_pos * delta_scale
        self._set_viewport()
        self.update()
        
        
    def on_mouse_press(self, event):
        self.__last_pos = (event.pos[0] + 1j*event.pos[1]).conjugate()
        
        
    def on_mouse_move(self, event):
        if event.is_dragging:
            pos = event.pos[0] + 1j*event.pos[1]
            pos = pos.conjugate()
            
            self.__offset += pos - self.__last_pos
            self.__last_pos = pos
            self._set_viewport()
            self.update()
                   

    def on_draw(self, event):
        clear(color=True, depth=True)
        self.program.draw('triangle_strip')
        
        
    def _set_viewport(self):
        sc = self.size[0] + 1j*self.size[1]
        scale = self.scale
        offset = self.__offset
        rc = sc.real / sc.imag
        ri = self.__image_ratio
        
        if rc >= ri:
            si = sc.imag * (ri + 1j)
        else:
            si = sc.real * (1 + 1j/ri)
            
        si *= scale
        set_viewport(offset.real, offset.imag, si.real, si.imag)
        
        
    def _on_timer(self, event):
        if self._timer.running:
            self.program['current_angle'] += event.dt*pi
        self.update()
        


if __name__ == '__main__':
    mat = imread('c:/lab/test.jpg')
    canvas = Canvas(image=mat)
    app.run()