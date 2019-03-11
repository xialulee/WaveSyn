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
        clk_freq # Parameter Hz
    ):
    States = enum(
        'START_SIGNAL_LOW', 
        'START_SIGNAL_HIGH',
        'WAIT_RESPONSE_LOW',
        'WAIT_RESPONSE_HIGH',
        'WAIT_BIT_LOW',
        'WAIT_BIT_HIGH',
        'WAIT_DAT_BIT',
        'IDLE')

    READ_LINE = 0
    WRITE_LINE = 1

    state = Signal(States.IDLE)
    
    timeout18ms = Signal(bool(0))
    rst18ms = Signal(bool(0))
    delay18ms = Delayer(timeout18ms, clk, rst18ms, 18e-3, clk_freq)

    timeout40us = Signal(bool(0))
    rst40us = Signal(bool(0))
    delay40us = Delayer(timeout40us, clk, rst40us, 40e-6, clk_freq)

    shift_reg = [Signal(bool(0)) for k in range(40)]
    bit_counter = intbv(0, min=0, max=41)
    dat_sig = ConcatSignal(*shift_reg)

    @always(clk.posedge)
    def transmitting():
        if state == States.IDLE:
            if read_dev:
                bit_counter[:] = 0
                state.next = States.START_SIGNAL_LOW
                rst18ms.next = 1
                inout_state.next = WRITE_LINE
            else:
                inout_state.next = READ_LINE
        elif state == States.START_SIGNAL_LOW:
            if timeout18ms:
                state.next = States.START_SIGNAL_HIGH
                rst40us.next = 1
            else:
                rst18ms.next = 0
                line_out.next = 0
        elif state == States.START_SIGNAL_HIGH:
            if timeout40us:
                state.next = States.WAIT_RESPONSE_LOW
                inout_state.next = READ_LINE
            else:
                rst40us.next = 0
                line_out.next = 1
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
                state.next = States.WAIT_DAT_BIT
                rst40us.next = 1
        elif state == States.WAIT_DAT_BIT:
            if timeout40us:
                for k in range(39):
                    shift_reg[k].next = shift_reg[k+1]
                shift_reg[39].next = line_in
                bit_counter[:] = bit_counter + 1
                if bit_counter == 40:
                    valid.next = 1
                    dat.next = dat_sig
                    state.next = States.IDLE
                rst40us.next = 1
            else:
                rst40us.next = 0

    return instances()



def convert_block(target):
    dat = Signal(intbv(0)[40:])
    valid = Signal(bool(0))
    line_in = Signal(bool(0))
    line_out = Signal(bool(0))
    inout_state = Signal(bool(0))
    read_dev = Signal(bool(0))
    clk = Signal(bool(0))
    clk_freq = 100e6

    inst = DHT11(dat, valid, inout_state, line_in, line_out, read_dev, clk, clk_freq)
    inst.convert(hdl=target)



if __name__ == '__main__':
    convert_block(target='verilog')

