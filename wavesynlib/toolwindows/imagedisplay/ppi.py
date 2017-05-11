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


vertex = """
#version 420

attribute vec2 position;
attribute vec2 texcoord;
out vec2 v_texcoord;


void main(){
    gl_Position = vec4(position, 0.0, 1.0 );
    v_texcoord = texcoord - 0.5;
}
"""


fragment = """
#version 420

#define PI 3.1415926535897932384626433832795

uniform sampler2D image;
uniform float current_angle;
in vec2 v_texcoord;
out vec3 frag_color;


void main(){
    float angle;    
    float len;
            
    if (length(v_texcoord)<=0.5) {
        angle = 2*PI-(atan(v_texcoord.y, v_texcoord.x) + PI);
        len = length(v_texcoord);      
        frag_color.g = (texture(image, vec2(angle / 2 / PI, len * 2)) 
            * max(1 - mod(angle+current_angle, 2*PI) / 2 / PI * 3, 0)).g;
        frag_color.rb = vec2(0.0, 0.0);
    } else {
        frag_color = vec3(0.0, 0.0, 0.0);
    }
}
"""


class Canvas(app.Canvas):
    def __init__(self, image):
        app.Canvas.__init__(self, title='WaveSyn-ImageViewer', size=(512, 512),
                            keys='interactive')

        height, width, dumb = image.shape        
        self.__image_ratio = 1
        self.__image_size = width + 1j*height

        self.program = Program(vertex, fragment, 4)
        self.program['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)
        self.program['texcoord'] = (0, +1), (0, 0), (+1, +1), (+1, 0)


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