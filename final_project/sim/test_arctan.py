import cocotb
import os
import random
import sys
import logging
from pathlib import Path
from cocotb.utils import get_sim_time as gst
from cocotb.runner import get_runner
from cocotb_bus.bus import Bus
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import Monitor
from cocotb_bus.monitors import BusMonitor
from cocotb_bus.scoreboard import Scoreboard
import numpy as np
from cocotb.triggers import Timer, ClockCycles, RisingEdge, FallingEdge, ReadOnly,with_timeout, First, Join
from cocotb.clock import Clock

from cocotb.handle import SimHandleBase

def split_32bit_to_16bit(number):
    # Ensure the input is within the range of a 32-bit signed integer
    #print(number)
    # if not (-2**31 <= number < 2**31):
    #     raise ValueError("The number is out of the range for a 32-bit signed integer.")

    # Extract the lower 16 bits
    lower_16_bits = number & 0xFFFF
    # Extract the upper 16 bits by shifting right by 16 bits
    upper_16_bits = (number >> 16) & 0xFFFF

    # Convert to signed 16-bit integers if necessary
    if lower_16_bits >= 0x8000:
        lower_16_bits -= 0x10000
    if upper_16_bits >= 0x8000:
        upper_16_bits -= 0x10000

    return upper_16_bits, lower_16_bits
def to_fixed16(float_num, scale=2**16):
    # Convert float to 16-bit fixed point
    return (int(float_num * scale) & 0xFFFF)

def combine_to_32bit(angle16, radius16):
    # Combine two 16-bit numbers into one 32-bit number
    return (angle16 << 16) | ((radius16 >> 15) )
 
class SSSTester:
    """
    Checker of a split square sum instance
    Args
      dut_entity: handle to an instance of split-square-sum
    """
    def __init__(self, dut_entity: SimHandleBase, debug=False):
        self.dut = dut_entity
        self.log = logging.getLogger("cocotb.tb")
        self.log.setLevel(logging.DEBUG)
        self.input_mon = AXISMonitor(self.dut,'s00',self.dut.s00_axis_aclk, callback=self.model)
        self.output_mon = AXISMonitor(self.dut,'m00',self.dut.s00_axis_aclk)
        self.input_driver = AXISDriver(self.dut,'s00',self.dut.s00_axis_aclk)
        self._checker = None
        self.calcs_sent = 0
        # Create a scoreboard on the stream_out bus
        self.expected_output = [] #contains list of expected outputs (Growing)
        self.scoreboard = Scoreboard(self.dut, fail_immediately=False)
        self.scoreboard.add_interface(self.output_mon, self.expected_output)
 
    def stop(self) -> None:
        """Stops everything"""
        if self._checker is None:
            raise RuntimeError("Monitor never started")
        self.input_mon.stop()
        self.output_mon.stop()
        self.input_driver.stop()
 
    def model(self, transaction):
      #define a model here
      print("type: ",type(transaction))
      msb, lsb = split_32bit_to_16bit(transaction)
      print(msb,lsb)
      
      square_msb = msb*msb
      square_lsb = lsb*lsb
      square_sum = square_msb+square_lsb
      print("Square sum: ", square_sum)
      atan = np.arctan(msb/lsb)
      #print(hex(atan))
      print("atan: ", atan)
      new_atan = to_fixed16(atan)
      total = combine_to_32bit(new_atan,0)
      print(hex(new_atan))
      self.expected_output.append(new_atan)


class AXISMonitor(BusMonitor):
    """
    monitors axi streaming bus
    """
    transactions = 0
    def __init__(self, dut, name, clk, callback = None):
        self._signals = ['axis_tvalid','axis_tready','axis_tlast','axis_tdata','axis_tstrb']
        BusMonitor.__init__(self, dut, name, clk,callback=callback)
        self.clock = clk
        self.transactions = 0
        
    async def _monitor_recv(self):
        """
        Monitor receiver
        """
        rising_edge = RisingEdge(self.clock) # make these coroutines once and reuse
        falling_edge = FallingEdge(self.clock)
        read_only = ReadOnly() #This is
        while True:
            await rising_edge
            await falling_edge
            await read_only  #readonly (the postline)
            valid = self.bus.axis_tvalid.value
            ready = self.bus.axis_tready.value
            last = self.bus.axis_tlast.value
            data = self.bus.axis_tdata.value
            if valid and ready:
              self.transactions += 1
              thing = dict(data=data,last=last,name=self.name,count=self.transactions)
              print(thing)
              self._recv(data.integer)

