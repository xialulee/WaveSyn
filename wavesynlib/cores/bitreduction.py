# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 02:05:45 2018

@author: Feng-cong Li
"""

from myhdl import modbv, block, always, always_comb, Signal, instance, instances, delay



def _and(a, b):
    return a and b

def _or(a, b):
    return a or b

def _xor(a, b):
    return a != b



@block
def BitReduce(
        result, # Output
        bitvec, # Input
        op # Parameter, str: "and", "nand", "or", "nor", "xor", "nxor".
    ):
    not_ = False
    if op=='and':
        verilog_op = '&'
        vhdl_op = 'and'
        op = _and
    elif op=='nand':
        verilog_op = '~&'
        vhdl_op = 'nand'
        op = _and
        not_ = True
    elif op=='or':
        verilog_op = '|'
        vhdl_op = 'or'
        op = _or
    elif op=='nor':
        verilog_op = '~|'
        vhdl_op = 'nor'
        op = _or
        not_ = True
    elif op=='xor':
        verilog_op = '^'
        vhdl_op = 'xor'
        op = _xor
    elif op=='nxor':
        verilog_op = '~^'
        vhdl_op = 'nxor'
        op = _xor
        not_ = True
    else:
        raise NotImplementedError
        
    @always(bitvec)
    def do():
        # For MyHDL simulation.
        temp = bitvec[0]
        for i in range(1, len(bitvec)):
            temp = op(temp, bitvec[i])
        if not_:
            result.next = not temp
        else:
            result.next = temp
    result.driven = 'wire'
    return instances()

# For Verilog convertion.
BitReduce.verilog_code = 'assign $result = $verilog_op$bitvec;'

# I believe that VHDL2008 support this.
BitReduce.vhdl_code = '$result <= $vhdl_op $bitvec;'



@block
def Test(op):
    # If the initial value of in_ is 0,
    # the always block in BitReduce will not be triggered 
    # for the first iteration of the loop below. 
    in_ = Signal(modbv(15)[4:])
    out = Signal(bool(0))
    
    rd = BitReduce(out, in_, op)
    
    @instance
    def stimulus():
        print('out\tin')
        for k in range(16):
            in_.next = k       
            yield delay(10)                 
            print(out, in_, sep='\t')                      
            yield delay(10)              
            
    return instances()



def test_convert(hdl):
    bitvec = Signal(modbv(0)[4:])
    result = Signal(bool(0))
    inst = BitReduce(result, bitvec, op='nxor')
    inst.convert(hdl=hdl)



import sys

if __name__ == '__main__':
    if sys.argv[1] == 'simulate':
        test = Test(sys.argv[2])
        test.run_sim()
    elif sys.argv[1] == 'convert':
        test_convert(hdl=sys.argv[2])
