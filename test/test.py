# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
import random
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge

WIDTH = 24


@cocotb.test()
async def test_cla(dut):
    global WIDTH
    dut._log.info("Start CLA test")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    await ClockCycles(dut.clk, 1)
    dut.ena.value = 1

    for j in range(1000):
        dut.ui_in.value = 0
        dut.uio_in.value = 0  # Selecting cla
        dut._log.info("Reset")
        dut.rst_n.value = 0  # Reset
        await ClockCycles(dut.clk, 1)
        dut.rst_n.value = 1  # Normal operation

        a = []
        b = []
        for i in range(0, WIDTH, 8):
            a.append(random.randint(0, 255))
            b.append(random.randint(0, 255))

        # A
        for i in range(len(a)):
            dut.ui_in.value = a[i]
            await ClockCycles(dut.clk, 1)

        # B
        for i in range(len(b)):
            dut.ui_in.value = b[i]
            await ClockCycles(dut.clk, 1)

        await ClockCycles(dut.clk, 6)  # Waiting
        dut.uio_in.value = 0b00000111  # start_calc
        await ClockCycles(dut.clk, 10) # Waiting
        dut.uio_in.value = 0b00001111  # output_result

        # Reading
        await ClockCycles(dut.clk, 2)
        z = []
        for i in range(len(a)):
            z.append(dut.uo_out.value)
            await ClockCycles(dut.clk, 1)

        a_op = logic_vector2int(a)
        b_op = logic_vector2int(b)
        overflow = dut.uio_out[7].value
        result = logic_vector2int([overflow] + z)

        dut._log.info(f"CLA test {j} with a = {a_op}, b = {b_op} yielded z = {result}. Should be {a_op + b_op}")
        assert result == a_op + b_op

@cocotb.test()
async def test_rca(dut):
    global WIDTH
    dut._log.info("Start RCA test")


    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    await ClockCycles(dut.clk, 1)
    dut.ena.value = 1

    for j in range(1000):
        dut.ui_in.value = 0
        dut.uio_in.value = 1  # Selecting rca
        dut._log.info("Reset")
        dut.rst_n.value = 0  # Reset
        await ClockCycles(dut.clk, 1)
        dut.rst_n.value = 1  # Normal operation

        a = []
        b = []
        for i in range(0, WIDTH, 8):
            a.append(random.randint(0, 255))
            b.append(random.randint(0, 255))

        # A
        for i in range(len(a)):
            dut.ui_in.value = a[i]
            await ClockCycles(dut.clk, 1)

        # B
        for i in range(len(b)):
            dut.ui_in.value = b[i]
            await ClockCycles(dut.clk, 1)

        await ClockCycles(dut.clk, 6)  # Waiting
        dut.uio_in.value = 0b00000110  # start_calc
        await ClockCycles(dut.clk, 10) # Waiting
        dut.uio_in.value = 0b00001110  # output_result

        # Reading
        await ClockCycles(dut.clk, 2)
        z = []
        for i in range(len(a)):
            z.append(dut.uo_out.value)
            await ClockCycles(dut.clk, 1)

        a_op = logic_vector2int(a)
        b_op = logic_vector2int(b)
        overflow = dut.uio_out[6].value
        result = logic_vector2int([overflow] + z)

        dut._log.info(f"RCA test {j} with a = {a_op}, b = {b_op} yielded z = {result}. Should be {a_op + b_op}")
        assert result == a_op + b_op


def logic_vector2int(vec: []) -> int:
    result = 0
    for byte in vec:
        result = result << 8
        result = result | byte

    return result
