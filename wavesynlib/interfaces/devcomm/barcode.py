# -*- coding: utf-8 -*-
"""
Created on Thu Nov 05 10:58:33 2015

@author: Feng-cong Li
"""

from __future__ import print_function
import sys
import getopt

ERROR_NOERROR, ERROR_PARAM = range(2)

import qrcode # pip install qrcode

from Tkinter import *
from PIL import ImageTk

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:],\
            'd:e:s:f:',\
            ['nodisplay', 'stdin', 'size=', 'decode=', 'encode=', 'file=', 'wintitle=']
        )
    except getopt.GetoptError, err:
        print(str(err), file=sys.stderr)
        sys.exit(ERROR_PARAM)
        
        
    size = 400 # default size
    nodisplay = False
    readStdin = False
    decode = None
    encode = 'utf-8'
    filename = None
    title = 'WaveSyn-Barcode'
    for o, a in opts:
        if o in ('-s', '--size'):
            size = int(a) # size is not implemented. 
        if o in ('-f', '--file'):
            filename = a
        if o in ('-d', '--decode'):
            decode = a
        if o in ('-e', '--encode'):
            encode = a
        if o in ('--nodisplay',):
            nodisplay = True
        if o in ('--stdin',):
            readStdin = True
        if o in ('--wintitle'):
            title = a
            
    if readStdin:
        content = sys.stdin.read()
    else:
        content = args[0]
        
    if decode:
        content = content.decode(decode)
        
    if isinstance(content, unicode):
        content = content.encode(encode)
        
    qrImage = qrcode.make(content)
    
    if filename:
        qrImage.save(filename)
    
    if not nodisplay:
        root = Tk()
        root.title(title)
        photo = ImageTk.PhotoImage(qrImage)
        label = Label(root, image=photo)
        label.pack()
        root.mainloop()
     
     
if __name__ == '__main__':
    main(sys.argv)