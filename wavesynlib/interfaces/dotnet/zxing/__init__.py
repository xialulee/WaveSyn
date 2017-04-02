# -*- coding: utf-8 -*-
"""
Created on Fri Apr 02 16:11:43 2017

@author: Feng-cong Li
"""
from __future__ import print_function, division, unicode_literals

import os

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting
from wavesynlib.languagecenter.utils import get_caller_dir

import clr
clr.AddReference(os.path.join(get_caller_dir(), 'zxing.dll'))
from ZXing import BarcodeReader



class ZXingNET(ModelNode):
    def __init__(self, *args, **kwargs):
        super(ZXingNET, self).__init__(*args, **kwargs)
        
        
    @Scripting.printable
    def read(self, image):
        image = self.root_node.interfaces.os.clipboard.support_clipboard_image(image)
        image = self.root_node.interfaces.dotnet.pyimage_to_netbitmap(image)
        result = BarcodeReader().Decode(image)
        if result is None:
            raise ValueError('Input image seems not contain any barcode.')
        return result.Text
        
        