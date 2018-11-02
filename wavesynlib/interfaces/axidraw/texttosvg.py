# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 10:42:20 2018

@author: Feng-cong Li
"""
import os
from random import random
from lxml import etree
import xml.etree.ElementTree



width = '200'
height = '400'

# assume the size of chars in the fontlib is 100x100

def generate(text, 
             svg_filename,
             width, height,
             x_offset, y_offset,
             char_width_scale, char_height_scale, char_width_jitter, char_height_jitter, char_skew_jitter,
             fontlibs):

    origin = (x_offset, y_offset)
    char_width = 100*char_width_scale 
    char_height = 100*char_height_scale
        
    root = etree.Element('svg', attrib={'width':str(width), 'height':str(height), 'viewBox':f'0 0 {width} {height}'})

    def rand_font_idx():
        return int(random()*len(fontlibs))
    
    def rand_char_size():
        if char_width_jitter:
            cw = char_width * (1+char_width_jitter*random())
        else:
            cw = char_width
            
        if char_height_jitter:
            ch = char_height * (1+char_height_jitter*random())
        else:
            ch = char_height
            
        return cw, ch
    
    for char in text:
        if char != ' ':
            char_font_filename = f'{char}.svg'
            char_font_filepath = os.path.join(fontlibs[rand_font_idx()], char_font_filename)
            if not os.path.exists(char_font_filepath):
                raise ValueError(f'{char} not exists in {fontlibs[rand_font_idx()]}')

        cw, ch = rand_char_size()
        
        if x_offset + cw > width:
            x_offset = origin[0]
            y_offset += char_height*(1+char_height_jitter)        

        if char != ' ':
            group = etree.Element('g', attrib={'transform':f'''\
translate({x_offset} {y_offset}) scale({cw/char_width*char_width_scale} {ch/char_height*char_height_scale})'''})
            root.append(group)
            char_paths = xml.etree.ElementTree.parse(char_font_filepath).getroot().findall('*/{http://www.w3.org/2000/svg}path')
            for path in char_paths:
                path_el = etree.Element('path', attrib={'d':path.get('d'), 'style':path.get('style')})
                group.append(path_el)
            

        x_offset += cw              
    with open(svg_filename, 'w') as f:
        f.write(etree.tostring(root, pretty_print=True).decode('utf-8'))
        