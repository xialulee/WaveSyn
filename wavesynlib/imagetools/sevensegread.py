# -*- coding: utf-8 -*-
"""
Created on Mon May 14 15:49:34 2018

@author: Feng-cong Li
"""

import cv2
import sys
import numpy as np

image = cv2.imread(sys.argv[1])
#image = cv2.imread('./5.jpg')
ratio = image.shape[0] / image.shape[1]
orig = image.copy()
image = cv2.resize(image, (int(500/ratio), 500))
scale = orig.shape[0] / 500
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
cv2.imwrite('./gray.jpg', gray)
gray = cv2.GaussianBlur(gray, (5, 5), 0)
cv2.imwrite('./blurred.jpg', gray)
edged = cv2.Canny(gray, threshold1=75, threshold2=200, apertureSize=3) # 75 200

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,3))
dilated = cv2.dilate(edged, kernel)

cv2.imwrite('./dilated.jpg', dilated)

cnts = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
boxes = []
for c in cnts:
    x, y, w, h = cv2.boundingRect(c)

    if h>2*w:
        boxes.append((x,y,w,h))
        points = np.zeros((4,1,2), dtype=int)
        points[0, 0, :] = (x, y)
        points[1, 0, :] = (x+w, y)
        points[2, 0, :] = (x+w, y+h)
        points[3, 0, :] = (x, y+h)
        cv2.drawContours(image, [points], -1, (0,0,255), 2)
        
cv2.imwrite('./box.jpg', image)
cv2.imwrite('./edge.jpg', edged)


def check_seg(image, start, stop, offset, vertical=False):
    if vertical:
        line = image[start:stop, offset]
    else:
        line = image[offset, start:stop]
    if np.sum(line>0)==2:
        return 1
    else:
        return 0
    
    
    
def check_one(image, x, y, w, h):
    line1 = image[y+h//4, x:x+w]
    line2 = image[y+h//4*3, x:x+w]
    if np.sum(line1>0)==2 and np.sum(line2>0)==2:
        return True
    else:
        return False



digit_map = {
    '1101101': 2,
    '1111001': 3,
    '0110011': 4,
    '1011011': 5,
    '1011111': 6,
    '1110010': 7,
    '1111111': 8,
    '1111011': 9,
    '1111110': 0
}

label = 96

for box in boxes:
    x, y, w, h = box
    if h > 5*w:
        #print(h, w, 5*w, end=' ')
        if check_one(edged, x, y, w, h):
            L = '1'
        else:
            L = ''
    else:
        result = [0] * 7
        # A seg
        result[0] = check_seg(edged, y, y+h//4, x+w//2, True)
        # B seg
        result[1] = check_seg(edged, x+w//2, x+w, y+h//4, False)
        # C seg
        result[2] = check_seg(edged, x+w//2, x+w, y+h//4*3, False)
        # D seg
        result[3] = check_seg(edged, y+h//4*3, y+h, x+w//2, True)
        # E seg
        result[4] = check_seg(edged, x, x+w//2, y+h//4*3, False)
        # F seg
        result[5] = check_seg(edged, x, x+w//2, y+h//4, False)
        # G seg
        result[6] = check_seg(edged, y+h//2-h//6, y+h//2+h//6, x+w//2, True)
        result = ''.join(map(str, result))
        
        L = ''
        if result in digit_map:
            L = str(digit_map[result])
        else:
            L = ''
            #label += 1
    cv2.putText(image, L, (x,y), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 0), lineType=2, thickness=3)
    print(result, L, (x,y,w,h))
    
cv2.imwrite('Labeled.jpg', image)


