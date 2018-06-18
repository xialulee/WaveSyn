# -*- coding: utf-8 -*-
"""
Created on Sat Jun 16 20:19:50 2018

@author: Feng-cong Li
"""

from myhdl import Signal, intbv, modbv, always_seq, always_comb, instances, block, delay, instance



@block
def Stack(dout, din, full, empty, push, clk, posedge=True, width=8, depth=128):
    mem = [Signal(intbv(0)[width:]) for i in range(depth)]
    pointer = Signal(modbv(0, min=0, max=depth))
    
    if posedge:
        edge = clk.posedge
    else:
        edge = clk.negedge

    @always_seq(edge, reset=None)
    def operate():
        if push:
            if pointer == depth - 1:
                full.next = True
                empty.next = False
            if not full:
                mem[pointer].next = din
                pointer.next = pointer + 1                
        else:
            if pointer == 1:
                empty.next = True
                full.next = False
            if not empty:
                dout.next = mem[pointer-1]
                pointer.next = pointer - 1

    return instances()



@block
def Test():
    depth = 4
    width = 4
    
    dout = Signal(modbv(0)[width:])
    din = Signal(modbv(0)[width:])
    full = Signal(bool(0))
    empty = Signal(bool(0))
    push = Signal(bool(0))
    clk = Signal(bool(0))
    
    stack = Stack(dout, din, full, empty, push, clk, width=width, depth=depth)
    
    @instance
    def stimulus():
        print('dout\tdin\tfull\tempty\tpush')
        push.next = 1
        for k in range(16):
            din.next = k + 1
            push.next = k < 8
            yield delay(10)
            clk.next = 1
            yield delay(10)
            clk.next = 0
            print(dout, din, full, empty, push, sep='\t')
            
    return instances()



def convert_test(target):
    depth = 4
    width = 4
    
    dout = Signal(modbv(0)[width:])
    din = Signal(modbv(0)[width:])
    full = Signal(bool(0))
    empty = Signal(bool(0))
    push = Signal(bool(0))
    clk = Signal(bool(0))
    
    stack = Stack(dout, din, full, empty, push, clk, width=width, depth=depth)
    stack.convert(hdl=target)



import sys

if __name__ == '__main__':
    if sys.argv[1] == 'convert':
        convert_test('verilog')
    elif sys.argv[1] == 'simulate':
        test = Test()
        test.run_sim()