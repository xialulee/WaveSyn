# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 18:04:01 2017

@author: Feng-cong Li
"""
import sys
from wavesynlib.widgets.matplotlibwidgets import ImageFrame
from tkinter import Tk
import pylab
import numpy as np
import cv2
import time


# see https://stackoverflow.com/questions/38048650/opencv-grabcut-background-color-and-contour-in-python
if __name__ == '__main__':
    root = Tk()
    frame = ImageFrame(root)
    frame.pack(side='top', fill='both', expand='yes')
    filename = sys.argv[1]
    im = cv2.imread(filename)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    frame.axes.imshow(im)
    
    def callback(rect, dumb):
        mask = np.zeros(im.shape[:2], np.uint8)
        t_0 = time.time()
        cv2.grabCut(im, mask, rect, None, None, 6, cv2.GC_INIT_WITH_RECT)
        deltaT = time.time() - t_0
        print(f'deltaT = {deltaT}')
        mask = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
        img = im * mask[:,:, np.newaxis]
        pylab.imshow(img)
        pylab.show()
        
    frame.rectselector.callback = callback    
    frame.rectselector.activate()
    root.mainloop()
    
    