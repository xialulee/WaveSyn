# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 00:46:11 2018

@author: Feng-cong Li
"""
from os import environ

from wavesynlib.gadgets.wsmakeqrcode import main

main(['', environ['QUTE_URL']])