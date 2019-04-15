from argparse import ArgumentParser
from pathlib import Path 

from myhdl import (
    block, Signal, enum, intbv,
    ConcatSignal,
    always_seq, always_comb, always, instances)

from wavesynlib.cores.delayer import Delayer, DualDelayer



READ_LINE = 0
WRITE_LINE = 1



@block
def PyDHT11(
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

    state = Signal(States.IDLE)

    if state_out is not None:
        @always_comb
        def set_state_out():
            state_out.next = state
    
    timeout_20ms = Signal(bool(0))
    timeout_40us = Signal(bool(0))
    delayer_rst = Signal(bool(0))
    
    read_dev_tap = [Signal(bool(0)), Signal(bool(0))]
    read_dev_posedge = Signal(bool(0))
    
    @always_comb
    def read_dev_posedge_detector():
        read_dev_posedge.next = read_dev_tap[0] & (~read_dev_tap[1])
        
    @always(clk.posedge)
    def connect_read_dev_tap():
        read_dev_tap[0].next = read_dev
        read_dev_tap[1].next = read_dev_tap[0]        

    delayer = DualDelayer(
        timeout_short=timeout_40us, 
        timeout_long=timeout_20ms,
        clk=clk,
        rst=delayer_rst,
        interval_short=40e-6,
        interval_long=20e-3,
        clk_freq=clk_freq)


    shift_reg = [Signal(bool(0)) for k in range(40)]
    bit_counter = Signal(intbv(0, min=0, max=41))
    shift_reg_sig = ConcatSignal(*shift_reg)

    @always(clk.posedge)
    def transmitting():        
        if reset:
            state.next = States.IDLE
        elif state == States.IDLE:
            if not read_dev_posedge:
                inout_state.next = READ_LINE
            else:
                bit_counter.next = 0
                delayer_rst.next = 1
                inout_state.next = WRITE_LINE
                valid.next = 0
                state.next = States.START_SIGNAL_LOW
        elif state == States.START_SIGNAL_LOW:
            if not timeout_20ms:
                delayer_rst.next = 0
                line_out.next = 0
            else:
                delayer_rst.next = 1
                inout_state.next = READ_LINE
                state.next = States.START_SIGNAL_HIGH
        elif state == States.START_SIGNAL_HIGH:
            if not timeout_40us:
                delayer_rst.next = 0
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
                delayer_rst.next = 1
                state.next = States.WAIT_BIT_DAT
        elif state == States.WAIT_BIT_DAT:
            if not timeout_40us:
                delayer_rst.next = 0
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
            dat.next = shift_reg_sig
            state.next = States.IDLE
        else:
            state.next = States.IDLE

    return instances()



DHT11_VERILOG_CODE = f'''\
`include "PyDHT11.v"


module DHT11(
    output [7:0] humidity0,
    output [7:0] humidity1,
    output [7:0] temperature0,
    output [7:0] temperature1,
    output [7:0] checksum,
    output valid,
    output [3:0] state,
    inout dat_line,
    input read,
    input reset,
    input clk);

    `define READ_LINE {READ_LINE}
    `define WRITE_LINE {WRITE_LINE}

    wire line_in;
    wire line_out;
    wire inout_state;

    // IN-OUT control.
    assign dat_line = inout_state==`READ_LINE ? 1'bz : line_out;
    assign line_in  = inout_state==`READ_LINE ? dat_line : 1'bz;

    PyDHT11 pydht11(
        .dat({{humidity0, humidity1, temperature0, temperature1, checksum}}), 
        .valid(valid),
        .inout_state(inout_state),
        .line_out(line_out),
        .line_in(line_in),
        .read_dev(read),
        .clk(clk),
        .reset(reset),
        .state_out(state));
endmodule
'''




def to_verilog(clk_freq):
    dat = Signal(intbv(0)[40:])
    valid = Signal(bool(0))
    line_in = Signal(bool(0))
    line_out = Signal(bool(0))
    inout_state = Signal(bool(0))
    read_dev = Signal(bool(0))
    clk = Signal(bool(0))
    reset = Signal(bool(0))
    state = Signal(intbv(0)[4:])

    inst = PyDHT11(
        dat, 
        valid, 
        inout_state, 
        line_out, 
        line_in, 
        read_dev, 
        clk, 
        reset, 
        clk_freq, 
        state)
    inst.convert(hdl="verilog")



if __name__ == '__main__':
    parser = ArgumentParser(description='''\
Generate two modules for reading the DHT11 sensor.
    ''')
    parser.add_argument(
        '--clk-freq',
        help='Input clock frequency (Hz).',
        type=float)

    args = parser.parse_args()

    to_verilog(clk_freq=args.clk_freq)
    vpath = Path(__file__).parent / "dht11.v"
    with open(vpath, 'w') as vfile:
        vfile.write(DHT11_VERILOG_CODE)


