# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 17:00:03 2019

@author: Feng-cong Li
"""

from myhdl import (
    enum, block, 
    modbv, intbv, ConcatSignal,
    Signal, ResetSignal, always, always_comb, always_seq,
    instances, instance, delay)



@block
def PS2Keyboard(
        code,
        finish,
        kb_dat,
        kb_clk,
        rst
    ):
    States = enum('READ', 'FINISH')

    state = Signal(States.FINISH)

    # Eight Data bits and One Parity. 
    bits = [Signal(bool(0)) for k in range(9)]
    code_reg = ConcatSignal(*bits)
    bit_counter = Signal(intbv(0, min=0, max=10))
    
    @always_seq(kb_clk.posedge, reset=rst)
    def receiving():
        if state == States.FINISH:
            if not kb_dat:
                # kb_dat=0, device starts a new transmission. 
                state.next = States.READ
                finish.next = 0
            else:
                # kb_dat=1, the stop bit. 
                code.next = code_reg
                finish.next = 1
        elif state == States.READ:
            # Shift Register. 
            bits[0].next = kb_dat
            for k in range(1, 9):
                bits[k].next = bits[k-1]
            # End Shift Register.
            if bit_counter == 8:
                # Have got all the 8bits and parity.
                state.next = States.FINISH
                bit_counter.next = 0
            else:
                bit_counter.next = bit_counter + 1
        else:
            raise ValueError('Undefined state.')

    return instances()



@block
def TestKB():
    dat = Signal(bool(0))
    clk = Signal(bool(0))
    rst = ResetSignal(bool(0), active=1, isasync=True)
    code = Signal(intbv(0)[9:])
    finish = Signal(bool(0))
    
    inst = PS2Keyboard(code, finish, dat, clk, rst)

    the_data = [
        [0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1],
        [0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1]]

    @instance
    def stimulus():
        print('dat\tcode\t\tfinish')
        clk.next = 1
        yield delay(10)
        for k in range(2*11):
            bit = the_data[k//11][k%11]
            dat.next = bit 
            yield delay(10)
            clk.next = 0
            yield delay(10)
            clk.next = 1
            print(bit, f'{int(code):09b}', finish, sep='\t')

    return instances()



def convert_kb(target):
    dat = Signal(bool(0))
    clk = Signal(bool(0))
    rst = ResetSignal(bool(0), active=1, isasync=True)
    code = Signal(intbv(0)[9:])
    finish = Signal(bool(0))

    inst = PS2Keyboard(code, finish, dat, clk, rst)

    inst.convert(hdl=target)



import sys

if __name__ == '__main__':
    if sys.argv[1] == 'simulate':
        tb = TestKB()
        tb.run_sim()
    elif sys.argv[1] == 'convert':
        convert_kb(target=sys.argv[2])


