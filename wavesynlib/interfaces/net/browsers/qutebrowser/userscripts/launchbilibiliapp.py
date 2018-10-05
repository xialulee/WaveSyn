# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 21:52:36 2018

@author: Feng-cong Li
"""

# Only works on Windows with bilibili uwp app installed. 

import os
import re
import webbrowser



def main():
    url = os.environ['QUTE_URL']
    
    # Get the Live room ID if the URL is a live room.
    m = re.search('live\D*(\d+)', url)
    if m:
        webbrowser.open(f'bilibili://live/{m.group(1)}')
        return
    
    # Get the ID of the video.
    m = re.search('av(\d+)', url)
    if m:
        webbrowser.open(f'bilibili://video/{m.group(1)}')
        return
        
        
        
if __name__ == '__main__':
    main()
