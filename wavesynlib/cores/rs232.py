# -*- coding: utf-8 -*-
"""
Created on Sat Jun 23 14:47:57 2018

@author: Feng-cong Li
"""

from myhdl import block, Signal, modbv, intbv, instance, instances, always_comb, always_seq, delay
from wavesynlib.cores.shiftreg import DelayReg
from wavesynlib.cores.bitreduction import BitReduce



@block
def RS232(
        rx, # input, receive
        tx, # output, transmit
        rx_finish, # output, posedge presenting a receiving process is finished.
        tx_occupy, # output
        tx_start, # posedge for staring a transmitting process.
        rx_reg, # output, 8bit
        tx_reg, # input, 8bit
        clk,
        rst,
        baud_rate, # parameter, Hz
        clk_freq, # parameter, Hz
    ):
    bit_interval = clk_freq // baud_rate
    samp_moment = bit_interval // 2
        
    # Handling async rx signal using shifting registers.
    rx_delay0 = Signal(bool(0))
    async_delay = DelayReg(rx_delay0, rx, clk, order=4)
    
    # Store the previous bit of the rx_delay0, for change detection. 
    rx_delay1 = Signal(bool(0))
    event_detect = DelayReg(rx_delay1, rx_delay0, clk, order=1)
    
    # Signal for detecting RX level change. 
    rx_event = Signal(bool(0))
            
    rx_clk_counter = Signal(intbv(0, min=0, max=bit_interval))
    rx_bit_counter = Signal(intbv(0, min=0, max=10))
    samp_pulse = Signal(bool(0))
    receiving = Signal(bool(0))
    
    # Register for storing the transmitting byte.
    tx_buf = Signal(intbv(0, min=0, max=256))
    # Transmitting status
    tx_available = Signal(bool(1))
    tx_clk_counter = Signal(intbv(0, min=0, max=bit_interval))
    tx_bit_counter = Signal(intbv(0, min=0, max=12))
    tx_checker_bit = Signal(bool(0))
    tx_checker_bit_gen = BitReduce(tx_checker_bit, tx_buf, 'xor')
    
    @always_comb
    def comb_do():
        # RX level change detected. 
        rx_event.next = rx_delay0 != rx_delay1
        # Generating the bit sampling pulse based on the clock counter.
        # The sampling moment is roughly on the middle of a bit. 
        samp_pulse.next = rx_clk_counter==samp_moment
        tx_occupy.next = not tx_available
        
    @always_seq(clk.posedge, reset=None)
    def seq_do():
        # For receiving
        if rx_event or rx_clk_counter==bit_interval-1:
            # A new bit starts
            rx_clk_counter.next = 0
        else:
            rx_clk_counter.next = rx_clk_counter + 1
                        
        if samp_pulse and not rx_delay0 and not receiving:
            receiving.next = True
        elif receiving and rx_bit_counter==9 and samp_pulse:
            receiving.next = False
            
#        if receiving:
#            if samp_pulse:
#                rx_bit_counter.next = rx_bit_counter + 1
#                rx_reg.next = (rx_reg >>1) | (rx_delay0<<7)
#        else:
#            rx_bit_counter.next = 0
            
        rx_finish.next = receiving and samp_pulse and (rx_bit_counter==9)
        
        # For transmitting
        if tx_available:
            tx.next = 1
            if tx_start:
                tx_buf.next = tx_reg
                tx_available.next = 0
            
        if not tx_available: 
            if tx_bit_counter==11: # Transmitting finished.                
                tx_available.next = 1
                tx_bit_counter.next = 0
                tx_clk_counter.next = 0
            else:
                if tx_clk_counter == bit_interval-1:
                    tx_clk_counter.next = 0
                    tx_bit_counter.next = tx_bit_counter + 1
                else:
                    tx_clk_counter.next = tx_clk_counter + 1
                if tx_bit_counter == 0: # Start bits, low level. 
                    tx.next = 0
                elif tx_bit_counter == 9: # Parity bit.
                    tx.next = tx_checker_bit
                elif tx_bit_counter == 10: # Stop bit
                    tx.next = 1
                else:
                    tx.next = tx_buf[tx_bit_counter-1]
                
    return instances()



@block
def Test():
    rx = Signal(bool(0))
    tx = Signal(bool(1))
    rx_finish = Signal(bool(0))
    tx_occupy = Signal(bool(0))
    tx_start = Signal(bool(1))
    rx_reg = Signal(modbv(0)[8:])
    tx_reg = Signal(modbv(0b11010100)[8:])
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    baud_rate = 9600
    clk_freq = 9600*4    
    
    inst = RS232(rx, tx, rx_finish, tx_occupy, tx_start, rx_reg, tx_reg, clk, rst, baud_rate=baud_rate, clk_freq=clk_freq)  
        
    @instance
    def stimulus():
        for k in range(100):
            yield delay(10)
            clk.next = not clk    
    return instances()        



def test_convert(hdl):
    rx = Signal(bool(0))
    tx = Signal(bool(0))
    rx_finish = Signal(bool(0))
    tx_occupy = Signal(bool(0))
    tx_start = Signal(bool(1))
    rx_reg = Signal(modbv(0)[8:])
    tx_reg = Signal(modbv(0b01010101)[8:])
    clk = Signal(bool(0))
    rst = Signal(bool(0))
    baud_rate = 9600
    clk_freq = 100000000
    
    inst = RS232(rx, tx, rx_finish, tx_occupy, tx_start, rx_reg, tx_reg, clk, rst, baud_rate=baud_rate, clk_freq=clk_freq)
    inst.convert(hdl=hdl)
    
    
    
import sys
    
if __name__ == '__main__':
    if sys.argv[1] == 'convert':
        test_convert(hdl=sys.argv[2])
    elif sys.argv[1] == 'simulate':
        tb = Test()
        tb.config_sim(trace=True)
        tb.run_sim()