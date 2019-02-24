# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 22:41:10 2019

@author: Feng-cong Li
"""

from myhdl import block, Signal, delay, intbv, modbv, always_comb, instance, instances
from wavesynlib.cores.priorityencoder import PriorityEncoder



@block
def MShifter(
    shifted_sig,
    unsigned_int,
    width_e):
    '''\
Convert unsigned interger to float.'''
    M_WIDTH = len(shifted_sig)
    e_sig_unbiased = Signal(modbv(0)[width_e:])
    nz_flag = Signal(bool(0))
    
    detector = PriorityEncoder(e_sig_unbiased, nz_flag, unsigned_int)
    
    @always_comb
    def m_shifter():        
        if e_sig_unbiased > M_WIDTH:
            shifted_sig.next = unsigned_int >> (e_sig_unbiased - M_WIDTH)
        else:
            shifted_sig.next = unsigned_int << (M_WIDTH - e_sig_unbiased)

        
    return instances()
    


@block
def Test():
    int_width = 6
    uint_input = Signal(modbv(0)[int_width:])
    width_m = 23
    shifted_sig = Signal(modbv(0)[width_m:])
    
    shifter = MShifter(shifted_sig, uint_input, width_e=8)
    
    @instance
    def stimulus():
        print('input\toutput')
        for k in range(2**6):
            uint_input.next = k
            yield delay(10)
            print(f'{int(uint_input):0{int_width}b}', f'{int(shifted_sig):0{width_m}b}', sep='\t')
    return instances()



if __name__ == '__main__':
    test = Test()
    test.run_sim()
    