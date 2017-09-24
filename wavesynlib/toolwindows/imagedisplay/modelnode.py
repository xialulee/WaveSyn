# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 21:26:31 2017

@author: Feng-cong Li
"""

import _thread as thread
import socket
from subprocess import Popen
import numpy as np

from wavesynlib.languagecenter.wavesynscript import ModelNode, Scripting
from wavesynlib.languagecenter.utils import get_caller_dir


class DisplayLauncher(ModelNode):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    
    @Scripting.printable
    def launch(self, rgba_matrix):
        height, width, depth = rgba_matrix.shape
        mat = np.zeros((height, width, 4), dtype=np.float32)
        if depth < 4:
            mat[:, :, :depth] = rgba_matrix[:, :, :]
        else:
            mat[:, :, :] = rgba_matrix[:, :, :4]
        if rgba_matrix.dtype == np.uint8:
            mat /= 255.0
        
        sockobj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        port = 10000
        while True:
            try:
                sockobj.bind(('', port))
            except socket.error:
                port += 1
                if port > 65535:
                    raise socket.error
            else:
                break
            
        def send_data():
            sockobj.listen(1)
            conn, addr = sockobj.accept()
            conn.send(mat.tostring())
            
        thread.start_new_thread(send_data, ())
        
        display_path = str(get_caller_dir() / 'display.py')
        Popen(['python', display_path, str(port), str(width), str(height)])