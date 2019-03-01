# -*- coding: utf-8 -*-
"""
Created on Fri Mar  1 19:09:48 2019

@author: Feng-cong Li
"""

from myhdl import block, Signal, delay, always_comb, instances



@block
def Abs(
        abs_output,
        int_input):
    INT_WIDTH = len(int_input)
    
    @always_comb
    def abs_calculator():
        if int_input[INT_WIDTH-1]:
            abs_output.next = ~int_input + 1
        else:
            abs_output.next = int_input
            
    return instances()



@block
def SignGetter(
        sign_output,
        int_input):
    INT_WIDTH = len(int_input)
    
    @always_comb
    def getter():
        sign_output.next = int_input[INT_WIDTH-1]
        
    return instances()
