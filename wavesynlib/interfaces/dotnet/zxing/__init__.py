# -*- coding: utf-8 -*-
"""
Created on Fri Apr 02 16:11:43 2017

@author: Feng-cong Li
"""
from pathlib import Path

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting
from wavesynlib.interfaces.dotnet.utils import new, BitmapUtils

import clr
clr.AddReference(str(Path(__file__).parent / 'zxing.dll'))
from ZXing import BarcodeReader, BarcodeWriter, BarcodeFormat
from ZXing.QrCode import QrCodeEncodingOptions
from System.Drawing import Bitmap



class ZXingNET(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    @Scripting.wavesynscript_api
    def read(self, image):
        image = self.root_node.interfaces.os.clipboard.constant_handler_CLIPBOARD_IMAGE(image)
        # To Do: support ask open file dialog
        bitmap = BitmapUtils.pil_to_netbmp(image)
        result = BarcodeReader().Decode(bitmap)
        if result is None:
            raise ValueError('Input image seems not contain any barcode.')
        return result.Text
        
        
    @Scripting.wavesynscript_api
    def write(self, contents, size=400, encode='utf-8'):
        writer = BarcodeWriter()
        writer.Format = BarcodeFormat.QR_CODE
        writer.Options = new(QrCodeEncodingOptions,
                                      DisableECI = True,
                                      CharacterSet = encode,
                                      Width = size,
                                      Height = size)
        mtx = writer.Write(contents)
        bmp = Bitmap(mtx)
        return BitmapUtils.netbmp_to_pil(bmp)