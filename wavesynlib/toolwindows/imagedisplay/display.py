# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 22:14:32 2017

@author: Feng-cong Li
"""
from __future__ import division, print_function

__DEBUG__ = False

from sys import argv
import socket
from six.moves import cStringIO as StringIO

import numpy as np
#from scipy.ndimage import imread
from vispy import app
from vispy.gloo import clear, set_clear_color, set_viewport, Program


vertex = """
#version 130

attribute vec2 position;
attribute vec2 texcoord;
varying vec2 v_texcoord;


void main(){
    gl_Position = vec4(position, 0.0, 1.0 );
    v_texcoord = texcoord;
}
"""


fragment = """
#version 130

uniform sampler2D image;
varying vec2 v_texcoord;

out vec4 frag_color;


void main(){
    frag_color = texture(image, v_texcoord);
}
"""


class Canvas(app.Canvas):
    def __init__(self, image):
        app.Canvas.__init__(self, title='WaveSyn-ImageViewer', size=(512, 512),
                            keys='interactive')
                            
        #image = imread(r"C:\Users\xialulee\Pictures\1-4.jpg", mode='RGBA').astype('float32') / 255.0
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
        self.__center = self.size[0]/2.0 + 1j*self.size[1]
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
        self.scale += 0.1*event.delta[1] 
        if self.scale <= 1:
            self.__offset = 0+1j*0
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
        LL = sc/2 + offset - si/2
        set_viewport(LL.real, LL.imag, si.real, si.imag)
        

def recv_data(port):
    sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockobj.connect(('localhost', port))
    sio = StringIO()
    while True:
        data = sockobj.recv(4096)
        if not data: 
            break
        sio.write(data)
    retval = sio.getvalue()
    sio.close()
    return retval


if __name__ == '__main__':
    port = int(argv[1])
    width = int(argv[2])
    height = int(argv[3])
    data = recv_data(port)
    mat = np.fromstring(data, dtype=np.float32)
    mat.shape = (height, width, 4)
    canvas = Canvas(image=mat)
    app.run()