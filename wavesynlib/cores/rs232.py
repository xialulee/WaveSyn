# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 14:47:57 2018

@author: Feng-cong Li
"""

from myhdl import block, Signal, modbv, intbv, instances, always_comb, always_seq
from wavesynlib.cores.shiftreg import DelayReg



@block
def RS232(
        rx, # input, receive
        tx, # output, transmit
        rx_available, # output
        tx_available, # output
        rx_reg, # output, 8bit
        tx_reg, # input, 8bit
        clk,
        rst,
        baud_rate, # parameter, Hz
        clk_freq, # parameter, Hz
    ):
    bit_bound = clk_freq // baud_rate
    samp_moment = bit_bound // 2
    
    # Handling async rx signal
    rx_delay0 = Signal(bool(0))
    async_delay = DelayReg(rx_delay0, rx, clk, order=4)
    
    rx_delay1 = Signal(bool(0))
    event_detect = DelayReg(rx_delay1, rx_delay0, clk, order=1)
    
    rx_event = Signal(bool(0))
            
    clk_counter = Signal(intbv(0, min=0, max=bit_bound))
    bit_counter = Signal(intbv(0, min=0, max=10))
    samp_pulse = Signal(bool(0))
    receiving = Signal(bool(0))
    
    @always_comb
    def comb_do():
        rx_event.next = rx_delay0 != rx_delay1
        samp_pulse.next = clk_counter==samp_moment
        
    @always_seq(clk.posedge, reset=None)
    def seq_do():
        if rx_event or clk_counter==bit_bound-1:
            # A new bit starts
            clk_counter.next = 0
        else:
            clk_counter.next = clk_counter + 1
                        
        if samp_pulse and not rx_delay0 and not receiving:
            receiving.next = True
        elif receiving and bit_counter==9 and samp_pulse:
            receiving.next = False
            
        if receiving:
            if samp_pulse:
                bit_counter.next = bit_counter + 1
                rx_reg.next = (rx_reg >>1) | (rx_delay0<<7)
        else:
            bit_counter[:] = 0
    
    return instances()



def test_convert(hdl):
    rx = Signal(bool(0))
    tx = Signal(bool(0))
    rx_available = Signal(bool(0))
    tx_available = Signal(bool(0))
    rx_reg = Signal(modbv(0)[8:])
    tx_reg = Signal(modbv(0)[8:])
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    baud_rate = 9600
    clk_freq = 100000000
    
    inst = RS232(rx, tx, rx_available, tx_available, rx_reg, tx_reg, clk, rst, baud_rate=baud_rate, clk_freq=clk_freq)
    inst.convert(hdl=hdl)
    
    
    
import sys
    
if __name__ == '__main__':
    if sys.argv[1] == 'convert':
        test_convert(hdl=sys.argv[2])