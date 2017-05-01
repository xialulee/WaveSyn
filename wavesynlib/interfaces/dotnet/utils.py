# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 22:57:24 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import six
import clr
import System



class NETMemoryStream(object):
    def __init__(self):
        from System.IO import MemoryStream
        self.__stream = MemoryStream()
       
       
    def write(self, data):
        self.__stream.Write(data, 0, len(data))
        
        
    def seek(self, offset, whence=0):
        self.__stream.Seek(offset, whence)
        
    
    @property
    def net_object(self):
        return self.__stream



def new_and_init(class_object, **kwargs):
    obj = class_object()
    for key in kwargs:
        setattr(obj, key, kwargs[key])
    return obj

        

class BitmapUtils(object):
    @staticmethod
    def pil_to_net(image):    
        from System.Drawing import Bitmap    
        ns = NETMemoryStream()
        image.save(ns, 'png')
        ns.seek(0)
        return Bitmap(ns.net_object)
        
        
    @staticmethod
    def net_to_matrix(bitmap):
        from System.IO import MemoryStream
        from System.Drawing.Imaging import ImageFormat
        ms = MemoryStream()
        bitmap.Save(ms, ImageFormat.Png)
        arr = ms.ToArray()
        from cStringIO import StringIO
        stream = StringIO()
        stream.write(six.binary_type('').join([chr(c) for c in arr]))
        from scipy.ndimage import imread
        return imread(stream)
        
    
    
        