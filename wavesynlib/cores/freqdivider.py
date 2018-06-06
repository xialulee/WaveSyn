# -*- coding: utf-8 -*-
"""
Created on Wed Jun  6 23:35:02 2018

@author: Feng-cong Li
"""

from myhdl import block, Signal, delay, intbv, \
    always_comb, always_seq, instance
    
    
    
@block
def _DividerEven(out, in_, factor):
    N = factor // 2 - 1
    cnt = intbv(0, min=0, max=N+1)
    
    @always_seq(in_.posedge, reset=None)
    def do():
        if cnt == N:
            out.next = not out
            cnt[:] = 0
        else:
            out.next = out
            cnt[:] = cnt[:]+1
    return do



@block
def _DividerOdd(out, in_, factor):
    N1 = factor // 2
    N2 = N1 - 1
    cnt1 = intbv(0, min=0, max=N1+1)
    cnt2 = intbv(0, min=0, max=N1+1)
    out1 = Signal(bool(0))
    out2 = Signal(bool(0))
    
    @always_seq(in_.posedge, reset=None)
    def on_posedge():
        if not out1:
            if cnt1 == N1:
                out1.next = 1
                cnt1[:] = 0
            else:
                out1.next = 0
                cnt1[:] = cnt1[:] + 1
        else:
            if cnt1 == N2:
                out1.next = 0
                cnt1[:] = 0
            else:
                out1.next = 1
                cnt1[:] = cnt1[:] + 1
                
    @always_seq(in_.negedge, reset=None)
    def on_negedge():
        if not out2:
            if cnt2 == N1:
                out2.next = 1
                cnt2[:] = 0
            else:
                out2.next = 0
                cnt2[:] = cnt2[:] + 1
        else:
            if cnt2 == N2:
                out2.next = 0
                cnt2[:] = 0
            else:
                out2.next = 1
                cnt2[:] = cnt2[:] + 1
                
    @always_comb
    def or_gate():
        out.next = out1 | out2
        
    return on_posedge, on_negedge, or_gate
    



@block
def ClockDivider(out, in_, factor):
    if factor % 2:
        divider = _DividerOdd(out, in_, factor)
    else:
        divider = _DividerEven(out, in_, factor)
    return divider



@block
def Test(factor):
    in_clk = Signal(False)
    out_clk = Signal(False)
    divider = ClockDivider(out_clk, in_clk, factor)
    @instance
    def stimulus():
        for k in range(64):
            in_clk.next = not in_clk
            print(in_clk, out_clk)
            yield delay(10)
    return divider, stimulus



import sys

if __name__ == '__main__':
    inst = Test(int(sys.argv[1]))
    inst.run_sim()