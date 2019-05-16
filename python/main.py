#!/usr/bin/env python3
import os
import signal
from time import sleep

from ctypes.util import find_library
from ctypes import CDLL, c_int, c_long, c_char_p, c_void_p, cast, byref
from ctypes import addressof, sizeof, POINTER, Structure, create_string_buffer

#os.environ["LD_LIBRARY_PATH"] = "/home/agerstmayr/redhat/dev/bpftrace/build/src"
#libbpftrace = CDLL(find_library("bridge"))
libbpftrace = CDLL("src/libbpftracelib.so")

libbpftrace.bpftrace_init.argtypes = []
libbpftrace.bpftrace_init.restype = c_void_p

libbpftrace.bpftrace_run.argtypes = [c_void_p, c_char_p]
libbpftrace.bpftrace_run.restype = c_int

libbpftrace.bpftrace_data_cb.argtypes = [c_void_p]
libbpftrace.bpftrace_data_cb.restype = c_int


class BPFTrace():
    def __init__(self):
        self.bpftrace_ptr = libbpftrace.bpftrace_init()
        self.is_parent = True

    def run(self, script):
        pid = os.fork()
        if pid == 0: # child
            self.is_parent = False
            err = libbpftrace.bpftrace_run(self.bpftrace_ptr, script)
            if err:
                print("error starting bpftrace {}".format(err))
        else:
            self.pid = pid
            print("this inst has pid {}".format(self.pid))

    def data_cb(self):
        print('>>current ptr is {}, parent: {}'.format(self.bpftrace_ptr, self.is_parent))
        libbpftrace.bpftrace_data_cb(self.bpftrace_ptr)
        print('<<current ptr is {}, parent: {}'.format(self.bpftrace_ptr, self.is_parent))

    def stop(self):
        if not self.is_parent:
            return

        print("got stop cmd, my pid is {}".format(os.getpid()))
        print("send kill to {}".format(self.pid))
        os.kill(self.pid, signal.SIGINT)
        os.waitpid(self.pid, 0)
        print("child is gone")


tracer1 = BPFTrace()
tracer1.run(b"tracepoint:syscalls:sys_enter_read { @[probe] = count(); }")

#tracer2 = BPFTrace()
#tracer2.run(b"tracepoint:syscalls:sys_enter_read { @[probe] = count(); }")

sleep(5)
tracer1.data_cb()
sleep(5)
tracer1.data_cb()
sleep(5)
tracer1.stop()
#sleep(5)
#tracer2.data_cb()
#tracer2.stop()

print("stopped")
