from myhdl import (
    block, Signal, intbv, always, always_comb, instances)

from wavesynlib.cores.sevensegdecoder import Decoder
from wavesynlib.cores.bcd import UByteToBCD



@block
def Display100(
        seg_out, # 7 bit
        sel_out, # 1 bit
        dat_in, # 8 bit
        clk,
        clk_freq, # Parameter, Hz
        common_anode=True
    ):
    T_clk = 1 / clk_freq

    # Switch after every 2 ms. 
    SWITCH_COUNT = int(2e-3 / T_clk)
    counter = Signal(intbv(0, min=0, max=SWITCH_COUNT+1))

    digit = Signal(intbv(0)[4:])
    decoder7seg = Decoder(seg=seg_out, num=digit, common_anode=common_anode)

    all_digits = Signal(intbv(0)[10:])
    ubyte2bcd = UByteToBCD(bcd=all_digits, binary=dat_in)

    sel = Signal(bool(0))

    @always(clk.posedge)
    def count():
        if counter >= SWITCH_COUNT-1:
            sel.next = not sel
            counter.next = 0
        else:
            counter.next = counter + 1

    @always_comb
    def choose():
        if sel:
            digit.next = all_digits[8:4]
        else:
            digit.next = all_digits[4:0]
        sel_out.next = sel
    
    return instances()



def convert_display100(clk_freq, target):
    seg_out = Signal(intbv(0)[7:])
    sel_out = Signal(bool(0))
    dat_in  = Signal(intbv(0)[8:])
    clk     = Signal(bool(0))
    inst = Display100(
        seg_out=seg_out, 
        sel_out=sel_out, 
        dat_in=dat_in, 
        clk=clk, 
        clk_freq=clk_freq,
        common_anode=True)
    inst.convert(hdl=target)



import sys

if __name__ == '__main__':
    clk_freq = float(sys.argv[1])
    lang = sys.argv[2]
    convert_display100(clk_freq, lang)

