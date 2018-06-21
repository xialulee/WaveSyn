# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 22:52:04 2018

@author: Feng-cong Li
"""

from myhdl import block, always_comb, instance, instances, Signal, modbv, delay


# MSB g f e d c b a LSB
common_anode_lut = (
        0b1000000, # 0
        0b1111001, # 1
        0b0100100, # 2
        0b0110000, # 3
        0b0011001, # 4
        0b0010010, # 5
        0b0000010, # 6
        0b1111000, # 7
        0b0000000, # 8
        0b0011000, # 9
        0b0001000, # A
        0b0000011, # b
        0b1000110, # C
        0b0100001, # d
        0b0000110, # E
        0b0001110, # F
        0b1111111 # Not valid.
)


common_cathode_lut = tuple([~i & 0x7f for i in common_anode_lut])



@block
def Decoder(seg, # output, width=7
            num, # input, width=4
            common_anode=True # parameter, bool, whether the 7-seg is common anode or cathode.
    ):
    if common_anode:
        table = common_anode_lut
    else:
        table = common_cathode_lut
    @always_comb
    def do():
        seg.next = table[int(num)]
    return instances()



@block
def test():
    in_ = Signal(modbv()[4:])
    out = Signal(modbv()[7:])
    segctrl = Decoder(out, in_)
    
    @instance
    def stimulus():
        for x in range(16):
            in_.next = x
            print(out, in_)
            yield delay(10)
    
    return segctrl, stimulus



def test_convert(hdl):
    in_ = Signal(modbv()[4:])
    out = Signal(modbv()[7:])
    decoder = Decoder(out, in_, common_anode=False)
    decoder.convert(hdl=hdl)
    
    
    
import sys
    
if __name__ == '__main__':
    if sys.argv[1] == 'simulate':
        inst = test()
        inst.run_sim()
    elif sys.argv[1] == 'convert':
        test_convert(hdl=sys.argv[2])
