# -*- coding: utf-8 -*-
"""
Created on Mon Jul 30 18:10:50 2018

@author: Feng-cong Li
"""

from myhdl import Signal, intbv, always_comb, instance, instances, block, delay



@block
def Bin8ToBCD(bcd, binary):
    assert len(bcd)==12
    assert len(binary)==8
    
    @always_comb
    def calc():
        temp = intbv(0)[12:]
        # Iterate from 7 to 0 is more appropriate,
        # but MyHDL only supports loop with step larger than zero. 
        for i in range(8):
            for j in range(3):
                if temp[4*(j+1):4*j] >= 5:
                    temp[4*(j+1):4*j] += 3
            temp[:] <<= 1
            temp[0] = binary[7-i]
                            
        bcd.next = temp
        
    return instances()



@block
def Test():
    binary = Signal(intbv(0)[8:])
    bcd = Signal(intbv(0)[12:])
    
    bin2bcd = Bin8ToBCD(bcd, binary)
    
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



def convert_test(target):
    binary = Signal(intbv(0)[8:])
    bcd = Signal(intbv(0)[12:])
    bin2bcd = Bin8ToBCD(bcd, binary)
    bin2bcd.convert(hdl=target)



import sys

if __name__ == '__main__':
    if sys.argv[1] == 'simulate':
        test = Test()
        test.run_sim()
    elif sys.argv[1] == 'convert':
        convert_test(target=sys.argv[2])