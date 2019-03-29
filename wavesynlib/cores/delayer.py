from myhdl import block, Signal, always, always_seq, intbv, instances



@block
def Delayer(
        timeout,    # Output
        clk,        # Clock
        rst,        # Reset
        interval,   # Parameter
        clk_freq    # Parameter (Hz)
    ):
    COUNTER_MAX = int(interval * clk_freq)

    counter = Signal(intbv(0, min=0, max=COUNTER_MAX+1))
    
    @always(clk.posedge, rst.posedge)
    def do():
        if rst:
            counter[:] = 0
            timeout.next = 0
        else:
            if counter >= COUNTER_MAX-1:
                timeout.next = 1
            else:
                timeout.next = 0
                counter.next = counter + 1

    return instances()




