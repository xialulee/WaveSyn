# -*- coding: utf-8 -*-
"""
Created on Sun Feb 24 22:41:10 2019

@author: Feng-cong Li
"""

from myhdl import (
        block, Signal, delay, modbv, intbv, ConcatSignal,
        always_comb, instance, instances)
from struct import pack, unpack
from wavesynlib.cores.priorityencoder import PriorityEncoder
from wavesynlib.cores.abs import Abs, SignGetter



def uint_to_float(unsigned_int):
    return unpack('f', 
                  pack('I', unsigned_int))



@block
def UIntToFraction(
        fraction_output,
        uint_input,
        unbiased_exponent_input
    ):
    '''\
Calculating the fraction part of the given uint and unbiased exponent.'''
    FRACTION_WIDTH = len(fraction_output)
    
    @always_comb
    def m_shifter():        
        if unbiased_exponent_input > FRACTION_WIDTH:
            fraction_output.next = uint_input >> \
                (unbiased_exponent_input - FRACTION_WIDTH)
        else:
            fraction_output.next = uint_input << \
                (FRACTION_WIDTH - unbiased_exponent_input)
        
    return instances()



@block
def UIntToFloat(
        float_output,
        uint_input,
        exponent_width,
        fraction_width,
        exponent_bias
    ):
    
    # Calculating unbiased and biased exponent.
    unbiased_exponent = Signal(modbv(0)[exponent_width:])
    biased_exponent = Signal(modbv(0)[exponent_width:])
    nz_flag = Signal(bool(0))
    unbiased_exponent_calculator = PriorityEncoder(
            unbiased_exponent, nz_flag, uint_input)
    @always_comb
    def biased_exponent_calculator():
        biased_exponent.next = unbiased_exponent + exponent_bias
    
    # Calculating fraction part. 
    fraction = Signal(modbv(0)[fraction_width:])
    fraction_calculator = UIntToFraction(
            fraction, uint_input, unbiased_exponent)
    
    float_sig = ConcatSignal(bool(0), biased_exponent, fraction)
    
    @always_comb
    def make_output():
        if uint_input == 0:
            float_output.next = 0
        else:
            float_output.next = float_sig
        
            
    return instances()



@block
def IntToFloat(
        float_output,
        int_input,
        exponent_width,
        fraction_width,
        exponent_bias):
    INT_WIDTH = len(int_input)
    FLOAT_WIDTH = len(float_output)
    
    sign = Signal(bool(0))
    sign_getter = SignGetter(sign, int_input)
    
    abs_int = Signal(modbv(0)[INT_WIDTH:])           
    abs_calculator = Abs(abs_int, int_input)
    
    abs_float = Signal(modbv(0)[(1+exponent_width+fraction_width):])         
    float_calculator = UIntToFloat(
            abs_float, abs_int, 
            exponent_width, fraction_width, exponent_bias)
    
    signed_float = ConcatSignal(sign, abs_float(FLOAT_WIDTH-1, 0))
    
    @always_comb
    def make_output():
        float_output.next = signed_float
        
    return instances()
    


@block
def Test():
    # IEEE754 Single
    EXPONENT_WIDTH = 8
    FRACTION_WIDTH = 23
    EXPONENT_BIAS = 127
    
    INT_WIDTH = 6
    
    float_sig = Signal(modbv(0)[(1+EXPONENT_WIDTH+FRACTION_WIDTH):])
    int_sig = Signal(modbv(0)[INT_WIDTH:])
    
    convertor = IntToFloat(
            float_sig,
            int_sig,
            exponent_width=EXPONENT_WIDTH,
            fraction_width=FRACTION_WIDTH,
            exponent_bias=EXPONENT_BIAS)
    
    @instance
    def stimulus():
        print('input', 'output', sep='\t')
        for k in range(-2**(INT_WIDTH-1), 2**(INT_WIDTH-1)):
            int_sig.next = k
            yield delay(10)
            int_val = int(int_sig)
            if k < 0:
                int_val = ~int_val + 1
                int_val &= 2**INT_WIDTH - 1
                int_val = -int_val
            print(int_val, uint_to_float(int(float_sig))[0], sep='\t')
            
    return instances()



def convert_int_to_float(target):
    EXPONENT_WIDTH = 8
    FRACTION_WIDTH = 23
    EXPONENT_BIAS = 127
    
    INT_WIDTH = 6    

    float_sig = Signal(modbv(0)[(1+EXPONENT_WIDTH+FRACTION_WIDTH):])
    int_sig = Signal(modbv(0)[INT_WIDTH:])
    
    convertor = IntToFloat(
            float_sig,
            int_sig,
            exponent_width=EXPONENT_WIDTH,
            fraction_width=FRACTION_WIDTH,
            exponent_bias=EXPONENT_BIAS)
    
    convertor.convert(hdl=target)



import sys

if __name__ == '__main__':
    if sys.argv[1] == 'simulate':
        test = Test()
        test.run_sim()
    elif sys.argv[1] == 'convert':
        convert_int_to_float(sys.argv[2])
    