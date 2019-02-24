# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 00:22:19 2018

@author: Feng-cong Li
"""

from myhdl import block, Signal, delay, modbv, always_comb, instance, instances



@block
def PriorityEncoder(
        code,  # Output
        valid, # Output
        in_    # Input
    ):
    L = len(in_)
    @always_comb
    def search():
        valid.next = 1 if in_ else 0
        code.next = 0
        for k in range(L):
            if in_[k]:
                code.next = k
    return search



@block
def Test():
    code = Signal(modbv(0)[2:])
    valid = Signal(bool(0))
    in_ = Signal(modbv(0)[4:])
    
    encoder = PriorityEncoder(code, valid, in_)
    
    @instance
    def stimulus():
        print('code\tvalid\tin')
        for k in range(16):
            in_.next = k
            yield delay(10)
            print(code, valid, f'{int(in_):04b}', sep='\t')
    return instances()



if __name__ == '__main__':
    test = Test()
    test.run_sim()
    