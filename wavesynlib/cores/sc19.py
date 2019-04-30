# -*- coding: utf-8 -*-
"""
Created on Fri Apr  5 17:34:20 2019

@author: Feng-cong Li
"""



from myhdl import (
        Signal, intbv, modbv, 
        always, always_seq, always_comb,
        instances, instance, block, enum,
        delay)

from wavesynlib.cores.calcstack import STACK_OP, STACK_OP_WIDTH, CalcStack



OPCODE_WIDTH = 4

STOP     = 0b0000
PUSH_IMM = 0b0001
PUSH_DIR = 0b0010
PUSH_STP = 0b0011
STOR_IMM = 0b0100
STOR_STP = 0b0101
CALC     = 0b0110

UADD = 0

DATA_READ  = 0
DATA_WRITE = 1


@block
def SC19(
        ib_a,
        ib_d,
        db_a,
        db_rw,
        db_dr,
        db_dw,
        clk,
        POSEDGE = True
    ):
    '''\
Stack Calculator (started in 2019).
    '''
    IA_WIDTH = len(ib_a)  # Instruction address width
    IW_WIDTH = len(ib_d)  # Instruction word width
    DA_WIDTH = len(db_a)  # Data address width
    DW_WIDTH = len(db_dr) # Data word width    
    
    if POSEDGE:
        edge = clk.posedge
    else:
        edge = clk.negedge
        
    stack_out     = Signal(intbv(0)[8:])
    stack_in      = Signal(intbv(0)[8:])
    stack_full    = Signal(bool(0))
    stack_empty   = Signal(bool(0))
    stack_op      = Signal(STACK_OP.IDLE)
    stack_success = Signal(bool(0))
        
    stack = CalcStack(
        data_out=stack_out,
        data_in=stack_in,
        full=stack_full,
        empty=stack_empty,
        op=stack_op,
        op_success=stack_success,
        offset=0,
        clk=clk,
        posedge=POSEDGE,
        width=8,
        depth=4)
    
    STATUS = enum(
            'GET_INSTR', 
            'DECODE_INSTR',
            'GET_STACK_TOP',
            'DATA_STORE',
            'STOP')
    status = Signal(STATUS.GET_INSTR)
    
    # Program Counter
    pc = Signal(modbv(0)[IA_WIDTH:])
    # Instruction address register
    iar = Signal(modbv(0)[IA_WIDTH:])
    # Data address register
    dar = Signal(modbv(0)[DA_WIDTH:])
    # Data write register
    dwr = Signal(modbv(0)[DW_WIDTH:])
    # Data read register
    drr = Signal(modbv(0)[DW_WIDTH:])
    
    @always_comb
    def comb():
        #print('ib_a', ib_a)
        ib_a.next  = iar
        db_a.next  = dar
        db_dw.next = dwr
    
    @always(edge)
    def do():
        #print(pc)
        if status == STATUS.GET_INSTR:
            iar.next = pc
            pc.next = pc + 1
            db_rw.next = DATA_READ
            stack_op.next = STACK_OP.IDLE
            status.next = STATUS.DECODE_INSTR
        elif status == STATUS.DECODE_INSTR:
            opcode = ib_d[IW_WIDTH:(IW_WIDTH-OPCODE_WIDTH)]
            opdata = ib_d[(IW_WIDTH-OPCODE_WIDTH):]
            if opcode == STOP:
                pc.next = 0
                status.next = STATUS.STOP
            elif opcode == CALC:
                if opdata == UADD:
                    stack_op.next = STACK_OP.UADD
                else:
                    pass
                status.next = STATUS.GET_INSTR
            elif opcode == PUSH_IMM:
                stack_in.next = opdata
                stack_op.next = STACK_OP.PUSH
                status.next = STATUS.GET_INSTR
            elif opcode == STOR_IMM:
                dar.next = opdata                
                stack_op.next = STACK_OP.POP
                status.next = STATUS.GET_STACK_TOP
        elif status == STATUS.GET_STACK_TOP:
            status.next = STATUS.DATA_STORE
        elif status == STATUS.DATA_STORE:
            #print('In DATA_STORE', 'stack_out =', stack_out, 'stack_op =', stack_op)
            dwr.next = stack_out
            db_rw.next = DATA_WRITE
            status.next = STATUS.GET_INSTR
        elif status == STATUS.STOP:
            pass
        else:
            pass
            
    return instances()



def instr(opcode, opdata):
    return (opcode<<4) + opdata



test_program = (
        instr(PUSH_IMM, 7),
        instr(PUSH_IMM, 4), 
        instr(CALC, UADD),        
        instr(STOR_IMM, 3),        
        instr(STOP, 0),
        0,0,0,0,0,0,0,0,0,0,0
)

@block
def ProgramROM(
        data,
        addr):
    @always_comb
    def do():
        data.next = test_program[addr]
    return instances()



@block
def Testbench():
    ib_a = Signal(modbv(0)[4:])
    ib_d = Signal(modbv(0)[8:])
    db_a = Signal(modbv(0)[4:])
    db_rw = Signal(bool(0))
    db_dr = Signal(modbv(0)[8:])
    db_dw = Signal(modbv(0)[8:])
    clk = Signal(bool(0))
    
    prom = ProgramROM(data=ib_d, addr=ib_a)
    sc19 = SC19(ib_a, ib_d, db_a, db_rw, db_dr, db_dw, clk)
    
    @instance
    def do():
        print('ib_a', 'ib_d', 'db_a', 'db_rw', 'db_dw', sep='\t')
        for k in range(12):
            yield delay(10)
            clk.next = 1
            yield delay(10)
            clk.next = 0
            print(ib_a, ib_d, db_a, bool(db_rw), db_dw, sep='\t')
    
    return instances()



def test():
    inst = Testbench()
    inst.run_sim()
    



def to_verilog():
    ib_a = Signal(modbv(0)[4:])
    ib_d = Signal(modbv(0)[8:])
    db_a = Signal(modbv(0)[4:])
    db_rw = Signal(bool(0))
    db_dr = Signal(modbv(0)[8:])
    db_dw = Signal(modbv(0)[8:])
    clk = Signal(bool(0))
    
    sc19 = SC19(ib_a, ib_d, db_a, db_rw, db_dr, db_dw, clk)
    sc19.convert(hdl='verilog')
    
    
    
if __name__ == '__main__':
    to_verilog()
    # test()
    
