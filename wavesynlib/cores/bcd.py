# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 18:10:50 2018

@author: Feng-cong Li
"""

from myhdl import Signal, intbv, always_comb, instance, instances, block, delay

from wavesynlib.cores.abs import Abs



@block
def UByteToBCD(bcd, binary):
    assert len(bcd)==10
    assert len(binary)==8
    
    @always_comb
    def calc():
        temp = intbv(0)[12:]
        # Iterate from 7 to 0 is more appropriate,
        # but MyHDL only supports loop with step larger than zero. 
        for i in range(8):
            # Cannot use loops for following code,
            # since range must be bounded by constant expressions.
            if temp[4:0] >= 5:
                temp[4:0] += 3
            if temp[8:4] >= 5:
                temp[8:4] += 3
                    
            temp[:] <<= 1
            temp[0] = binary[7-i]
                            
        bcd.next = temp
        
    return instances()



@block
def ByteToBCD(sign, bcd, binary):
    assert len(bcd)==9
    assert len(binary)==8
    
    abs_ = Signal(intbv(0)[8:])
    abs_calculator = Abs(abs_, binary)
            
    uout = Signal(intbv(0)[10:])
    uconverter = UByteToBCD(uout, abs_)
    
    @always_comb
    def generate_output():
        sign.next = binary[7]
        bcd.next = uout[9:]
        
    return instances()



@block
def TestUByte():
    binary = Signal(intbv(0)[8:])
    bcd = Signal(intbv(0)[10:])
    
    ubyte2bcd = UByteToBCD(bcd, binary)
    
    @instance
    def stimulus():
        print('bcd\tbinary')
        for k in range(256):
            binary.next = k
            yield delay(10)
            val = ((bcd & 0xf00) >> 8)*100 + ((bcd & 0xf0) >> 4)*10 + (bcd & 0xf)
            assert val == binary
            print(bcd, binary, sep='\t')
            
    return instances()



@block
def TestByte():
    binary = Signal(intbv(0, min=-128, max=128))
    bcd = Signal(intbv(0)[9:])
    sign = Signal(bool(0))
    
    byte2bcd = ByteToBCD(sign, bcd, binary)
    
    @instance
    def stimulus():
        print('sign\tbcd\tinput')
        for k in range(-128, 128):
            binary.next = k
            yield delay(10)
            print(sign, bcd, int(binary), sep='\t')
            
    return instances()



def convert_ubyte(target):
    binary = Signal(intbv(0)[8:])
    bcd = Signal(intbv(0)[10:])
    bin2bcd = UByteToBCD(bcd, binary)
    bin2bcd.convert(hdl=target)
    
    
    
def convert_byte(target):
    binary = Signal(intbv(0)[8:])
    bcd = Signal(intbv(0)[9:])
    sign = Signal(bool(0))
    bin2bcd = ByteToBCD(sign, bcd, binary)
    bin2bcd.convert(hdl=target)



import sys

if __name__ == '__main__':
    if sys.argv[1] == 'simulate':
        if sys.argv[2] == 'ubyte':
            test = TestUByte()
        elif sys.argv[2] == 'byte':
            test = TestByte()
        test.run_sim()
    elif sys.argv[1] == 'convert':
        if sys.argv[2] == 'ubyte':
            convert_ubyte(target=sys.argv[3])
        elif sys.argv[2] == 'byte':
            convert_byte(target=sys.argv[3])