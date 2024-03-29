# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 22:57:24 2017

@author: Feng-cong Li
"""

import clr
import System


def new(class_object, **kwargs):
    obj = class_object()
    for [key, val] in kwargs.items():
        setattr(obj, key, val)
    return obj


class MemoryStreamWrapper:
    def __init__(self):
        from System.IO import MemoryStream
        self.__stream = MemoryStream()

    def write(self, data):
        return self.__stream.Write(data, 0, len(data))

    def seek(self, offset, whence=0):
        return self.__stream.Seek(offset, whence)

    @property
    def real_object(self):
        return self.__stream


class BitmapUtils:
    @staticmethod
    def pil_to_netbmp(image):
        from System.Drawing import Bitmap
        ms = MemoryStreamWrapper()
        image.save(ms, 'png')
        ms.seek(0)
        return Bitmap(ms.real_object)

    @staticmethod
    def netbmp_to_pil(bitmap):
        from PIL import Image
        stream = BitmapUtils.netbmp_to_pystream(bitmap)
        return Image.open(stream)

    @staticmethod
    def netbmp_to_pystream(bitmap):
        from System.IO import MemoryStream
        from System.Drawing.Imaging import ImageFormat
        ms = MemoryStream()
        bitmap.Save(ms, ImageFormat.Png)
        arr = ms.ToArray()
        from io import BytesIO
        stream = BytesIO()
        stream.write(bytes(arr))
        stream.seek(0)
        return stream

    @staticmethod
    def netbmp_to_matrix(bitmap):
        stream = BitmapUtils.netbmp_to_pystream(bitmap)
        from imageio import imread
        return imread(stream, 'png')

