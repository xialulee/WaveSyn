# -*- coding: utf-8 -*-
"""
Created on Fri Apr 02 16:11:43 2017

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import os

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting
from wavesynlib.languagecenter.utils import get_caller_dir
from wavesynlib.interfaces.dotnet.utils import new_and_init, BitmapUtils

import clr
clr.AddReference(os.path.join(get_caller_dir(), 'zxing.dll'))
from ZXing import BarcodeReader, BarcodeWriter, BarcodeFormat
from ZXing.QrCode import QrCodeEncodingOptions
from System.Drawing import Bitmap



class ZXingNET(ModelNode):
    def __init__(self, *args, **kwargs):
        super(ZXingNET, self).__init__(*args, **kwargs)
        
        
    @Scripting.printable
    def read(self, image):
        image = self.root_node.interfaces.os.clipboard.support_clipboard_image(image)
        # To Do: support ask open file dialog
        image = BitmapUtils.pil_to_net(image)
        result = BarcodeReader().Decode(image)
        if result is None:
            raise ValueError('Input image seems not contain any barcode.')
        return result.Text
        
        
    @Scripting.printable
    def write(self, contents, image, size=400, encode='utf-8'):
        writer = BarcodeWriter()
        writer.Format = BarcodeFormat.QR_CODE
        writer.Options = new_and_init(QrCodeEncodingOptions,
                                      DisableECI = True,
                                      CharacterSet = encode,
                                      Width = size,
                                      Height = size)
        mtx = writer.Write(contents)
        bmp = Bitmap(mtx)
        bmp.Save(image)
        