from myhdl import (
    block, Signal, enum, intbv,
    ConcatSignal,
    always_seq, always_comb, always, instances)

from wavesynlib.cores.delayer import Delayer



@block
def DHT11(
        dat, # Received data, Output
        valid, # Output
        inout_state, # Output, low for input, high for output
        line_out, # Output line
        line_in, # Input line
        read_dev, # INPUT
        clk, 
        reset,
        clk_freq, # Parameter Hz
        state_out=None # Output, for debugging.
    ):
    States = enum(
        'START_SIGNAL_LOW', 
        'START_SIGNAL_HIGH',
        'WAIT_RESPONSE_LOW',
        'WAIT_RESPONSE_HIGH',
        'WAIT_BIT_LOW',
        'WAIT_BIT_HIGH',
        'WAIT_BIT_DAT',
        'OUTPUT_DAT',
        'IDLE')

    READ_LINE = 0
    WRITE_LINE = 1

    state = Signal(States.IDLE)

    if state_out is not None:
        @always_comb
        def set_state_out():
            state_out.next = state
    
    timeout_20ms = Signal(bool(0))
    rst_20ms = Signal(bool(0))
    delay20ms = Delayer(timeout_20ms, clk, rst_20ms, 20e-3, clk_freq)

    timeout_40us = Signal(bool(0))
    rst_40us = Signal(bool(0))
    delay40us = Delayer(timeout_40us, clk, rst_40us, 40e-6, clk_freq)

    shift_reg = [Signal(bool(0)) for k in range(40)]
    bit_counter = Signal(intbv(0, min=0, max=41))
    dat_sig = ConcatSignal(*shift_reg)

    @always(clk.posedge)
    def transmitting():
        if reset:
            state.next = States.IDLE
        elif state == States.IDLE:
            if not read_dev:
                inout_state.next = READ_LINE
            else:
                bit_counter.next = 0
                rst_20ms.next = 1
                inout_state.next = WRITE_LINE
                valid.next = 0
                state.next = States.START_SIGNAL_LOW
        elif state == States.START_SIGNAL_LOW:
            if not timeout_20ms:
                rst_20ms.next = 0
                line_out.next = 0
            else:
                rst_40us.next = 1
                inout_state.next = READ_LINE
                state.next = States.START_SIGNAL_HIGH
        elif state == States.START_SIGNAL_HIGH:
            if not timeout_40us:
                rst_40us.next = 0
            else:
                state.next = States.WAIT_RESPONSE_LOW
        elif state == States.WAIT_RESPONSE_LOW:
            if line_in == 0:
                state.next = States.WAIT_RESPONSE_HIGH
        elif state == States.WAIT_RESPONSE_HIGH:
            if line_in == 1:
                state.next = States.WAIT_BIT_LOW
        elif state == States.WAIT_BIT_LOW:
            if line_in == 0:
                state.next = States.WAIT_BIT_HIGH
        elif state == States.WAIT_BIT_HIGH:
            if line_in == 1:
                rst_40us.next = 1
                state.next = States.WAIT_BIT_DAT
        elif state == States.WAIT_BIT_DAT:
            if not timeout_40us:
                rst_40us.next = 0
            else:
                for k in range(39):
                    shift_reg[k].next = shift_reg[k+1]
                shift_reg[39].next = line_in
                if bit_counter == 39:
                    state.next = States.OUTPUT_DAT
                else:
                    bit_counter.next = bit_counter + 1
                    state.next = States.WAIT_BIT_LOW
        elif state == States.OUTPUT_DAT:
            valid.next = 1
            dat.next = dat_sig
            state.next = States.IDLE
        else:
            state.next = States.IDLE

    return instances()



def convert_block(target):
    dat = Signal(intbv(0)[40:])
    valid = Signal(bool(0))
    line_in = Signal(bool(0))
    line_out = Signal(bool(0))
    inout_state = Signal(bool(0))
    read_dev = Signal(bool(0))
    clk = Signal(bool(0))
    reset = Signal(bool(0))
    clk_freq = 100e6
    state = Signal(intbv(0)[4:])

    inst = DHT11(dat, valid, inout_state, line_in, line_out, read_dev, clk, reset, clk_freq, state)
    inst.convert(hdl=target)



if __name__ == '__main__':
    convert_block(target='verilog')

