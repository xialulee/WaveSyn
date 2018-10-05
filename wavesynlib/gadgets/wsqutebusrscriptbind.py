# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 23:05:06 2018

@author: Feng-cong Li
"""

import pathlib
import tkinter
from tkinter import messagebox, simpledialog, filedialog



def main():
    root = tkinter.Tk()
    root.withdraw()
    
    self_path = pathlib.Path(__file__)
    init_dir = self_path.parent / '..' / 'interfaces/net/browsers/qutebrowser/userscripts'
    
    script_path = filedialog.askopenfilename(title='Select script file', initialdir=init_dir)
    if not script_path:
        return
    
    key_chain = simpledialog.askstring('Key chain', 'Please input the key chain:')
    if not key_chain:
        return
    
    messagebox.showinfo('Bind command', f'bind {key_chain} spawn --userscript {script_path}')
    
    
    
if __name__ == '__main__':
    main()