class AXISDriver(BusDriver):
    def __init__(self, dut, name, clk):
        self._signals = ['axis_tvalid', 'axis_tready', 'axis_tlast', 'axis_tdata','axis_tstrb']
        BusDriver.__init__(self, dut, name, clk)
        self.clock = clk
        self.bus.axis_tdata.value = 0
        self.bus.axis_tstrb.value = 0
        self.bus.axis_tlast.value = 0
        self.bus.axis_tvalid.value = 0

    async def send_single(self,contents):
        

        await FallingEdge(self.clock)
        self.bus.axis_tdata.value = contents["data"]
        self.bus.axis_tstrb.value = contents["strb"]
        self.bus.axis_tlast.value = contents["last"]
        self.bus.axis_tvalid.value = 1

        await ReadOnly()
        while self.bus.axis_tready.value == 0:
                await RisingEdge(self.clock)
        await FallingEdge(self.clock)

        self.bus.axis_tvalid.value = 0

    async def send_burst(self,data_arr):
        # self.bus.axis_tvalid.value = 1
        for i,data in enumerate(data_arr):

            await FallingEdge(self.clock)
            self.bus.axis_tvalid.value = 1
            self.bus.axis_tdata.value = int(data)
            self.bus.axis_tlast.value = (i == len(data_arr)-1)
            self.bus.axis_tstrb.value = 0xF

            await ReadOnly()
            while self.bus.axis_tready.value == 0:
                await RisingEdge(self.clock)

        await FallingEdge(self.clock)
        self.bus.axis_tvalid.value = 0
        self.bus.axis_tlast.value = 0
        

    async def _driver_send(self, value, sync=True):
        #you finish
        fallngedge = await FallingEdge(self.clock)
        if value["type"] == "single":
            await self.send_single(value["contents"])
        elif value["type"] == "burst":
       
            await self.send_burst(value["contents"]["data"])

class SqrtScoreboard (Scoreboard):
  def compare(self, got, exp, log, strict_type=True):
    if abs(got-exp) <= 1: #change to whatever you want for the problem at hand.
      # Don't want to fail the test
      # if we're passed something without __len__
      try:
        log.debug("Received expected transaction %d bytes" %
                  (len(got)))
        log.debug(repr(got))
      except Exception:
        pass
    else:
      self.errors += 1
      # Try our best to print out something useful
      strgot, strexp = str(got), str(exp)
      log.error("Received transaction differed from expected output")
      log.info("Expected:\n" + repr(exp))
      log.info("Received:\n" + repr(got))
      if self._imm:
        assert False, (
          "Received transaction differed from expected "
          "transaction"
        )
  
    
async def set_ready(dut, ready_value):
    await FallingEdge(dut.s00_axis_aclk)
    dut.m00_axis_tready.value = ready_value
    #dut.m00_axis_tready.value = ready_value
    await FallingEdge(dut.s00_axis_aclk)

async def reset(clk,rst_in,wait_count,enable):
    rst_in.value = enable
    await ClockCycles(clk,wait_count)
    rst_in.value = ~enable

@cocotb.test()
async def test_arctan(dut):
    """cocotb test for square rooter"""
    tester = SSSTester(dut)
    cocotb.start_soon(Clock(dut.s00_axis_aclk, 10, units="ns").start())
    await set_ready(dut,1)
    await reset(dut.s00_axis_aclk, dut.s00_axis_aresetn,2,0)
    #feed the driver:
    s00_inputs = []
    for _ in range(16):
    # Generate non-zero values for both upper and lower 16 bits
        upper = random.randint(1000, 65535)  # Ensure significant upper bits
        lower = random.randint(1000, 65535)  # Ensure significant lower bits
        combined = (upper << 16) | lower
        s00_inputs.append(combined)
    print(s00_inputs)
    # for i in range(50):
    #   data = {'type':'single', "contents":{"data": random.randint(1,2**31),"last":0,"strb":15}}
    #   tester.input_driver.append(data)
    # data = {'type':'burst', "contents":{"data": np.array(20*[0]+[1]+30*[0]+[-2]+59*[0])}}
    data = {'type':'burst', "contents":{"data": np.array(s00_inputs)}}
    tester.input_driver.append(data)
    await ClockCycles(dut.s00_axis_aclk, 50)
    await set_ready(dut,0)
    await ClockCycles(dut.s00_axis_aclk, 300)
    await set_ready(dut,1)
    await ClockCycles(dut.s00_axis_aclk, 10)
    await set_ready(dut,0)
    await ClockCycles(dut.s00_axis_aclk, 10)
    await set_ready(dut,1)
    await ClockCycles(dut.s00_axis_aclk, 300)
    # access internal elements as needed (or do them inside of the class)
    assert tester.input_mon.transactions==tester.output_mon.transactions, f"Transaction Count doesn't match! :/"
    raise tester.scoreboard.result


def AXIS_runner():
    """Simulate the counter using the Python runner."""
    hdl_toplevel_lang = os.getenv("HDL_TOPLEVEL_LANG", "verilog")
    sim = os.getenv("SIM", "icarus")
    proj_path = Path(__file__).resolve().parent.parent
    sys.path.append(str(proj_path / "sim" / "model"))
    sources = [proj_path / "hdl" / "arctan.sv"] #grow/modify this as needed.
    build_test_args = ["-Wall"]#,"COCOTB_RESOLVE_X=ZEROS"]
    parameters = {}
    sys.path.append(str(proj_path / "sim"))
    runner = get_runner(sim)
    runner.build(
        sources=sources,
        hdl_toplevel="arctan",
        always=True,
        build_args=build_test_args,
        parameters=parameters,
        timescale = ('1ns','1ps'),
        waves=True
    )
    run_test_args = []
    runner.test(
        hdl_toplevel="arctan",
        test_module="test_arctan",
        test_args=run_test_args,
        waves=True
    )
 
if __name__ == "__main__":
    AXIS_runner()