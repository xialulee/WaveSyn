# -*- coding: utf-8 -*-
"""
Created on Fri Jul 31 10:19:14 2015

@author: Feng-cong Li
"""
from __future__ import print_function
import sys
import os

ERROR_NOERROR, ERROR_PARAM = range(2)

if __name__ == '__main__':
    import platform
    if platform.python_implementation() != 'IronPython':
        sts = os.system(' '.join(['ipy'] + sys.argv))
        sys.exit(sts)

import clr
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')

from System.Windows.Forms import (
    Application, DockStyle, Form, PictureBox, PictureBoxSizeMode
)

class MainForm(Form):
    def __init__(self, bitmap):
        Form.__init__(self)
        picBox  = PictureBox()
        picBox.SizeMode = PictureBoxSizeMode.AutoSize
        picBox.Image    = bitmap
        picBox.Dock     = DockStyle.Fill
        
        self.Controls.Add(picBox)
        self.Show()
        self.Width = bitmap.Width + 20
        self.Height = bitmap.Height + 20

        

clr.AddReference('zxing')
import ZXing

def QRCodeGen(content, width=None, height=None):
    writer  = ZXing.BarcodeWriter()
    writer.Format = ZXing.BarcodeFormat.QR_CODE
    writer.Options.Hints[ZXing.EncodeHintType.CHARACTER_SET] = 'utf-8'
    if width is not None:
        writer.Options.Hints[ZXing.EncodeHintType.WIDTH] = width
    if height is not None:
        writer.Options.Hints[ZXing.EncodeHintType.HEIGHT] = height
    return writer.Write(content)

    
import getopt

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], \
            'dh:w:s:',\
            ['display', 'height=', 'width=', 'saveas=', 'stdin']
        )
    except getopt.GetoptError, err:
        print(str(err), file=sys.stderr)
        sys.exit(ERROR_PARAM)
        
        
    height = width = None
    filename = None
    display = False
    readStdin = False
    
    for o, a in opts:
        if o in ('-h', '--height'):
            height = int(a)
        if o in ('-w', '--width'):
            width = int(a)
        if o in ('-s', '--saveas'):
            filename = a
        if o in ('-d', '--display'):
            display = True
        if o in ('--stdin',):
            readStdin = True

    if readStdin:
        content = sys.stdin.read()
    else:
        content = args[0]

    bitmap = QRCodeGen(content, width, height)
    
    if filename:
        bitmap.Save(filename)

    if display:        
        Application.EnableVisualStyles()
        form = MainForm(bitmap)
        Application.Run(form)    


if __name__ == '__main__':
    main()