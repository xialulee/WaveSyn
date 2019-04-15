# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 16:31:11 2019

@author: Feng-cong Li
"""
from math import ceil, log2

from myhdl import (
        Signal, intbv, modbv, always, always_comb, always_seq,
        instances, instance, block, enum, delay)



STACK_OP = enum('PUSH', 'POP', 'UADD', 'IDLE')
STACK_OP_WIDTH = ceil(log2(len(STACK_OP)))



@block
def CalcStack(
        data_out,
        data_in,
        full,
        empty,
        op,
        op_success,
        offset,
        clk,
        posedge=True,
        width=8,
        depth=128
    ):
    
    if posedge:
        edge = clk.posedge
    else:
        edge = clk.negedge
        
    mem = [Signal(intbv(0)[width:]) for i in range(depth)]
    pointer = Signal(modbv(0, min=0, max=depth))
    
    @always_seq(edge, reset=None)
    def operate():
        # print('mem:', mem)
        if op == STACK_OP.PUSH:
            if not full:
                if pointer == depth - 1:
                    full.next = 1
                if empty:
                    empty.next = 0
                mem[pointer].next = data_in
                pointer.next = pointer + 1
                op_success.next = 1
            else:
                op_success.next = 0
        elif op == STACK_OP.POP:
            if not empty:
                if pointer == 1:
                    empty.next = 1
                if full:
                    full.next = 0
                data_out.next = mem[pointer-1]
                pointer.next = pointer - 1
                op_success.next = 1
            else:
                op_success.next = 0
        elif op == STACK_OP.UADD:
            if pointer >= 2 or full:
                mem[pointer-2].next = mem[pointer-2] + mem[pointer-1]
                pointer.next = pointer - 1
                op_success.next = 1
            else:
                op_success.next = 0
        elif op == STACK_OP.IDLE:
            pass
        else:
            pass
        
    return instances()



@block
def Testbench():
    stack_out  = Signal(intbv(0)[8:])
    stack_in   = Signal(intbv(0)[8:])
    full       = Signal(bool(0))
    empty      = Signal(bool(0))
    op         = Signal(STACK_OP.IDLE)
    op_success = Signal(bool(0))
    clk        = Signal(bool(0))
    
    stack = CalcStack(
        data_out   = stack_out,
        data_in    = stack_in,
        full       = full,
        empty      = empty,
        op         = op,
        op_success = op_success,
        offset     = 0,
        clk        = clk,
        depth      = 4)
    
    @instance
    def do():
        print('out', 'in', 'full', 'empty', 'op', 'succ', sep='\t')
        stack_in.next = 3
        op.next = STACK_OP.PUSH
        clk.next = 0
        yield delay(10)
        clk.next = 1
        yield delay(10)
        
        stack_in.next = 4
        op.next = STACK_OP.PUSH
        clk.next = 0
        yield delay(10)
        clk.next = 1
        yield delay(10)

        stack_in.next = 5
        op.next = STACK_OP.PUSH
        clk.next = 0
        yield delay(10)
        clk.next = 1
        yield delay(10)        

        op.next = STACK_OP.POP        
        clk.next = 0        
        yield delay(10)
        clk.next = 1
        yield delay(10)
        print(stack_out, stack_in, full, empty, op, op_success, sep='\t')
        
    return instances()



def test():
    inst = Testbench()
    inst.run_sim()
    
    
    
if __name__ == '__main__':
    test()
    
    