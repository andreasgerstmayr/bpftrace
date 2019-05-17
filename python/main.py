#!/usr/bin/env python3
from time import sleep
from bpftrace import BPFTrace

tracer1 = BPFTrace(b"tracepoint:syscalls:sys_enter_read { @[probe] = count(); }")
tracer1.start()

sleep(2)

tracer2 = BPFTrace(b"""
tracepoint:syscalls:sys_enter_read
{
  @start[tid] = nsecs;
}

tracepoint:syscalls:sys_exit_read / @start[tid] /
{
  @times = hist(nsecs - @start[tid]);
  delete(@start[tid]);
}
""")
tracer2.start()

sleep(5)
tracer1.data_cb()
tracer2.data_cb()



tracer1.stop()
tracer2.stop()

print("all stopped")
