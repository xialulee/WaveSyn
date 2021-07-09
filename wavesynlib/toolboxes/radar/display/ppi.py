# -*- coding: utf-8 -*-
"""
Created on Mon May 08 22:17:47 2017

@author: Feng-cong Li
"""
__DEBUG__ = False

from pathlib import Path

import numpy as np
import quantities as pq
from math import pi
from vispy import app
from vispy.gloo import clear, set_clear_color, set_viewport, Program

from jinja2 import Template
from wavesynlib.languagecenter.pysl.utils import hit_circle, hit_line
from wavesynlib.languagecenter.pysl.constants import pi as PI_STR
from wavesynlib.languagecenter.nputils import NamedAxesArray

# The PyQt5 support of VisPy still has some problems.
# Hence we use the GLFW backend here. 
app.use_app(backend_name='glfw')



with open(Path(__file__).parent/"ppi.vert", "r") as vert_file:
    vertex = vert_file.read()


with open(Path(__file__).parent/"ppi.frag", "r") as frag_file:
    frag_temp = frag_file.read()
fragment = Template(frag_temp).render(    
    pi=PI_STR,
    hit_circle=hit_circle.partial('hit_circle', center='vec2(0.0,0.0)').to_code(),
    hit_line=hit_line.to_code())



class Canvas(app.Canvas):
    def __init__(self, image):
        assert(isinstance(image, NamedAxesArray))
        assert(image.axis_names[:2]==("azimuth", "range"))
        self.__scale = 1
        self.__image_ratio = 1
        app.Canvas.__init__(self, title='WaveSyn-ImageViewer', size=(512, 512),
                            keys='interactive')

        azimuth_scale = image.get_scale(axis='azimuth')
        azimuth_scale = azimuth_scale.rescale(pq.rad).magnitude
        azimuth_scale = np.unwrap(azimuth_scale)
        while azimuth_scale.max() > 2*np.pi:
            azimuth_scale -= 2*np.pi
        start_angle    = azimuth_scale.min()
        stop_angle     = azimuth_scale.max()
        angle_interval = stop_angle - start_angle

        height, width, dumb = image.array.shape        
        self.__image_size = width + 1j*height

        self.program = Program(vertex, fragment, 4)
        self.program['position'] = (-1, -1), (-1, +1), (+1, -1), (+1, +1)

        self.program['image'] = image.array
        self.program['image'].interpolation = 'linear'
        self.program["start_angle"] = start_angle
        self.program["stop_angle"] = stop_angle
        self.program["angle_interval"] = angle_interval
        self.program['current_angle'] = 0.0

        set_clear_color('black')
        self.__last_pos = 0+1j*0
        self.__offset = 0+1j*0
        
        self._timer = app.Timer(1/30, connect=self._on_timer, start=True)

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
        


#if __name__ == '__main__':
    ## mat = imread('c:/lab/test.jpg')
    #canvas = Canvas(image=np.ones((128, 128, 3), dtype=np.uint8)*255)
    #app.run()
