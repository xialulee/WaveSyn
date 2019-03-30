from myhdl import block, Signal, always, always_seq, intbv, instances



@block
def Delayer(
        timeout,    # Output
        clk,        # Clock
        rst,        # Reset
        interval,   # Parameter (Seconds)
        clk_freq    # Parameter (Hz)
    ):
    COUNTER_MAX = int(interval * clk_freq)

    counter = Signal(intbv(0, min=0, max=COUNTER_MAX+1))
    
    @always(clk.posedge, rst.posedge)
    def do():
        if rst:
            counter.next = 0
            timeout.next = 0
        else:
            if counter >= COUNTER_MAX:
                timeout.next = 1
            else:
                timeout.next = 0
                counter.next = counter + 1

    return instances()



@block
def DualDelayer(
        timeout_short,
        timeout_long,
        clk,
        rst,
        interval_short, # Parameter (Seconds)
        interval_long,  # Parameter (Seconds)
        clk_freq, # Parameter (Hz)
    ):
    COUNTER_LONG_MAX  = int(interval_long  * clk_freq)
    COUNTER_SHORT_MAX = int(interval_short * clk_freq) 

    counter = Signal(intbv(0, min=0, max=COUNTER_LONG_MAX+1))

    @always(clk.posedge, rst.posedge)
    def do():
        if rst:
            counter.next = 0
            timeout_short.next = 0
            timeout_long.next = 0
        else:
            if counter >= COUNTER_SHORT_MAX:
                timeout_short.next = 1
            else:
                timeout_short.next = 0
            if counter >= COUNTER_LONG_MAX:
                timeout_long.next = 1
            else:
                timeout_long.next = 0
                counter.next = counter + 1

    return instances()

