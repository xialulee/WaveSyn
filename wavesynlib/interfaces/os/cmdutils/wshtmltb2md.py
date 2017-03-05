# -*- coding: utf-8 -*-
"""
Created on Sun Mar 05 20:02:23 2017

@author: Feng-cong Li
"""

from __future__ import print_function, division, unicode_literals

import sys
from wavesynlib.languagecenter.html.utils import get_table_text



def main(argv):
    html_code = sys.stdin.read()
    table = get_table_text(html_code)
    print(table)