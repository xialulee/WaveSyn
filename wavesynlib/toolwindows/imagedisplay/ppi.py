# -*- coding: utf-8 -*-
"""
Created on Mon May 08 22:17:47 2017

@author: Feng-cong Li
"""
from __future__ import division, print_function

__DEBUG__ = False


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
    v_texcoord = texcoord;
}
"""


fragment = """
#version 420

#define PI 3.1415926535897932384626433832795

uniform sampler2D image;
in vec2 v_texcoord;

out vec4 frag_color;


void main(){
    vec2 new_coord;
    vec2 center = vec2(0.5, 0.5);
    vec2 relative;
    float angle;    
    float len;
    
    new_coord = v_texcoord;
    relative = new_coord - center;
    relative.x = - relative.x;
    
    if (length(relative)>0.5){
        new_coord.x = -1;
        new_coord.y = -1;
    } else {
        if (relative.x == 0) {
            angle = PI / 2.0;
        } else {
            angle = atan(relative.y, relative.x) + PI;
        }
        len = length(relative);
        
        new_coord.x = angle / 2 / PI;
        new_coord.y = len * 2;
    }
    
    frag_color = texture(image, new_coord);
}
"""


class Canvas(app.Canvas):
    def __init__(self, image):
        app.Canvas.__init__(self, title='WaveSyn-ImageViewer', size=(512, 512),
                            keys='interactive')

        height, width, dumb = image.shape        
        self.__image_ratio = width / height
        self.__image_size = width + 1j*height

        self.program = Program(vertex, fragment, 4)
        self.program['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)
        self.program['texcoord'] = (0, +1), (0, 0), (+1, +1), (+1, 0)


        self.program['image'] = image
        self.program['image'].interpolation = 'linear'

        set_clear_color('black')
        self.__scale = 1
        self.__last_pos = 0+1j*0
        self.__offset = 0+1j*0

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
        


if __name__ == '__main__':
    mat = imread('c:/lab/test.png')
    canvas = Canvas(image=mat)
    app.run()