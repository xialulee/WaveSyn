# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 21:53:19 2019

@author: Feng-cong Li
"""

from myhdl import (block, Signal, intbv, modbv, instances, always_comb, 
    ConcatSignal)

LEFT = 0
RIGHT = 1


# (* use_dsp48 = "yes" *)
# Force Vivado use DSP for multiply.
@block
def MultShifter(
        shifted,
        data,
        direction,        
        num
        ):
    WIDTH = len(data)
    MAX_SHIFT = 2**len(num)
        
    line_in_bits  = [Signal(bool(0)) for k in range(WIDTH)]    
    @always_comb
    def line_in_conn():
        for k in range(WIDTH):
            line_in_bits[k].next = data[k]
    line_in_origin   = ConcatSignal(*reversed(line_in_bits))
    line_in_reversed = ConcatSignal(*line_in_bits)
    line_in = Signal(modbv(0)[WIDTH:])
    @always_comb
    def line_in_mux():
        if direction==LEFT:
            line_in.next = line_in_origin
        else:
            line_in.next = line_in_reversed
    
    line_out = Signal(modbv(0)[WIDTH:])
    line_out_bits = [Signal(bool(0)) for k in range(WIDTH)]
    @always_comb
    def line_out_conn():
        for k in range(WIDTH):
            line_out_bits[k].next = line_out[k]
    line_out_origin   = ConcatSignal(*reversed(line_out_bits))
    line_out_reversed = ConcatSignal(*line_out_bits)    
    @always_comb
    def shifted_mux():
        if direction==LEFT:
            shifted.next = line_out_origin
        else:
            shifted.next = line_out_reversed
                
    m = Signal(modbv(0)[WIDTH:])
        
    @always_comb
    def num_to_pow():
        temp = modbv(0)[WIDTH:]
        for k in range(WIDTH):
            if k == num:
                temp[k] = 1
        m.next = temp
        
    @always_comb
    def shift():
        if num > WIDTH - 1:
            line_out.next = 0
        else:
            line_out.next = line_in * m
        
    return instances()
    


def convert():
    shifted = Signal(modbv(0)[32:])
    data = Signal(modbv(0)[32:])
    num = Signal(modbv(0)[5:])
    direction = Signal(bool(0))
    
    inst = MultShifter(shifted=shifted, data=data, direction=direction, num=num)
    inst.convert(hdl='verilog')
    
    
    
if __name__ == '__main__':
    convert()
