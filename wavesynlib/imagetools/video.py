# -*- coding: utf-8 -*-
"""
Created on Thu Feb 25 23:10:39 2016

@author: Feng-cong Li
"""

from six.moves import xrange

import cv2

FRAME_NUM = cv2.cv.CV_CAP_PROP_FRAME_COUNT


def get_frames(filename, start=0, stop=-1, step=1):
    try:
        video = cv2.VideoCapture(filename)
        frame_num = int(video.get(FRAME_NUM))
        if stop < 0:
            stop = frame_num
        frame_indices = set(xrange(start, stop, step))
        for index in xrange(frame_num):
            image = video.read()
            if index in frame_indices:
                yield image
    finally:
        video.release()