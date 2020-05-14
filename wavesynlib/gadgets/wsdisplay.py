# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 22:14:32 2017

@author: Feng-cong Li
"""
__DEBUG__ = False

import os
import argparse
from pathlib import Path

from PIL import Image

import numpy as np
from vispy import app
from vispy.gloo import clear, set_clear_color, set_viewport, Program

from wavesynlib.fileutils.photoshop import psd


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

uniform sampler2D image;
in vec2 v_texcoord;

out vec4 frag_color;


void main(){
    frag_color = texture(image, v_texcoord);
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
        new_scale = original_scale + delta_scale
        if new_scale < 0.1:
            return
        self.scale = new_scale
        
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
            
            
    def on_key_press(self, event):
        if event.key.name == 'Enter':
            self.fullscreen = not self.fullscreen
                   

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
        

def get_image_data(path):
    with open(path, 'rb') as f:
        if path.suffix == ".psd":
            image = psd.get_pil_image(f, read_channels="min")[0]
        else:
            image = Image.open(f)
        rgba_image = Image.new('RGBA', image.size)
        rgba_image.paste(image)    
    ret = np.array(rgba_image, dtype=np.float32)
    ret /= 255.0
    return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display a given image file.')
    parser.add_argument('filename', metavar='filename', type=Path, help='The filename of the given image.')
    parser.add_argument('--delete', help='Delete image file.', action='store_true')
    args = parser.parse_args()
    mat = get_image_data(args.filename)
    if args.delete:
        os.remove(args.filename)
    canvas = Canvas(image=mat)
    app.run()