# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 02:05:45 2018

@author: Feng-cong Li
"""

from myhdl import modbv, block, always, always_comb, Signal, instance, instances, delay



def _and(a, b):
    return a and b

def _or(a, b):
    return a or b

def _xor(a, b):
    return a != b



@block
def BitReduce(
        result, # Output
        bitvec, # Input
        op # Parameter, str: "and", "or", "xor". 
    ):
    if op=='and':
        verilog_op = '&'
        vhdl_op = 'and'
        op = _and
    elif op=='or':
        verilog_op = '|'
        vhdl_op = 'or'
        op = _or
    elif op=='xor':
        verilog_op = '^'
        vhdl_op = 'xor'
        op = _xor
    else:
        raise NotImplementedError
        
    @always(bitvec)
    def do():
        # For MyHDL simulation.
        temp = bitvec[0]
        for i in range(1, len(bitvec)):
            temp = op(temp, bitvec[i])
        result.next = temp
    result.driven = 'wire'
    return instances()

# For Verilog convertion.
BitReduce.verilog_code = 'assign $result = $verilog_op$bitvec;'

# I believe that VHDL2008 support this.
BitReduce.vhdl_code = '$result <= $vhdl_op $bitvec;'
