# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 22:14:32 2017

@author: Feng-cong Li
"""
from __future__ import division

from scipy.ndimage import imread
from vispy import app
from vispy.gloo import clear, set_clear_color, set_viewport, Program


vertex = """
#version 130

attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;


void main(){
    gl_Position = vec4(position, 0.0, 1.0 );
    v_texcoord.y = 1.0 - texcoord.y;
    v_texcoord.x = texcoord.x;
}
"""


fragment = """
#version 130

uniform sampler2D image;
varying vec2 v_texcoord;

out vec4 frag_color;


void main(){
    if ((v_texcoord.x < 0.0 || v_texcoord.x > 1.0) || (v_texcoord.y < 0.0 || v_texcoord.y > 1.0))
        frag_color = vec4(0.0, 0.0, 0.0, 0.0);
    else
        frag_color = texture(image, v_texcoord);
}
"""


class Canvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, size=(512, 512),
                            keys='interactive')
                            
        image = imread(r"C:\Users\xialulee\Pictures\1-4.png", mode='RGBA').astype('float32') / 255.0
        height, width, dumb = image.shape        
        self.__image_ratio = width / height
        self.__image_size = width + 1j*height

        self.program = Program(vertex, fragment, 4)
        self.program['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)
        self.program['texcoord'] = (0, 0), (0, +1), (+1, 0), (+1, +1)


        self.program['image'] = image
        self.program['image'].interpolation = 'linear'

        set_clear_color('black')

        self.show()

    def on_resize(self, event):
        scale = 2
        c_w, c_h = event.physical_size
        self._set_viewport(c_w+1j*c_h, scale=scale)
                   

    def on_draw(self, event):
        clear(color=True, depth=True)
        self.program.draw('triangle_strip')
        
        
    def _set_viewport(self, canvas_size, scale=1, offset=0):
        sc = canvas_size
        rc = sc.real / sc.imag
        ri = self.__image_ratio
        
        if rc >= ri:
            si = sc.imag * (ri + 1j)
        else:
            si = sc.real * (1 + 1j/ri)
            
        si *= scale
        LL = sc/2 - si/2
        set_viewport(LL.real, LL.imag, si.real, si.imag)
        

if __name__ == '__main__':
    canvas = Canvas()
app.run()