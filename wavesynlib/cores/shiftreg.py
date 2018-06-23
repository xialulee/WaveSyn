# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 15:09:36 2018

@author: Feng-cong Li
"""

from myhdl import block, always_seq, Signal, modbv, delay, instance, instances



@block
def DelayReg(bitout, bitin, clk, posedge=True, order=4):
    if posedge:
        edge = clk.posedge
    else:
        edge = clk.negedge
              
    if order > 1:
        buf = [Signal(bool(0)) for i in range(order-1)]
            
        @always_seq(edge, reset=None)
        def do():
            buf[0].next = bitin
            for i in range(1, len(buf)):
                buf[i].next = buf[i-1]
            bitout.next = buf[len(buf)-1]
    elif order == 1:
        @always_seq(edge, reset=None)
        def do():
            bitout.next = bitin
    else:
        raise ValueError('order should be interger larger than 0.')             
    
    return instances()



@block
def ShiftBuf(buf, bitin, clk, posedge=True, width=4, direction='right'):
    if posedge:
        edge = clk.posedge
    else:
        edge = clk.negedge
        
    if width < 1:
        raise ValueError('width should larger than 0.')
        
    buf = [Signal(bool(0)) for i in range(width)]
    
    if direction.lower() in ('right', 'r'):
        @always_seq(edge, reset=None)
        def do():
            for i in range(0, width-1):
                buf[i].next = buf[i+1]
            buf[width-1].next = bitin
    elif direction.lower() in ('left', 'l'):
        @always_seq(edge, reset=None)
        def do():
            for i in range(1, width):
                buf[i].next = buf[i-1]
            buf[0].next = bitin        
        
    return instances()
            
            
@block
def Test():
    order = 4
    bitout = Signal(bool(0))
    bitin = Signal(bool(1))
    clk = Signal(bool(0))
    
    shift = DelayReg(bitout, bitin, clk, order=order)
    
    @instance
    def stimulus():
        print('clk\tbitout')
        for k in range(order*2):
            yield delay(10)
            clk.next = 1
            yield delay(10)
            clk.next = 0
            print(clk, bitout, sep='\t')
            
    return instances()



def convert_test(hdl):
    order = 2
    bitin = Signal(bool(0))
    bitout = Signal(bool(0))
    clk = Signal(bool(0))
    delayreg = DelayReg(bitout, bitin, clk, order=order)
    delayreg.convert(hdl=hdl)
    
    width = 4
    buf = [Signal(bool(0)) for i in range(width)]
    shiftbuf = ShiftBuf(buf, bitin, clk, width=width)
    shiftbuf.convert(hdl=hdl)



import sys

if __name__ == '__main__':
    if sys.argv[0] == 'simulate':
        test= Test()
        test.run_sim()
    elif sys.argv[1] == 'convert':
        convert_test(hdl=sys.argv[2])